# AI Research Agent

연구 주제 하나를 입력하면 **주제 이해 → 조사 계획 → 문헌 탐색 → 평가 → 종합 → Research Gap 제안**을 수행해
연구 착수용 브리프(Research Brief)를 만드는 에이전트.

연세대학교 DAS6035 *AI에이전트설계및응용* 중간 해커톤 제출물 (제출 2026-11-02).

## 빠른 시작

실행·구조·검증 결과는 **[`research_agent/README.md`](research_agent/README.md)** 에 한 페이지로 정리되어 있습니다.

```bash
cd research_agent
uv sync                       # uv 가 없으면: curl -LsSf https://astral.sh/uv/install.sh | sh  (Python 3.12 도 받아줍니다)
cp .env.example .env          # ANTHROPIC_API_KEY 입력 — 필요한 키는 이것 하나
uv run agent run --topic "생성형 AI 활용이 대학원생의 연구 생산성과 연구 품질에 미치는 영향"
# → runs/<타임스탬프>_graph_<주제>/report.md   (1회 ≈ $0.7 · 6~8분, claude-sonnet-5-5)
```

**실행 결과 바로 보기** — `research_agent/runs/` 에 대표 실행 8개를 넣어 두었습니다 (클린룸 2개 = `cleanroom.json` 포함, 주제 5개의 최종 구조 실행 = `ablation.json` 포함, 베이스라인 1개). 예시 주제의 클린룸 리포트:
[`runs/20261008T022603Z_graph_…/report.md`](research_agent/runs/20261008T022603Z_graph_생성형-ai-활용이-대학원생의-연구-생산성과-연구-품질에-미치는-영향/report.md) (한국어본, 영어 원문은 같은 폴더의 `report.en.md`).
각 폴더에는 `report.md`·`brief.json`·`events.jsonl`(단계 전이·LLM/도구 호출 로그)·`cost.json`(비용·결정적 지표)·노드별 중간 산출물이 있습니다.
제출 zip 에는 ablation 20회·반복 실행을 포함한 전체 55개 실행이 들어 있습니다.

GitHub: https://github.com/JAY2160288/research_agent · 웹 버전(초대 계정 전용, 같은 에이전트를 그대로 실행): https://research-brief-web.vercel.app

## 제출물 안내 — 지침의 세 항목이 어디에 있는가

| 지침 항목 | 위치 | 보는 법 |
|---|---|---|
| **설계 의도** | [`research_agent/docs/design.md`](research_agent/docs/design.md) §1 아키텍처(역할 카드·토폴로지 선택 이유·실패 대응·비용 모델) · §2 설계 의도("달라지는 것 / 아닌 것") · §6 한계. 배경은 [`goals.md`](goals.md)(평가 기준 → 목표 O1~O7), 결정 이력은 [`plan.md`](plan.md) §4 ADR-1~14 | design.md §1~§2 만 읽어도 "왜 이 구조인가"가 닿도록 썼습니다 |
| **소스** | [`research_agent/src/research_agent/`](research_agent/src/research_agent/) — `graph.py`(노드 순서 + Critic/Replan 루프), `nodes/`(6단계 + critic·replan·write), `schemas.py`(모든 입출력 타입 + 결정적 검사), `llm.py`(유일한 LLM 호출 지점), `tools/`(OpenAlex·arXiv·Crossref). 프롬프트는 [`prompts/`](research_agent/prompts/), 설정은 [`config/models.yaml`](research_agent/config/models.yaml), 테스트 98개는 [`tests/`](research_agent/tests/) | 구조 설명과 디렉터리 표는 [`research_agent/README.md`](research_agent/README.md) §2 |
| **수행 입출력 결과** | [`research_agent/runs/INDEX.md`](research_agent/runs/INDEX.md) — 모든 실행을 **입력 주제 → 출력 리포트 링크 → 비용·시간·결정적 지표** 순으로 색인. 실행 폴더마다 `report.md`(출력), `brief.json`(구조화 출력), `events.jsonl`(단계 전이·LLM/도구 호출 로그), `cost.json`, 노드별 중간 산출물 | GitHub 에는 대표 8개, 제출 zip 에는 55개 전체. 예시 주제의 클린룸 결과는 위 "빠른 시작" 링크 |

## 저장소 구조

| 경로 | 내용 |
|---|---|
| [`research_agent/README.md`](research_agent/README.md) | **먼저 읽을 문서** — 실행 3단계, 결과 폴더 읽는 법, 파이프라인 그림, 디렉터리, 설계 요점, ablation·클린룸 결과 요약 |
| [`research_agent/docs/design.md`](research_agent/docs/design.md) | 설계 문서 — 아키텍처, 설계 의도("달라지는 것/아닌 것"), ablation 전체 매트릭스, 반복 실행 편차, 클린룸, 한계 |
| [`goals.md`](goals.md) | 목표 체계 — 평가 기준에서 도출한 Objective O1~O7, 성공 지표, non-goal |
| [`plan.md`](plan.md) | 구현 계획 — 아키텍처, 설계 결정 기록(ADR-1~14), 주차별 작업 분해, 변경 로그 |
| [`research_agent/`](research_agent/) | 소스 코드(`src/`), 프롬프트, 설정, 테스트 98개, 평가 세트, 실행 결과(`runs/`, GitHub 에는 대표 8개) |

## 설계 요점

- **키는 Anthropic 하나.** 문헌 검색은 키가 필요 없는 공개 학술 API(OpenAlex·arXiv·Crossref)만 사용합니다.
- **출력 구조 고정.** 모든 단계가 Pydantic 스키마로 주고받고, 최종 리포트도 스키마 검증을 통과해야 저장됩니다.
- **품질 하한은 코드가 보장.** 인용 실존 검증, 주장-출처 연결, Gap 근거 ≥ 2 는 LLM 이 아니라 결정적 검사가 확인합니다. 문헌은 검색 도구 출력 그대로라 LLM 이 만들 수 없습니다.
- **Critic → Replan 루프.** 결정적 검사 5종 → 통과 시 LLM 비판 → 미달이면 부족한 sub-RQ 만 재검색 (최대 2회). 끝까지 못 채우면 리포트 §7 한계에 자동 기재.
- 실행마다 문장과 선택 문헌은 달라질 수 있으나, 리포트 구조·필드 채움·인용 검증률은 달라지지 않습니다 — 주제 5개 × 조건 4개 ablation 20회, 독립 반복 8회, 클린룸 2회에서 확인.

## 진행 상태

| 주차 | 내용 | 상태 |
|---|---|---|
| W1 | 스키마, LLM 래퍼, 학술 도구, 베이스라인 ReAct, 평가 세트 | 완료 |
| W2 | 역할 분리 그래프(Planner·Searcher·Evaluator·Synthesizer·Critic·Writer) | 완료 |
| W3 | Reflection·Replanning 루프, 같은 주제 반복 실행 안정성 | 완료 |
| W4 | 베이스라인 vs 최종 구조 ablation(20회), LLM-judge, 주장-근거 지지율·정답 회수율, 클린룸 재현, 누출 검사 | 완료 (2026-10-08) |
| 마무리 | `docs/design.md` 전 섹션, 리포트 렌더러 개편, 한국어 번역 단계(ADR-11), 제출 직전 재점검(누출 검사·클린 clone 재설치·zip 검증) | 완료 (2026-10-23) |
