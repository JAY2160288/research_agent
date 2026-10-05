# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

연세대 DAS6035 *AI에이전트설계및응용* 중간 해커톤 제출물. 연구 주제 하나를 입력받아
**주제 이해 → 조사 계획 → 문헌 탐색 → 평가 → 종합 → Research Gap 제안** 6단계를 수행해
연구 착수용 브리프(Research Brief)를 만드는 에이전트. 제출 기한 2026-11-02.

- 설계 문서는 코드보다 상위에 있다. 설계 변경 전 반드시 읽을 것:
  - `goals.md` — 목표 O1~O7, 성공 기준, non-goal. **수정하지 않는다.**
  - `plan.md` — 아키텍처, ADR-1~6, 주차별 작업 분해(W1~W4), 테스트 주제·지표·ablation 설계.
    설계가 바뀌면 §4 ADR에 결정을 추가하고 §8 변경 로그에 날짜·이유를 기록한다.
    §3.1 디렉터리 트리는 초안 기준이라 실제와 조금 다를 수 있다 (`logging.py` → 실제는 `runlog.py`,
    LLM-judge 는 `eval/judge.py` 가 아니라 `src/research_agent/judge.py`). 파일 위치는 코드를 기준으로 판단한다.
- 코드는 전부 `research_agent/` 아래. 문서는 한국어, 코드 주석도 한국어.
- 진행 상태: W1~W3 + W4 Day 2 완료 (2026-10-05, ablation 1차 T1·T2 × B/C/D sonnet). 다음은 W4 Day 3 (plan.md §5 W4 일별 계획) — `uv run python scripts/run_ablation.py --topics T3,T4 --conditions D,B,C --model claude-sonnet-5-5 --judge --wait`, Day 4 T5 + A×5, 10/08 클린룸 재현 + config `model` 을 sonnet 으로 교체. OpenAlex 는 00:00 UTC(09:00 KST) 리셋, 러너가 헤더로 잔량을 확인하고 `--wait` 면 리셋까지 기다린다.

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
uv run agent run --topic "<주제>" --mode graph   # 최종 구조: 역할 분리 그래프 + Critic/Replan 루프
uv run agent run --topic "<주제>" --mode graph --until plan   # 그 노드까지만 실행 (개발용, 중간 산출물은 *.json)
uv run agent run --topic "<주제>" --mode graph --critic deterministic --max-replans 0   # 품질 게이트 축소 (ablation B/C)
uv run agent run --topic "<주제>" --no-cache     # 도구 캐시 끄고 live 검색
uv run agent run --topic "<주제>" --model <id>   # 이번 실행만 모델 덮어쓰기
uv run agent run --topic "<주제>" --mode graph --plan-from runs/<D 실행 폴더>   # 그 실행의 topic_frame·plan 재사용 (ablation 공정성, ADR-9)
uv run agent judge runs/<실행 폴더> | --all [--mode graph] [--force]   # LLM-judge J1~J7 → 그 폴더에 judge.json (judge_model=opus, 회당 ~$0.2)
uv run agent models                              # 계정에서 쓸 수 있는 Claude 모델명 목록
uv run agent schema                              # ResearchBrief JSON Schema → schemas/brief.json

