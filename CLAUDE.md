# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

연세대 DAS6035 *AI에이전트설계및응용* 중간 해커톤 제출물. 연구 주제 하나를 입력받아
**주제 이해 → 조사 계획 → 문헌 탐색 → 평가 → 종합 → Research Gap 제안** 6단계를 수행해
연구 착수용 브리프(Research Brief)를 만드는 에이전트. 제출 기한 2026-11-02.

- 설계 문서는 코드보다 상위에 있다. 설계 변경 전 반드시 읽을 것:
  - `goals.md` — 목표 O1~O7, 성공 기준, non-goal. **수정하지 않는다.**
  - `plan.md` — 아키텍처, ADR-1~5, 주차별 작업 분해(W1~W4), 테스트 주제·지표·ablation 설계.
    설계가 바뀌면 §4 ADR에 결정을 추가하고 §8 변경 로그에 날짜·이유를 기록한다.
- 코드는 전부 `research_agent/` 아래. 문서는 한국어, 코드 주석도 한국어.

## 명령어 (`research_agent/` 에서 실행)

```bash
uv sync                                  # 의존성 설치 (Python 3.12, uv.lock 고정)
cp .env.example .env                     # ANTHROPIC_API_KEY 입력 (키는 이것 하나만)

uv run pytest                            # 단위 테스트 전체 — 네트워크·API 키 불필요 (HTTP·LLM 모킹)
uv run pytest tests/test_llm.py          # 파일 하나
uv run pytest tests/test_llm.py::test_retry_then_ok   # 테스트 하나

uv run python scripts/smoke_tools.py     # OpenAlex·arXiv·Crossref 실제 호출 확인
uv run python scripts/smoke_llm.py       # Anthropic 구조화 출력 실제 호출 확인 (비용 발생)

uv run agent run --topic "<주제>"                # 베이스라인 ReAct 실행 (기본 mode=baseline)
uv run agent run --topic "<주제>" --mode graph   # 최종 그래프 구조 (W2 구현 예정)
uv run agent run --topic "<주제>" --no-cache     # 도구 캐시 끄고 live 검색
uv run agent run --topic "<주제>" --model <id>   # 이번 실행만 모델 덮어쓰기
uv run agent models                              # 계정에서 쓸 수 있는 Claude 모델명 목록
uv run agent schema                              # ResearchBrief JSON Schema → schemas/brief.json
```

린터·포매터는 설정되어 있지 않다. 실행 결과는 `runs/<UTC타임스탬프>_<mode>_<topic-slug>/` 에
`events.jsonl`, `cost.json`, `brief.json`, `report.md`, `papers.json` 으로 남는다 (`runs/` 는 gitignore).

## 아키텍처

### 데이터 흐름과 불변 원칙

모든 노드는 자유 텍스트가 아니라 `schemas.py` 의 Pydantic 타입만 주고받는다
(TopicFrame → ResearchPlan → Paper/EvidenceTable → Synthesis → GapList → ResearchBrief).
`RunState` 하나가 노드 간 공유 상태다. 각 스키마의 `check()` 는 LLM 없이 돌아가는
**결정적 자체 검증**이며 Critic 의 1차 게이트 역할을 한다. Pydantic `Field(description=...)` 은
그대로 JSON Schema 로 LLM 에 전달되므로 지시문처럼 작성한다.

핵심 설계 철학(goals.md O7): 품질을 모델의 똑똑함에 맡기지 않고 **파이프라인 구조가 보장**한다.
실행마다 문장·선택 문헌은 달라져도 리포트 섹션 구조·필드 채움·인용 검증률(100%)은 달라지면 안 된다.

### 레이어