uv run python scripts/summarize_runs.py [--mode graph] [--md]   # runs/ 전체 cost.json → 결정적 지표 표 (--md 는 design.md 용)
uv run python scripts/summarize_runs.py --ablation [--md]        # 주제 × 조건(A~D) 매트릭스 + 조건별 평균 (ablation.json·judge.json 반영)
uv run python scripts/run_ablation.py --topics T1,T2 --conditions D,B,C,A [--model claude-sonnet-5-5] [--judge] [--dry-run]   # ablation 러너. D→B→C→A, B/C 는 D 의 계획 재사용, OpenAlex 예산 가드
```

실제 실행 비용 감각 (Haiku, 2026-10-04): 베이스라인 주제당 $0.08~0.15, 그래프 Replan 없이 $0.11~0.13 · 11~13회 · 4~8분, Replan 2회까지 돌면 $0.25~0.30 · 20~25회 · 7~8분.
시간 상한 10분이 비용 상한보다 먼저 온다. 폭주 출력(잘린 JSON 재시도 3분×2)이나 arXiv 429 대기가 주범 — 노드 출력은 `llm.node_max_tokens` 로, arXiv 는 circuit breaker 로 막고 `notes` 에 남긴다.

린터·포매터는 설정되어 있지 않다. 실행 결과는 `runs/<UTC타임스탬프>_<mode>_<topic-slug>/` 에
`events.jsonl`, `cost.json`, `brief.json`, `report.md`, `papers.json` 으로 남는다 (`runs/` 는 gitignore).

## 아키텍처

### 데이터 흐름과 불변 원칙

모든 노드는 자유 텍스트가 아니라 `schemas.py` 의 Pydantic 타입만 주고받는다
(TopicFrame → ResearchPlan → Paper/EvidenceTable → Synthesis → GapList → ResearchBrief).
`RunState` 하나가 노드 간 공유 상태다. 각 스키마의 `check()` 는 LLM 없이 돌아가는
**결정적 자체 검증**이며 Critic 의 1차 게이트 역할을 한다. Pydantic `Field(description=...)` 은
그대로 JSON Schema 로 LLM 에 전달되므로 지시문처럼 작성한다.

**스키마에 `max_length`·`ge/le` 같은 제약을 넣을 때 주의**: SDK `messages.parse` 가 응답을 pydantic 으로 검증하다 실패하면
`ValidationError` 를 SDK 안에서 던지고 응답 본문·usage 를 잃는다. `llm.call` 이 이를 잡아 되먹여 재시도하긴 하지만(비용은 0 으로
기록됨) 한 호출이 통째로 낭비되므로, "상한을 넘으면 잘라 쓰면 되는" 종류의 제약(쿼리 개수 등)은 스키마가 아니라 노드 코드에서 자른다.
`min_length` 처럼 LLM 이 반드시 지켜야 하는 것만 스키마에 둔다 (2026-10-04 `ReplanPlan.queries` 사례).

핵심 설계 철학(goals.md O7): 품질을 모델의 똑똑함에 맡기지 않고 **파이프라인 구조가 보장**한다.
실행마다 문장·선택 문헌은 달라져도 리포트 섹션 구조·필드 채움·인용 검증률(100%)은 달라지면 안 된다.

### 레이어

| 모듈 | 역할 | 주의 |
|---|---|---|
| `llm.py` | **프로젝트의 유일한 LLM 호출 지점** (ADR-2). `call()` 은 SDK `messages.parse(output_format=PydanticModel)` 로 구조화 출력, 검증 실패 시 오류를 되먹여 `max_retries` 회 재시도. `call_with_tools()` 는 ReAct 한 턴 | 다른 곳에서 `anthropic` 클라이언트를 직접 만들지 않는다. 모든 호출은 `RunLogger` 에 토큰·비용 기록, 상한 초과 시 `CostLimitExceeded`/`TimeLimitExceeded` |
| `config.py` | `config/models.yaml` + `.env` → `Settings`. `load_prompt(name)` 으로 `prompts/<name>.md` 로딩. `.env` 는 `ANTHROPIC_API_KEY` 와 선택 `CONTACT_EMAIL`(OpenAlex polite pool 용, 키 아님) | **프롬프트 문자열을 코드에 두지 않는다.** 모델명·단가·상한은 yaml 에서만 바꾼다. SDK 가 `temperature` 를 받지 않아 config 에 없음. 개발 중 기본 모델은 `claude-haiku-4-5`(비용 절감), 품질 측정·제출은 `claude-sonnet-5-5`, judge 는 `claude-opus-5-5`. **제출 전 `model` 을 sonnet 으로 바꾸는 것이 W4 체크리스트(4.4)** |
| `tools/` | OpenAlex(기본, 전 분야), arXiv(CS 보강), Crossref(DOI 실존 검증 + **OpenAlex 실패 시 폴백 검색**, ADR-8). `tools/__init__.py` 의 `Tools` 가 캐시·로깅·중복 제거(`papers` 레지스트리)를 붙이고, `TOOL_DEFS` 가 LLM 에 노출할 tool 정의(베이스라인용, Crossref 검색은 미노출) | **키 필요 API 추가 금지** (ADR-3). `Paper` 는 도구 출력 그대로이며 LLM 이 만들지 않는다. DOI 없는 OpenAlex 문헌은 검증 불가라 버린다. `Paper.id` 는 소문자 DOI 또는 `arxiv:<id>` 로 정규화. **OpenAlex 는 IP 당 하루 약 100회 검색**(1000 크레딧/검색당 10, 소진 시 429 + retry-after 12h) — 그래프 1회가 약 30회를 쓰므로 반복 실행·ablation 은 하루 3회 안팎에서 막힌다. 실험 설계 시 이 예산을 먼저 계산할 것 |
| `tools/cache.py` | diskcache, 키 = 도구명 + 정규화 인자. ablation 공정성용(같은 검색 스냅샷 위에서 구조만 비교) | live 재현은 `--no-cache` |
| `runlog.py` | `runs/` 에 JSONL 이벤트·비용·산출물 기록. 외부 서비스 없음. `RunLogger(into=<기존 폴더>, prefix="judge_")` 는 끝난 실행 폴더에 덧붙여 쓰는 모드(judge 용) | Planning/Reflection/Replanning 이 실제로 일어났음을 보여주는 설계평가 증거이므로 단계 전이는 꼭 `event()` 로 남긴다 |
| `judge.py` | LLM-judge (W4-4.2, `eval/rubric.md` §B). 완주한 실행의 `report.md` + `cost.json` checks 를 `judge_model` 에 주고 `JudgeResult`(J1~J7, 인용 verbatim) 를 받는다. `consistency_flags` 가 결정적 지표와 모순되는 점수를 **표시만** 한다. 결과 `judge.json`·`judge_events.jsonl` 은 실행 폴더에, 원 `cost.json` 은 건드리지 않는다 | 파이프라인 밖 사후 작업 — 실행 중 품질은 Critic 이 보장. 프롬프트는 `prompts/judge.md`. 점수 범위는 스키마 `ge/le` 가 아니라 `check()` 로 (SDK parse 실패 방지) |
| `baseline.py` | 단일 ReAct 루프 (ablation 조건 A). 마지막 step 에 `tool_choice` 로 `submit_brief` 강제. 사후 결정적 검사는 하되 **재시도하지 않고 그대로 기록** — 베이스라인의 약점을 측정하는 것이 목적 | `render_markdown()` 이 리포트 7개 섹션을 만든다 |
| `nodes/` | 노드 = `run(state: RunState, ctx: NodeContext) -> None`. `nodes/__init__.py` 의 `checked_call` 이 공통 루프(구조화 호출 → 스키마 `check()` → 실패 시 이슈 되먹여 재호출). 9개 구현: understand, plan, search(LLM 없음, OpenAlex 주력 + arXiv 보강·circuit breaker, ADR-6; `extra_queries` 로 재검색), evaluate(sub-RQ 당 `evaluate_per_subrq` 편 선별 → `evaluate_batch` 편씩 LLM; 재검색 라운드엔 `only_sub_rqs` 의 새 후보만 **증분** 평가), synthesize·gap(Replan 라운드엔 직전 Critique 를 프롬프트에 붙임), critic(결정적 5종 → 통과 시에만 LLM 비판, major 이슈면 미통과, ADR-7), replan(걸린 sub-RQ 의 새 쿼리 1~3개, 계획에 덧붙임), write(구조 섹션은 상태에서 조립, LLM 은 한국어 요약·한계만) | 노드 입출력·결정적 검증 기준은 plan.md §3.2, Critic 검사는 §3.3. 검사 미해결은 `state.notes` 에 적고 계속 진행 — **실패로 죽지 않는다**. Critic 미달 노트는 **루프 종료 후 최종 라운드 기준으로 graph 가** 남긴다(중간 라운드에서 풀린 항목이 한계에 남지 않게). notes 는 write 에서 리포트 §7 한계에 `[auto]` 로 자동 편입. 각 노드 프롬프트는 `prompts/<role>.md`. 비용 손잡이는 `config/models.yaml` 의 `tools.evaluate_per_subrq` 와 `graph.max_replans` |
| `report.py` | `render_markdown`·`post_checks` — 베이스라인과 그래프가 같은 렌더러·지표를 쓴다 (ablation 공정성). `post_checks` 결과가 `cost.json` 의 `checks` 에 들어가고 `scripts/summarize_runs.py` 가 이를 표로 모은다 | 지표 정의를 바꾸면 양쪽에 동시에 반영됨. 지표 이름(`citation_verified_rate` 등)을 바꾸면 summarize_runs 의 컬럼도 함께 수정 |
| `graph.py` | understand → plan → [search → evaluate → synthesize → gap → critic] → write 러너. Critic 미달이면 replan 후 루프 선두로(상한 `graph.max_replans`). **프레임워크 없이 직접 구현** (ADR-1, LangGraph 사용 안 함). `--until <node>` 로 부분 실행. `plan_from=<실행 폴더>` 면 그 실행의 topic_frame·plan 을 재사용하고 understand·plan 을 건너뛴다 (ADR-9; 주제가 다르면 거부, `node_reused` 이벤트) | `graph.critic` = none/deterministic/full 이 ablation B/C/D. 노드 전후를 `node_start/node_end`(+`round`) 이벤트로, 판정·재계획은 `critique`/`replan` 이벤트로 남겨 설계평가 증거로 쓴다. `cost.json` 에 `critic_rounds`, `replans`, `final_critic_passed` |

### 테스트 방식

- LLM 은 `messages.parse` 를 흉내 내는 `FakeMessages` 로, HTTP 는 `httpx.MockTransport` 로 모킹. 실제 네트워크 테스트는 `scripts/smoke_*.py` 로만.
- `RunLogger(..., runs_dir=tmp_path)` 로 테스트 중 `runs/` 오염을 막는다. 러너(`graph.run_graph`·`baseline.run_baseline`)를 통째로 돌리는 테스트는 `monkeypatch.setattr(graph, "RunLogger", ...)` 로 같은 효과를 낸다 (`tests/test_graph.py` 참고).
- 노드 테스트는 `FakeMessages([출력1, 출력2, ...])` 에 호출 순서대로 Pydantic 객체를 넣어 LLM 응답을 정한다. 검사 실패 → 재호출 흐름을 검증하려면 첫 출력에 일부러 결함을 넣는다. `graph.critic: full` 이 기본이므로 그래프 통째 테스트는 critic 의 LLM 비판 출력(`{"issues": []}`)도 순서에 넣어야 한다. Replan 루프 테스트는 `tests/test_replan.py`.
- 테스트 주제 5개는 `eval/topics.yaml` (T1~T5, 분야 분산, 한·영 혼합). 특정 주제에 맞춘 프롬프트 튜닝은 금지 — 실제 평가 주제는 다를 수 있다.

## 작업 시 지킬 것

- 재현성 L1: 평가자(교수님)가 README 의 명령 3개와 Anthropic 키 하나로 실행한다. 의존성 추가 시 `uv.lock` 갱신, 새 환경변수는 `.env.example` 에 반영.
- 현재 진행 상태와 다음 할 일은 `plan.md` §5 작업 분해와 §8 변경 로그를 기준으로 판단한다.
- 커밋 메시지는 영어, Conventional Commits.