| 모듈 | 역할 | 주의 |
|---|---|---|
| `llm.py` | **프로젝트의 유일한 LLM 호출 지점** (ADR-2). `call()` 은 SDK `messages.parse(output_format=PydanticModel)` 로 구조화 출력, 검증 실패 시 오류를 되먹여 `max_retries` 회 재시도. `call_with_tools()` 는 ReAct 한 턴 | 다른 곳에서 `anthropic` 클라이언트를 직접 만들지 않는다. 모든 호출은 `RunLogger` 에 토큰·비용 기록, 상한 초과 시 `CostLimitExceeded`/`TimeLimitExceeded` |
| `config.py` | `config/models.yaml` + `.env` → `Settings`. `load_prompt(name)` 으로 `prompts/<name>.md` 로딩 | **프롬프트 문자열을 코드에 두지 않는다.** 모델명·단가·상한은 yaml 에서만 바꾼다. SDK 가 `temperature` 를 받지 않아 config 에 없음. 개발 중 기본 모델은 `claude-haiku-4-5`(비용 절감), 품질 측정·제출은 `claude-sonnet-5-5`, judge 는 `claude-opus-5-5` |
| `tools/` | OpenAlex(기본, 전 분야), arXiv(CS 보강), Crossref(DOI 실존 검증). `tools/__init__.py` 의 `Tools` 가 캐시·로깅·중복 제거(`papers` 레지스트리)를 붙이고, `TOOL_DEFS` 가 LLM 에 노출할 tool 정의 | **키 필요 API 추가 금지** (ADR-3). `Paper` 는 도구 출력 그대로이며 LLM 이 만들지 않는다. DOI 없는 OpenAlex 문헌은 검증 불가라 버린다. `Paper.id` 는 소문자 DOI 또는 `arxiv:<id>` 로 정규화 |
| `tools/cache.py` | diskcache, 키 = 도구명 + 정규화 인자. ablation 공정성용(같은 검색 스냅샷 위에서 구조만 비교) | live 재현은 `--no-cache` |
| `runlog.py` | `runs/` 에 JSONL 이벤트·비용·산출물 기록. 외부 서비스 없음 | Planning/Reflection/Replanning 이 실제로 일어났음을 보여주는 설계평가 증거이므로 단계 전이는 꼭 `event()` 로 남긴다 |
| `baseline.py` | 단일 ReAct 루프 (ablation 조건 A). 마지막 step 에 `tool_choice` 로 `submit_brief` 강제. 사후 결정적 검사는 하되 **재시도하지 않고 그대로 기록** — 베이스라인의 약점을 측정하는 것이 목적 | `render_markdown()` 이 리포트 7개 섹션을 만든다 |
| `nodes/` (비어 있음) | W2 에서 understand / plan / search / evaluate / synthesize / critic / gap / write 노드 구현 예정. `graph.py` 러너는 **프레임워크 없이 직접 구현** (ADR-1, LangGraph 사용 안 함) | 노드 입출력·결정적 검증 기준은 plan.md §3.2, Critic 6종 검사는 §3.3. Replan 상한 2회, 상한 도달 시 미달 항목을 리포트 "한계" 에 자동 기재하고 **실패로 죽지 않는다** |

### 테스트 방식

- LLM 은 `messages.parse` 를 흉내 내는 `FakeMessages` 로, HTTP 는 `httpx.MockTransport` 로 모킹. 실제 네트워크 테스트는 `scripts/smoke_*.py` 로만.
- `RunLogger(..., runs_dir=tmp_path)` 로 테스트 중 `runs/` 오염을 막는다.
- 테스트 주제 5개는 `eval/topics.yaml` (T1~T5, 분야 분산, 한·영 혼합). 특정 주제에 맞춘 프롬프트 튜닝은 금지 — 실제 평가 주제는 다를 수 있다.

## 작업 시 지킬 것

- 재현성 L1: 평가자(교수님)가 README 의 명령 3개와 Anthropic 키 하나로 실행한다. 의존성 추가 시 `uv.lock` 갱신, 새 환경변수는 `.env.example` 에 반영.
- 현재 진행 상태와 다음 할 일은 `plan.md` §5 작업 분해와 §8 변경 로그를 기준으로 판단한다.
- 커밋 메시지는 영어, Conventional Commits.
