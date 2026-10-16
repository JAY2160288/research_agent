# design.md — 설계 문서

- 상태: **2026-10-08 (W4 Day 5, 마무리 5.1)** — 전 섹션 작성. 2026-10-16: §1.2 역할 카드 · §1.3 토폴로지 선택 · §1.4 MAST 대응 · §1.5 비용·지연 모델 · §6 한계 1건 보강 (멀티에이전트 설계 용어로 재서술, plan.md ADR-14). 같은 날 `cost.json` 에 `stop_reason`·`critic_model` 추가, `scripts/node_costs.py`, 조건 E(Critic 만 opus) 1회 — 결과는 §6. 실행 결과가 더 늘면(Day 6 선택 반복) §5 표만 교체한다.
- 상위 문서: `../../goals.md` (목표 O1~O7), `../../plan.md` (ADR-1~14, 작업 분해, 평가 설계, §8 변경 로그). 이 문서는 두 문서의 결론 + 실험 결과를 한 곳에 모은 제출용 설명서다.
- 표의 원천: `uv run python scripts/summarize_runs.py --ablation --md --model claude-sonnet-5-5` (§3), `uv run python scripts/compare_repeats.py "생성형" --since 20261004T1200` (§5). 각 실행 폴더의 `cost.json` `checks` + `judge.json` 에서 계산되며 손으로 고치지 않는다.

## 1. 아키텍처

### 1.1 한 줄 요약

연구 주제 하나 → **understand → plan → [search → evaluate → synthesize → gap → critic] → write** → 7개 섹션 리포트. Critic 이 미달 판정을 내면 **replan** 이 부족한 sub-RQ 에만 새 쿼리를 만들어 루프 선두(search)로 돌아간다 (최대 2회). 지침의 필수 6단계(주제 이해 → 조사 계획 → 자료 탐색 → 자료 평가 → 비교·종합 → Gap·향후 연구)가 노드 하나씩에 대응하고, 루프가 Reflection·Replanning 이다.

```
[Topic]
  │
  ▼
understand ──→ TopicFrame (변수 X·Y, 모집단, 맥락, 영어 동의어)
  │
  ▼
plan ──→ ResearchPlan (sub-RQ 3~6개 × 검색 쿼리 2~4개, 소스 선호)
  │
  ▼  ┌─────────────────────────────────────────────────────────┐
     │ search    OpenAlex(주력) + arXiv(CS 보강) + Crossref(폴백)  │  LLM 없음
     │   │       → Paper (도구 출력 그대로, DOI/arXiv id 필수)    │
     │   ▼                                                       │
     │ evaluate  sub-RQ 당 12편 선별 → 관련성·신뢰도·방법·표본·결과 │
     │   │       → Evidence (verified 아니면 제외)               │
     │   ▼                                                       │
     │ synthesize  합의 / 상충(+원인 가설) / 조건부 → Synthesis    │
     │   ▼                                                       │
     │ gap       Gap(근거 ≥ 2) + 제안 RQ·방법·데이터 → GapList    │
     │   ▼                                                       │
     │ critic    결정적 5종 → (통과 시) LLM 비판 → Critique       │
     └───┬──────────────────────────────────────────────┬────────┘
         │ 통과 (또는 Replan 상한·예산 소진)              │ 미달
         ▼                                              ▼
       write ──→ ResearchBrief ──→ report.md        replan ──→ 걸린 sub-RQ 의 새 쿼리 1~3개
       (구조는 상태에서 조립,                         (계획에 덧붙임, 새 후보만 증분 평가)
        LLM 은 요약(한국어)·한계(영어)만)                   └──→ search 로
```

### 1.2 역할과 책임

| 노드 (역할) | 입력 → 출력 | LLM | 결정적 자체 검증 (`schemas.py` `check()`) |
|---|---|---|---|
| understand (Planner) | topic → `TopicFrame` | 1회 | 필드 비어있지 않음, 영어 동의어 ≥ 3 |
| plan (Planner) | TopicFrame → `ResearchPlan` | 1회 | sub-RQ 3~6, 쿼리 중복률 < 50% |
| search (Searcher) | ResearchPlan → `Paper[]` | **0회** | sub-RQ 당 ≥ 10편, DOI 또는 arXiv id 필수 — LLM 이 문헌을 만들 수 없는 구조 |
| evaluate (Evaluator) | Paper[] → `Evidence[]` | sub-RQ 당 1~2회 (10편 배치, 배치 4개 병렬 — ADR-12) | verified=False 즉시 제외, relevance < 3 제외 |
| synthesize (Synthesizer) | Evidence[] → `Synthesis` | 1회/라운드 | 모든 claim 에 evidence_id ≥ 1, 상충마다 원인 가설 |
| gap (Synthesizer) | Synthesis+Evidence → `GapList` | 1회/라운드 | Gap 당 근거 ≥ 2, 제안에 방법·데이터 |
| critic (Critic) | RunState → `Critique` | 결정적 통과 시 1회 | 인용 검증 100%·claim 출처·sub-RQ evidence ≥ 3·Gap 근거 ≥ 2·상충 가설 (plan.md §3.3) |
| replan (Planner) | Critique → 새 쿼리 | 1회/라운드 | 지목된 sub-RQ 마다 쿼리 ≥ 1, 없으면 결정적 fallback 쿼리 |
| write (Writer) | RunState → `ResearchBrief` | 1회 | 스키마 통과, 7개 섹션 |
| (렌더링, `report.py`) | ResearchBrief + papers + checks → `report.md` | **0회** | 요약 → 먼저 읽을 문헌 Top 10 → §1~§7 → 결정적 지표 카드 → 번호 인용 `[n]`(산문 속 DOI 도 치환) + 참고문헌, Evidence map, sub-RQ 별 접힌 표, Gap 제목+본문, §6 요약표. `agent render` 로 언제든 재생성 |
| (번역, `translate.py`, ADR-11) | brief.json 산문 필드 → `brief.ko.json` → `report.md`(한국어)·`report.en.md` | **1회** (사후, 실행당 ≈ $0.12) | 한글·숫자/DOI 보존·길이 비율 검사, 실패 항목은 영어 유지. 파이프라인·지표 불변 |

모든 노드는 `nodes/__init__.py` 의 `checked_call` 공통 루프를 쓴다: **구조화 호출 → `check()` → 실패 시 이슈를 되먹여 재호출(최대 2회) → 그래도 실패면 `notes` 에 적고 계속 진행**. 어떤 노드도 실행을 죽이지 않는다 (O1). 미해결 노트는 write 가 리포트 §7 한계에 `[auto]` 로 편입한다.

#### 역할 카드 — 역할은 페르소나가 아니라 경계다

위 표의 역할을 "책임 범위 · 도구 권한 · 읽는 맥락 · 완료 기준" 네 경계로 다시 적는다 (멀티에이전트 설계의 역할 카드 형식). 어떤 역할도 **프롬프트의 말투**로 구분되지 않는다 — 구분은 전부 *무엇을 읽고, 무엇을 돌려주고, 코드가 무엇을 검사하는가* 다. 핸드오프는 모두 Pydantic 스키마(structured handoff)이며 원시 초록·대화 이력·이전 라운드의 LLM 출력 원문은 다음 역할에 넘기지 않는다.

| 역할 | 하는 일 / **하지 않는 일** | 허용 도구 | 읽는 맥락 (그 외는 격리) | 완료 기준 (코드가 검사) | 미달 시 |
|---|---|---|---|---|---|
| understand | 주제를 변수·모집단·맥락·동의어로 고정 / **검색하지 않고 문헌을 언급하지 않는다** | 없음 | 주제 문자열 하나 | `TopicFrame.check` — 필드 비어있지 않음, 영어 동의어 ≥ 3 | 이슈 되먹여 재호출 ≤ 2회 → `notes` |
| plan | sub-RQ 와 검색 쿼리 설계 / **검색을 실행하지 않고 문헌 가치를 판단하지 않는다** | 없음 | `TopicFrame` + 원 주제 | `ResearchPlan.check` — sub-RQ 3~6, 쿼리 중복률 < 50% | 같음 |
| search | 쿼리 실행, 레코드 정규화·중복 제거 / **LLM 을 부르지 않고 레코드를 고치거나 만들지 않으며 관련성을 판단하지 않는다** | OpenAlex·arXiv·Crossref — **프로젝트에서 도구를 소유한 유일한 역할** | 계획의 쿼리 (Replan 라운드엔 새 쿼리만) | sub-RQ 당 후보 ≥ 10, DOI 또는 arXiv id 필수 | `notes`(candidate shortfall); 폴백·차단 사실은 §7 에 자동 기재 |
| evaluate | 배치 10편의 관련성·신뢰도·방법·표본·발견 기록 / **검색·종합·문헌 간 비교를 하지 않는다** | 없음 | RQ·sub-RQ 목록 + **자기 배치 10편**의 제목·연도·venue·인용수·초록(1,200자 상한). 다른 배치·다른 라운드의 평가는 보지 않음 | `EvidenceTable.check` — 배치 id 와 1:1, verified 아닌 id 제외, relevance < 3 제외 | 되먹임 ≤ 2회 → 남은 이슈는 `notes`, 배치 밖 id·미검증 id 는 버림 |
| synthesize | 합의·상충(+가설)·조건부 claim 작성 / **새 문헌을 끌어오지 않고(cite ONLY these ids) 초록 원문을 읽지 않는다** | 없음 | `evidence_digest` — 문헌당 1줄(id·연도·관련성·신뢰도·방법·표본·발견) + Replan 라운드엔 직전 Critique 지적 | `Synthesis.check` — claim 마다 evidence_id ≥ 1 (digest 안의 id 만), 상충마다 가설 | 같음 |
| gap | Gap·제안 RQ·방법·데이터 / **종합을 고치지 않고 문헌을 추가하지 않는다** | 없음 | digest + `Synthesis` + 직전 Critique | `GapList.check` — Gap 당 근거 ≥ 2, 제안에 방법·데이터 | 같음 |
| critic | 판정과 지시 / **고치지 않는다** (수정은 synthesize·gap·replan 의 일), **검색하지 않는다** | 없음 | digest + `Synthesis` JSON + `GapList` JSON (초록 원문 X) | 결정적 5종 → 통과 시에만 LLM 비판, `LLMCritique.check`(sub_rq_id 가 계획에 있음). major 가 있으면 미통과 + 실행 가능한 `actions` | 이미 재검색한 sub-RQ 에 같은 `search` 지적이 남으면 **한계로 기록하고 통과** (`critic_persisting`) |
| replan | 지목된 sub-RQ 의 새 쿼리 1~3개 / **지목되지 않은 sub-RQ 에 쿼리를 더하지 않고 종합을 바꾸지 않는다** | 없음 | sub-RQ·기존 쿼리·후보/관련 편수·Critic 지적·이전 Replan 쿼리 | `ReplanPlan.check` — 지목 sub-RQ 마다 ≥ 1, 계획에 없는 sub-RQ 거부, 기존 쿼리와 중복 거부 | 끝까지 비면 sub-RQ 질문에서 뽑은 **결정적 fallback 쿼리** — 라운드를 비워 보내지 않음 |
| write | 한국어 요약·영어 한계 문장 / **구조 섹션을 쓰지 않고(코드가 상태에서 조립) 인용 번호를 매기지 않고 문헌을 추가하지 않는다** | 없음 | claim 문장·상충·조건부·coverage note·Gap 설명·최종 Critic 지적·편수 (문헌 메타데이터 X) | `BriefText.check` → `ResearchBrief` 스키마 통과 | `notes` → §7 `[auto]` |

에스컬레이션의 종점은 사람이다. 어떤 역할도 미달을 "해결된 것처럼" 숨길 수 없고, 루프가 끝난 뒤 남은 미달은 §7 한계에 `[auto]` 로 기재되어 독자(연구자)가 판단한다. 사람의 개입 수단은 `--exclude`/`--include` 로 문헌을 교정해 다시 돌리는 것과 `--resume` 이다. **역할 간에 다른 것은 맥락·도구·검증 장치이고 모델은 같다** (sonnet 하나, judge 만 opus) — 이 점은 §6 한계에 적는다.

### 1.3 설계 결정의 뼈대 (plan.md §4 ADR 요약)

| ADR | 결정 | 왜 |
|---|---|---|
| 1 | 그래프 프레임워크 없이 직접 구현 (`graph.py` ≈ 150줄) | Planning·Reflection·Replanning 이 **내 코드에** 보여야 설계평가가 되고, 프레임워크 버전 변동이 재현 리스크 |
| 2 | Claude 단일 공급자, `llm.py` 가 유일한 호출 지점, SDK `messages.parse` 로 Pydantic 구조화 출력 | 모든 호출의 토큰·비용·재시도가 한 곳에서 기록됨. 평가자는 모델명만 바꾸면 됨 |
| 3 | 키 없는 공개 학술 API 만 (OpenAlex·arXiv·Crossref). `Paper` 는 도구 출력 그대로 | 평가자 환경에 키 1개(Anthropic)만 요구 (L1). LLM 이 문헌을 생성할 경로를 구조적으로 차단 (O2) |
| 5·7 | 품질은 Critic 이 보장: 결정적 5종 → 통과 시에만 LLM 비판 → major 면 Replan (증분 재검색·재평가) | 결정적 실패가 뻔한 상태에 LLM 비용을 쓰지 않음. 판정과 재계획이 각각 이벤트로 남아 O4 증거 |
| 6·8 | OpenAlex 주력 + arXiv circuit breaker + Crossref 폴백 | 외부 API 상태에 완주 여부가 흔들리면 안 됨. 차단·폴백 사실은 §7 에 자동 기재 |
| 9 | ablation B/C 는 D 의 계획을 재사용 (`--plan-from`) | 조건 간 차이가 계획·검색 변동이 아니라 품질 게이트 차이만 반영 |
| 10 | 사후 지표 2종 (주장-근거 지지율, 정답 서베이 회수율) 을 파이프라인 밖에 | "인용 실존 ≠ 주장 지지" 라는 벤치마크 문헌의 공통 지적을 분리 보고 |

#### 왜 "고정 파이프라인 + Critic" 인가 — 토폴로지 선택 (plan.md ADR-14)

멀티에이전트 토폴로지(Supervisor·Hierarchical·Swarm·Blackboard·Pipeline/Parallel·Debate) 가운데 이 과제에 맞는 것을 과제 특성으로 고른 결과다. 출발점은 "단일 에이전트로 충분한가" 이고, 그 답이 ablation 조건 A 다 (§3.6: 주장-근거 지지율 A 52% vs D 78%, claim 단위 76% vs 94%).

| 과제 특성 | 이 과제에서는 | 시사 |
|---|---|---|
| 분해 가능성 | sub-RQ 3~6개는 서로 독립이라 **검색·평가는 sub-RQ·배치 단위로 병렬** (`search_workers`·`evaluate_workers` 4). 종합·Gap·Critic 은 전체 evidence 를 봐야 해서 분해되지 않음 | 노드 **안**에서만 fan-out, 노드 **간**은 순차 |
| 순차 의존 | 높음 — 이해 → 계획 → 검색 → 평가 → 종합 → Gap 은 앞 단계 출력이 뒤 단계 입력. 과제 지침의 6단계 자체가 순서 | 고정 순서(Pipeline). LLM 이 다음 단계를 고를 이유가 없음 |
| 도구 밀도 | 낮음 — 검색 도구 3개가 전부 search 노드 하나에 속하고, LLM 을 부르는 노드는 도구가 0개 | 도구 라우팅 불필요. **도구 집약 단계에 LLM 을 두지 않는다** (도구 많은 과제에서 조정 비용이 커진다는 보고에 대한 답) |
| 검증 필요성 | 높음 — 인용 실존·출처·커버리지·Gap 근거는 **정답 확인이 가능**하므로 코드가 검사하고, 종합의 깊이는 작성자와 분리된 검토자(LLM Critic)가 본다 | 작성자/검토자 분리 + 중앙 검증 (오류 증폭 억제) |
| 권한·모델 분리 | 없음 — 외부 쓰기 권한이 없는 읽기 전용 도구, 모델 하나 | Supervisor 식 권한 경계·사람 승인 단계 불필요 |

기각한 토폴로지와 이유:

- **Supervisor-Worker (LLM 라우터)**: 경로가 고정이라 LLM 이 "다음 워커" 를 고를 판단거리가 없다. 라운드마다 감독 호출이 붙어 비용·지연만 늘고 재현성(L1)이 나빠진다. 우리 감독자는 `graph.py` 의 while 루프, 즉 **코드**다.
- **Hierarchical**: 팀이 하나다.
- **Swarm / handoff**: 역할이 겹치지 않아 넘길 일이 없고, 소유권 핑퐁과 감사 어려움은 L1·O4(로그 증거)와 상충한다.
- **Blackboard**: `RunState` 가 사실상 블랙보드지만 비동기 수집이 없고 키마다 **단일 작성자**가 정해져 있다 (plan 은 plan·replan, evidence 는 evaluate, synthesis 는 synthesize, critiques 는 critic). 쓰기 충돌 관리가 필요한 일반 블랙보드는 과하다.
- **Debate / Ensemble**: "종합의 깊이" 처럼 정답 확인이 어려운 판단에는 맞지만, 제안자 수 × 라운드만큼 호출이 늘어 실행당 $1·10분 상한(goals.md O6) 안에 들지 않는다. 대신 검토자 1명(Critic) + Replan 상한 2 로 같은 효과의 일부를 얻는다. 제출 후 실험 후보 (§6).
- **단일 에이전트**: 기준선 A 로 측정했고(§3), 구조 없이 재시도도 없어서 지지율·커버리지가 낮다. 다만 A 와 D 의 차이는 "에이전트 수" 가 아니라 **스키마(B)·결정적 검사(C)·LLM Critic(D)** 각각의 기여로 분리해 읽어야 한다 (§3.4) — 동질 모델로 역할 이름만 나눈 워크플로는 단일 에이전트와 다르지 않다는 지적이 있으므로, 이 프로젝트가 주장하는 것은 멀티에이전트의 이득이 아니라 **구조(계약·검증)의 이득**이다.

오케스트레이션 방식은 **정적 뼈대 + 국소 동적**이다. 실행 경로·종료 조건·예산은 코드가 정하고, LLM 은 두 곳에서만 판단한다: Critic 이 "미달인가, 어느 sub-RQ 를 다시 찾아야 하는가" 를 **제안**하고(승인은 결정적 검사와 `check()` 가 함), Replan 이 새 쿼리를 쓴다. 종료는 겹으로 둔다 — ① Critic 통과, ② `max_replans` 2, ③ 경과 시간·비용이 상한의 60% 를 넘으면 Replan 생략(`replan_budget_fraction`), ④ $1·10분 상한(`CostLimitExceeded`/`TimeLimitExceeded`) + 종합·Gap 이 있으면 `grace_write`, ⑤ 재검색 뒤에도 같은 지적이 남으면 "진전 없음" 으로 보고 한계 기재 후 통과(`critic_persisting`). 성공 조건(①)과 안전 종료(②~⑤)를 함께 둔 것이다.

### 1.4 관찰 가능성 (goals.md O4)

실행 폴더 `runs/<UTC>_<mode>_<topic>/` 의 `events.jsonl` 에 모든 단계 전이가 남는다. 설계평가 기준인 다섯 개념의 로그 증거:

| 개념 | 이벤트 | 산출물 |
|---|---|---|
| Planning | `node_start/node_end` (understand·plan) | `topic_frame.json`, `plan.json` |
| Tool Use | `tool_call` (openalex·arxiv·crossref, 캐시 적중 여부) | `papers.json` |
| RAG | evaluate 의 배치 호출 — 초록을 프롬프트에 넣고 구조화 평가 | `evidence.json` |
| Reflection | `critique` (round, passed, 결정적 이슈, LLM major/minor) | `critique_N.json` |
| Replanning | `replan` (걸린 sub-RQ, 새 쿼리), 이후 `node_start` round=N+1 | `replan_N.json`, 리포트 §2 에 덧붙은 쿼리 |

`cost.json` 에 `critic_rounds`·`replans`·`final_critic_passed`·`checks`(결정적 지표) 와 **`stop_reason`**(루프가 왜 끝났나: critic_passed · critic_persisting · replan_limit · replan_budget · limit_exceeded …, 2026-10-16 이후 실행) 이 요약된다. `scripts/summarize_runs.py` 가 이를 표로 모은다.

#### 실패 양상 대응 — 실제 사고를 MAST 분류로 읽기

멀티에이전트 실패 분류 MAST(3범주 14양상: ① 시스템 설계·명세, ② 에이전트 간 불일치, ③ 과제 검증)로 이 프로젝트의 실제 사고(plan.md §8 2026-10-04~06)를 다시 읽으면, 전부 모델 지능이 아니라 명세·소통·검증의 문제였고 장치도 전부 코드다.

| 실제 사고 (날짜) | MAST 범주 · 양상 | 장치 |
|---|---|---|
| Replan 라운드 gap 이 7만 자 JSON 을 쏟다 16384 토큰에서 잘림 → 3분×2 재시도 → 10분 초과, 완주 실패 (10-04 T1 반복 2회차) | ① 명세 — 작업 명세(출력 형식·길이) 불이행 | `node_max_tokens` 6000 분리, json_invalid 에 "더 짧게" 되먹임, 프롬프트에 길이 상한 |
| evaluate HTTP 요청 1건이 7분 멈춤 → 10분 상한 통째로 소모 (10-04 반복 3회차) | ① 설계 — 호출 수준 종료 조건 부재 | `request_timeout_sec` 180, `sdk_max_retries` 2 |
| Replan 이 `items: []` 로 두고 rationale 에만 쿼리를 글로 적음 (10-04, 2회 연속) | ② 불일치 — 계약 위반·정보 보류 (받는 쪽 search 는 `items` 만 읽음) | `ReplanPlan.check(required)` 되먹임 → 끝까지 비면 결정적 fallback 쿼리. **제안은 LLM, 승인은 코드** |
| 스키마 `max_length` 를 LLM 이 어겨 SDK 안에서 ValidationError → 응답 손실, 실행 사망 (10-04) | ① 명세 — 계약을 잘못된 층에 둠 | `llm.call` 이 SDK 측 검증 실패도 되먹임, 상한은 코드에서 자름, 예상 밖 예외도 `status=error` + `state.json` |
| rq2 "실험 연구 없음" 을 3라운드 연속 major 로 지적 → 10분 초과 (10-04 T1) | ① 설계 — 단계 반복·종료 조건 인식 실패 (진전 없음) | `critic_persisting`: 재검색한 sub-RQ 에 같은 search 지적이면 한계 기재 후 통과; `max_replans`; `replan_budget_fraction` |
| 34회 호출 뒤 write 직전 10.1분 → 브리프 없이 종료 (10-04 T1) | ③ 검증 — 조기 종료 | `grace_write` (종합·Gap 이 있으면 write 1회 허용) |
| 편수 기준 커버리지는 통과했지만 언어·대상이 빗나간 문헌 (T6 D rq3·rq4) | ③ 검증 — 불완전한 검증 | LLM Critic 이 적발·한계 기재. 결정적 지표에는 미반영 (§6) |
| §7 `[auto]` 항목이 160자에서 잘려 문장 중간 (10-06 T3 D, judge J7) | ② 불일치 — 핸드오프에서 정보 손실 | 자르지 않음 (스키마가 "한 문장" 을 보장) |
| 중간 라운드에서 풀린 Critic 미달이 §7 에 남음 | ③ 검증 — 잘못된 검증 | 미달 노트는 루프 종료 후 **최종 라운드 기준**으로만 |
| OpenAlex 일일 크레딧 429, arXiv 전면 차단 (10-04·10-05) | (외부 의존) | Crossref 폴백(ADR-8), circuit breaker(ADR-6), 사실을 §7 에 자동 기재 |

개입은 단계적이다 — **Retry**(`checked_call` 되먹임, SDK 재시도) → **Replan**(replan 노드) → **Fallback**(Crossref, `fallback_query`, `grace_write`) → **Stop**(종료 5겹, §1.3) → **사람**(§7 `[auto]` 를 읽는 독자, `--exclude/--include`·`--resume` 재실행). 감시는 전부 규칙 기반이라 LLM 비용이 없다: 호출 수·토큰·경과 시간은 `RunLogger` 가, 반복 지적은 `critic` 이 센다.

### 1.5 비용·지연 모델

비용 ≈ Σ 호출 × (입력 토큰 × 입력 단가 + 출력 토큰 × 출력 단가), 지연 ≈ 임계 경로 위 호출 지연의 합. 2026-10-10 14:34 실행(T1, sonnet, 웹 경유, Replan 2회, §5 마지막 행)의 `events.jsonl` 을 노드별로 합산하면 (`uv run python scripts/node_costs.py runs/20261010T143424Z_* --md` — node_start/node_end 의 `t` 차와 `llm_call` 의 role 별 합계):

| 노드 | 실행 횟수 | 소요 (초) | LLM 호출 | 입력 토큰 | 출력 토큰 | 비용 |
|---|---|---|---|---|---|---|
| understand | 1 | 5 | 1 | 1,908 | 289 | $0.007 |
| plan | 1 | 11 | 1 | 2,120 | 1,236 | $0.017 |
| search | 3 | 51 | 0 | 0 | 0 | $0.000 |
| evaluate | 3 | 54 | 11 | 66,123 | 19,187 | $0.324 |
| synthesize | 3 | 71 | 3 | 24,342 | 10,140 | $0.150 |
| gap | 3 | 59 | 3 | 30,051 | 7,164 | $0.132 |
| critic | 3 | 48 | 2 | 25,888 | 6,090 | $0.113 |
| replan | 2 | 8 | 2 | 6,552 | 486 | $0.018 |
| write | 1 | 11 | 1 | 4,396 | 1,177 | $0.021 |
| **합계** | | **318** | **24** | **161,380** | **45,769** | **$0.780** |

읽는 법:

- **지연은 임계 경로가 정한다.** 노드 소요의 합(317.5초)이 전체 경과(318.6초)와 같다 — 노드 간 병렬이 없으니 임계 경로가 곧 전체다. 병렬은 노드 안에만 있다: evaluate 11회 호출이 54초 (순차였다면 호출당 10~13초 × 11 ≈ 2분 이상). search 51초는 전부 네트워크(OpenAlex 30회 + arXiv 12회, 캐시 미적중).
- **재검색 라운드가 절반 이상이다.** 1라운드(understand~critic) $0.337 · 119초, Replan 라운드 2회 $0.423 · 188초, write $0.021 · 11초. 라운드마다 synthesize·gap·critic 이 evidence digest 를 **다시 읽는다** — 비용의 큰 부분이 "다시 읽는 맥락" 이라는 일반론이 그대로 보인다. 프롬프트 캐시 적중은 0 (`cache_read` 0) 이다. digest 를 프롬프트 앞에 고정해 같은 라운드의 세 호출이 캐시를 나눠 쓰는 것이 제출 후 비용 개선 후보다 (출력 불변이라 ADR-12 범위, `RunLogger` 가 캐시 토큰을 이미 기록하므로 효과 측정은 바로 된다).
- **토큰 수는 입력이 3.5배지만 비용은 출력이 59%** ($0.323 vs $0.458, sonnet 단가 입력 $2 · 출력 $10 /1M). 따라서 이 프로젝트에서 비용 손잡이는 (a) evaluate 의 편수 `evaluate_per_subrq` (입력 41%·출력 42% 를 차지) 와 (b) Replan 횟수다. 두 손잡이가 `config/models.yaml` 에 있다.
- 에이전트를 하나 늘릴 때의 다섯 비용(호출, 서로의 맥락을 읽는 입력 토큰, 순차 지연, 핸드오프 정보 손실, 조정 실패 경로)에 대해 이 설계가 지불하는 것은 Critic·Replan 의 호출 4회 · $0.13 과 라운드 재실행이고, 돌려받는 것이 §3 의 B→D 차이다.

## 2. 설계 의도 — "달라지는 것 / 아닌 것"

핵심 원칙 (goals.md O7): **품질을 모델의 똑똑함에 맡기지 않고 파이프라인 구조가 보장한다.** 평가자가 본인 키와 다른 모델로 돌려도 결론 문장은 달라지지만 리포트의 구조와 품질 하한은 같아야 한다. 아래 표의 오른쪽 열이 "무엇이 보장하는가" 다.

| 달라져도 되는 것 (측정: §5 편차) | 달라지면 안 되는 것 (측정: §4·§5 불변 지표) | 보장 장치 |
|---|---|---|
| 문장 표현, 한국어 요약 | 리포트 7개 섹션 구조 | write 가 구조를 **상태에서 조립**하고 LLM 은 요약·한계 문장만 씀. `ResearchBrief` 스키마 검증 통과해야 저장 |
| 선택된 개별 문헌 (실행 간 Jaccard 0.13) | 인용 검증률 100% | `Paper` 는 도구 출력 그대로, DOI 없으면 폐기, `unknown_ids` 검사. 베이스라인도 같은 도구를 씀 |
| sub-RQ 의 구체적 문구·개수(5~6) | 모든 claim 에 출처 ≥ 1, Gap 당 근거 ≥ 2 | `Synthesis.check()`·`GapList.check()` 가 되먹여 재호출, Critic 결정적 검사가 2차 게이트 |
| Gap 의 내용, 제안 RQ (실행 간 근거집합 겹침 0.03) | 제안마다 방법·데이터 필드 채움 | 스키마 `min_length` + `check()` |
| Replan 횟수 (0~2), 비용 ($0.3~0.8), 시간 (3~8분) | 비용 ≤ $1 · 시간 ≤ 10분 · 완주 | `RunLogger` 상한 검사, `replan_budget_fraction`, `grace_write` |
| LLM Critic 의 엄격함 (Haiku 는 끝까지 major, Sonnet 은 통과) | 미달 항목이 리포트에서 **사라지지 않음** | Critic 미해결 노트 → §7 한계 `[auto]` 자동 기재 |

**지침과의 대응.** 지침의 Agent 역할 6단계(이해 → 계획 → 탐색 → 평가 → 비교·종합 → Gap·향후 방향)는 노드 6개(understand·plan·search·evaluate·synthesize·gap)와 리포트 §1~§6 에 1:1 로 대응하고, "정해진 답이 아니라 좋은 연구 결과를 만드는 Agent" 라는 중요사항은 이 §2 의 원칙 그 자체다 — 결론은 실행마다 달라도 되고, 근거의 검증 가능성과 한계의 정직한 기재(§7)가 고정된다. 예시 입력(T1)은 테스트 주제 5개 중 하나로만 쓰고 프롬프트를 거기에 맞추지 않았다 (goals.md non-goal). **출력 언어**: 파이프라인(brief.json)은 요약만 한국어, 나머지 영어다 — 쿼리·초록이 영어라 노드가 영어로 쓰는 편이 토큰·검사 측면에서 안전하고, `agent support` 의 초록 verbatim 대조(ADR-10)도 이 영어 brief 에 대고 한다. 독자가 읽는 `report.md` 는 **사후 번역 단계** `agent translate` (ADR-11) 가 brief 의 산문 필드만 LLM 1회로 한국어로 옮겨 그린 것이고, 영어 원문은 `report.en.md` 로 남는다. 번역이 내용을 바꾸지 않았음은 코드가 확인한다(한글 포함, 원문 숫자·DOI 토큰 전부 보존, 길이 비율; 걸린 항목은 영어 유지). 논문 제목·저자·DOI·검색 쿼리·초록 인용·§3 표의 결과 요약은 번역하지 않는다. 처음엔 "영어여야 ADR-10 이 성립한다" 고 적었으나 인용문은 초록 쪽에서 나오므로 claim 언어와 무관하다 — 정정. §6 향후 연구 방향은 §5 각 Gap 의 제안 RQ·방법·데이터를 번호 목록으로 다시 모은 것이라 내용이 §5 와 겹친다 — goals.md §5 의 7섹션 형식을 그대로 따른 결과이며, 읽는 이가 제안만 빠르게 훑는 용도다.

**리포트의 가시성은 렌더러가 책임진다 (2026-10-08 개편).** 다른 리서치 에이전트(Deep Research 류의 번호 인용 + 참고문헌, Elicit 의 표 중심 제시, Consensus/Scite 의 주장별 지지 편수, 체계적 문헌고찰의 PRISMA 깔때기·evidence map)에서 공통 장치를 빌려 `report.py` 에 넣었다: 맨 위 카드(검색 524 → 평가 98 → 인용 98/98 검증, 커버리지, Replan 횟수, 미해결 한계 수 — 전부 `post_checks` 수치), 인용 `[n]` + 참고문헌(저자·연도·제목·DOI 링크), §3.1 Evidence map(sub-RQ × 신뢰도 구간 편수, 커버 ✅/⚠️), §3.2 sub-RQ 별 머리 요약 + 접힌 표, claim 옆 `(근거 n편 · 신뢰도 평균 x)`, 상충의 `A n편 vs B m편`, §6 제안 표, §7 에서 LLM 서술과 파이프라인 자동 기재를 분리. **LLM 호출 0** 이라 `brief.json`·`papers.json`·`cost.json` 만으로 `agent render --all` 이 기존 실행 전부를 같은 형식으로 다시 그린다 — 지표(`checks`)는 `brief.json` 에서 계산되므로 ablation 결과는 그대로이고, judge 점수 20회는 개편 전 형식(`report_v1.md` 로 보관)을 보고 매긴 것이다.

**같은 날 2차 개편 — "독자가 돈 주고 쓸 리포트인가".** 1차 개편은 장치는 다 갖췄지만 채점용 카드가 맨 앞이고 독자가 원하는 답은 표 더미 뒤에 있었다. 그래서 (1) 읽는 순서를 **요약 → 먼저 읽을 문헌 Top 10 → 품질 카드 → §1~§7** 로 바꿨다. Top 10 은 Evaluator 의 관련성→신뢰도→연도 순으로 코드가 고르며 번호 [1]~[10] 이 여기서 매겨져 참고문헌이 자연히 중요도순이 된다. (2) LLM 이 산문(커버리지 메모·Gap 설명·한계·Critic 노트)에 박아 넣은 DOI·arXiv id 를 레지스트리와 대조해 `[n]` 으로 치환한다 — 구조화 필드만 번호였던 반쪽 인용 체계를 하나로 맞춘 것. (3) Gap 은 굵은 문단 대신 `### G n. 짧은 제목` + 본문, §6 은 §5 를 복붙하던 표를 요약표로, Critic 자동 노트의 리스트 repr 은 항목별 불릿으로. (4) 관련성 ≤ 1 로 버려진 문헌은 참고문헌 번호를 받지 않는다 (T1 D: 95 → 69편). 전부 표현 계층이라 지표·ablation 결과는 그대로다.

**보장하지 않는 것도 분명히 한다.** 구조가 지키는 것은 "하한" 이다: sub-RQ 에 문헌 자체가 없으면 Replan 2회로도 채우지 못하며, 그 경우 "채움" 이 아니라 **"솔직한 기재"** 를 보장한다 (W3 T1 12:07 실행 5/6, T3 D rq3, T6 D rq3·rq4 — 모두 §7 에 자동 기재). judge 가 보는 "종합의 깊이" 는 구조가 아니라 모델이 결정하며 (§3.4 항목 3), 이는 §6 한계에 적는다.

## 3. Ablation 결과 (plan.md §6.3)

### 3.1 조건

| 조건 | 설명 | 실행 방법 |
|---|---|---|
| A | 베이스라인 — 단일 ReAct 루프, 사후 검사만 하고 재시도 없음 | `agent run --mode baseline` |
| B | 역할 분리 그래프, Critic 없음 | `--mode graph --critic none` |
| C | 그래프 + Critic 결정적 검사 5종만 (LLM 비판 없음) + Replan | `--mode graph --critic deterministic` |
| D | 그래프 + Critic 전체 (결정적 → LLM 비판) + Replan — **최종 구조** | `--mode graph` (기본) |

- 주제 5개 (`eval/topics.yaml`, T1~T4·T6), 한국어 입력. 실행 모델 `claude-sonnet-5-5`, judge `claude-opus-5-5`, Replan 상한 2.
- 공정성 통제 (ADR-9): 주제마다 D 를 먼저 돌려 TopicFrame·Plan 을 만들고 B·C 는 그 계획을 `--plan-from` 으로 재사용 → 첫 라운드 검색 쿼리가 같고 도구 캐시가 그대로 맞아 조건 간 차이는 **품질 게이트 차이만** 반영한다. A 는 계획 노드가 없어 독립 실행.
- 실행 일정: 10/05 T1·T2, 10/06 T3·T4 + A×4, 10/07 T6 (OpenAlex 일일 한도 때문에 분할, plan.md §5).

### 3.2 주제 × 조건 매트릭스 (sonnet-5-5, 20회 전부 완주)

열: cost = USD, min = 분, calls = LLM 호출 수, cite_ok = 인용 검증률, claim_src = 출처 있는 claim / 전체, subrq = evidence ≥ 3 인 sub-RQ / 전체, gaps_ok = 근거 2편 이상인 Gap / 전체, replans = Replan 횟수, judge = LLM-judge J1~J7 평균 (5점), flags = judge 가 결정적 지표와 모순된 점수 수.

| topic | cond | model | run | status | cost | min | calls | cite_ok | claim_src | subrq | gaps_ok | replans | judge | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 | A | sonnet-5-5 | 1006-0308 | ok | $0.156 | 1.0 | 3 | 100% | 7/7 | 5/5 | 4/4 | - | 3.86 | 0 |
| T1 | B | sonnet-5-5 | 1005-0008 | ok | $0.307 | 3.2 | 10 | 100% | 12/12 | 6/6 | 5/5 | 0 | 4.14 | 0 |
| T1 | C | sonnet-5-5 | 1005-0011 | ok | $0.305 | 4.0 | 10 | 100% | 11/11 | 6/6 | 5/5 | 0 | 4.29 | 0 |
| T1 | D | sonnet-5-5 | 1005-0000 | ok | $0.825 | 7.5 | 25 | 100% | 13/13 | 6/6 | 5/5 | 2 | 4.14 | 0 |
| T2 | A | sonnet-5-5 | 1006-0310 | ok | $0.262 | 1.7 | 4 | 100% | 9/9 | 6/6 | 3/3 | - | 3.43 | 0 |
| T2 | B | sonnet-5-5 | 1005-0023 | ok | $0.321 | 3.7 | 10 | 100% | 12/12 | 6/6 | 5/5 | 0 | 4.14 | 0 |
| T2 | C | sonnet-5-5 | 1005-0028 | ok | $0.318 | 3.6 | 10 | 100% | 11/11 | 6/6 | 5/5 | 0 | 3.86 | 0 |
| T2 | D | sonnet-5-5 | 1005-0016 | ok | $0.662 | 7.1 | 19 | 100% | 12/12 | 6/6 | 5/5 | 1 | 4.00 | 0 |
| T3 | A | sonnet-5-5 | 1006-0312 | ok | $0.169 | 1.2 | 3 | 100% | 9/9 | 5/5 | 4/4 | - | 3.57 | 0 |
| T3 | B | sonnet-5-5 | 1006-0248 | ok | $0.264 | 2.1 | 9 | 100% | 11/11 | 5/5 | 5/5 | 0 | 4.00 | 0 |
| T3 | C | sonnet-5-5 | 1006-0251 | ok | $0.273 | 2.2 | 9 | 100% | 11/11 | 5/5 | 5/5 | 0 | 3.86 | 0 |
| T3 | D | sonnet-5-5 | 1006-0241 | ok | $0.815 | 6.8 | 24 | 100% | 9/9 | 5/5 | 5/5 | 2 | 4.14 | 0 |
| T4 | A | sonnet-5-5 | 1006-0314 | ok | $0.176 | 1.2 | 3 | 100% | 6/6 | 4/5 | 4/4 | - | 3.43 | 0 |
| T4 | B | sonnet-5-5 | 1006-0301 | ok | $0.327 | 2.3 | 10 | 100% | 10/10 | 6/6 | 5/5 | 0 | 3.71 | 0 |
| T4 | C | sonnet-5-5 | 1006-0304 | ok | $0.342 | 2.4 | 10 | 100% | 12/12 | 6/6 | 5/5 | 0 | 3.86 | 0 |
| T4 | D | sonnet-5-5 | 1006-0254 | ok | $0.761 | 6.3 | 21 | 100% | 13/13 | 6/6 | 5/5 | 1 | 4.14 | 0 |
| T6 | A | sonnet-5-5 | 1007-0230 | ok | $0.163 | 1.1 | 3 | 100% | 8/8 | 5/5 | 3/3 | - | 3.71 | 0 |
| T6 | B | sonnet-5-5 | 1007-0223 | ok | $0.279 | 2.4 | 9 | 100% | 10/10 | 5/6 | 5/5 | 0 | 4.14 | 0 |
| T6 | C | sonnet-5-5 | 1007-0226 | ok | $0.421 | 3.7 | 14 | 100% | 12/12 | 6/6 | 5/5 | 1 | 3.86 | 0 |
| T6 | D | sonnet-5-5 | 1007-0216 | ok | $0.765 | 6.7 | 24 | 100% | 11/11 | 6/6 | 5/5 | 2 | 4.29 | 0 |

### 3.3 조건별 평균

| cond | n | done | cost | min | cite_ok | claim_src | subrq | gaps_ok | judge |
|---|---|---|---|---|---|---|---|---|---|
| A | 5 | 5/5 | $0.185 | 1.2 | 1.00 | 1.00 | 0.96 | 1.00 | 3.60 |
| B | 5 | 5/5 | $0.299 | 2.7 | 1.00 | 1.00 | 0.97 | 1.00 | 4.03 |
| C | 5 | 5/5 | $0.332 | 3.1 | 1.00 | 1.00 | 1.00 | 1.00 | 3.95 |
| D | 5 | 5/5 | $0.766 | 6.9 | 1.00 | 1.00 | 1.00 | 1.00 | 4.14 |

### 3.4 읽는 법 — 무엇이 구조 덕이고 무엇이 모델 덕인가

1. **결정적 불변 지표는 A 에서도 거의 만점이다.** 인용 검증률·주장-출처 연결·Gap 근거 2편은 20회 모두 100%. 이는 Critic 이 아니라 **스키마 + 도구 레이어**가 보장하는 것이다 — `Paper` 는 도구 출력 그대로이며 LLM 이 만들지 않고, DOI 없는 문헌은 버리며, 베이스라인도 같은 도구·같은 `post_checks` 를 쓴다 (`report.py` 공유). 즉 "환각 없는 인용"(O2) 은 베이스라인 설계 시점에 이미 구조로 잠갔다.
2. **sub-RQ 커버리지만 조건 간에 갈린다.** A 는 T4 4/5, B 는 T6 5/6 에서 구멍이 났고 C·D 는 10/10 주제 전부 만점. B → C 의 차이가 Critic 결정적 검사(커버리지 미달 sub-RQ 재검색) 하나로 생긴 것이므로, **Reflection/Replanning 이 실제로 결과를 바꾼 증거**는 이 열이다 (goals.md O4). T6 C 는 결정적 검사만으로 Replan 1회를 일으켜 rq5 를 2편 → 충분으로 끌어올렸다 (`events.jsonl` `critique`/`replan` 이벤트).
3. **LLM 비판(D) 은 수치 지표보다 "수치가 못 잡는 미달" 을 잡는다.** T6 D 에서 LLM Critic 은 rq3·rq4 가 편수 기준은 통과하지만 "한국어 논문이 없고 터키어·유럽어 결과로 답하고 있다" 는 major 를 2라운드 연속 냈고, 재검색 뒤에도 안 풀리자 §7 한계에 `[auto]` 로 기록하고 통과시켰다. 이것이 D 의 judge 점수가 가장 높은(4.14, T6 4.29) 이유이자 비용 2.5배의 대가다.
4. **비용·시간**: A $0.19·1.2분 → B/C $0.30~0.33·3분 → D $0.77·6.9분. 전부 goals.md O6 상한(≤ $1, ≤ 10분) 안. D 는 Replan 라운드마다 evaluate 증분 호출이 늘어 호출 수가 19~25회.
5. **judge 는 보조 지표**: 같은 Claude 로 채점하므로 자기 채점 편향이 있다 (plan.md §6.2). 결정적 지표와 모순된 점수(`flags`)는 20회 중 0건. 항목별 평균 (5주제, `eval/rubric.md` §B):

   | cond | J1 주제 이해 | J2 계획 | J3 근거 평가 | J4 종합 깊이 | J5 Gap 타당성 | J6 제안 구체성 | J7 한계 정직성 |
   |---|---|---|---|---|---|---|---|
   | A | 4.0 | 3.6 | 3.0 | 3.2 | 3.6 | 3.8 | 4.0 |
   | B | 4.4 | 4.0 | 3.6 | 3.8 | 3.8 | 4.6 | 4.0 |
   | C | 4.2 | 4.0 | 3.4 | 3.6 | 3.8 | 4.4 | 4.2 |
   | D | 4.2 | 4.0 | 3.4 | 3.8 | 4.2 | 4.8 | 4.6 |

   A → B 의 차이는 J3·J4·J6 (근거 평가·종합·제안) 에서 나는데, 이는 evaluate 노드가 문헌마다 method·sample·finding 을 먼저 적게 하고 gap 노드가 방법·데이터 필드를 강제하는 **스키마의 효과**다. B → D 의 차이는 J5·J7 (Gap 타당성·한계 정직성) 에서만 난다 — LLM Critic 이 "편수는 채웠지만 빗나간 문헌" 을 지적하고 그 미해결이 §7 에 남기 때문. J3 (근거 평가) 는 모든 조건에서 3.0~3.6 으로 가장 낮다 — 초록만 보고 method·sample 을 적어야 하는 ADR-4 의 한계 (§6).

### 3.5 외부 벤치마크의 평가 축과의 대응 (ADR-10)

공개 벤치마크 중 우리 과제(주제 → 착수 브리프, 한국어 입력)를 그대로 재는 것은 없다 — ReportBench·DeepScholar-bench 는 서베이/related-work 생성, DeepResearch Bench 는 웹 리서치 리포트(EN/ZH), ScholarQABench 는 질의응답이다. 그래서 벤치마크를 통째로 돌리는 대신 **평가 축을 빌려** 우리 지표가 어디에 대응하고 무엇이 비어 있었는지 표시한다.

| 외부 축 | 출처 | 우리 지표 | 비고 |
|---|---|---|---|
| Comprehensiveness / Insight / Instruction-following / Readability | DeepResearch Bench **RACE** | J2 계획 완결성 / J4 종합 깊이·J5 Gap / J1 주제 이해 / (요약 가독성은 미측정) | judge 가 같은 축을 5점 척도로 |
| Citation accuracy (인용이 주장을 지지) | DeepResearch Bench **FACT**, ReportBench faithfulness, DeepScholar verifiability | **`citation_support_rate`** (`agent support`, 2026-10-07 추가) | 이전엔 실존 검증(`citation_verified_rate`)만 있었다 — 문헌이 공통으로 지적하는 맹점 |
| Effective citations (주장당 유효 인용) | FACT | **`claim_support_rate`** + `claims_with_source` | |
| Reference coverage (정답 서베이 참고문헌 회수) | ReportBench, SurveyBench, DeepScholar retrieval quality | **`gold_recall.py`** retrieved / evaluated / cited | 결정적, LLM 비용 0 |
| Link validity / 인용 실존 | FACT, "Cited but Not Verified" | `citation_verified_rate` = 100% (도구 레이어가 보장) | 프런티어 모델도 링크 유효 94%+ vs 사실 정확도 39~77% — 둘을 분리해 보고해야 한다 |
| Planning / Retrieval / Reasoning 모듈별 평가 | ADRA-Bank | 노드 단위 결정적 검증(`check()`) + ablation B/C/D | 모듈 분리 구조가 같은 평가 단위 |
| 아이디어 참신성 | IdeaBench, AI Idea Bench 2025 | 미측정 (non-goal) | "미래 논문" 이 정답이라 지식 누출 문제 |

### 3.6 사후 지표 2종 결과 (ADR-10, 2026-10-07)

**정답 서베이 참고문헌 회수율** (`uv run python scripts/gold_recall.py --md --model claude-sonnet-5-5`, 정답 = `eval/gold.yaml` 의 사람 서베이 7편 참고문헌 47~189편):

| cond | n | retrieved | evaluated | cited |
|---|---|---|---|---|
| A | 5 | 0.6% | 0.6% | 0.5% |
| B | 5 | 3.4% | 3.0% | 2.0% |
| C | 5 | 3.4% | 3.0% | 1.8% |
| D | 5 | 3.6% | 3.2% | 1.7% |

읽는 법: (1) 절대값이 낮은 것은 설계상 예상된 결과다 — sub-RQ 당 12편만 선별하고 키워드 검색 상위 15편씩만 보며, 정답 서베이는 방법론·배경 문헌까지 인용한다 (DeepScholar-bench 도 어떤 시스템이든 기하평균 31% 미만). (2) 그래도 두 가지는 분명하다. **베이스라인(A)은 그래프의 1/6** — 검색 횟수 6~10회 vs sub-RQ 6 × 쿼리 4 = 24회 차이가 그대로 회수율 차이다. **D 가 B 보다 retrieved 는 높지만 cited 는 낮다** — Replan 이 후보는 늘리지만 인용은 주제 적합도로 고르므로 정답 서베이 참고문헌과 겹치지 않을 수 있다. (3) 가장 큰 손실은 **검색 단계**(retrieved ≤ 6%)에서 난다: 그래프가 300~400편을 모아도 사람 서베이 참고문헌과 거의 겹치지 않는다. 키워드 검색이 아니라 **인용 그래프 확장**(평가 상위 문헌의 `referenced_works`·`cited_by` 를 따라가는 snowballing)이 다음 개선점이다 — §6.

**주장-근거 지지율** (`agent support`, A·D 조건 10건, judge opus, 합계 $1.64; B·C 는 크레딧을 아껴 생략 — 같은 계획·검색 위에서 synthesize 가 같은 노드라 D 와 다를 이유가 적다). cite = supported 쌍 / 판정 쌍, (lenient) = supported+partial, claim = 지지 문헌 ≥1 인 claim 비율. 초록 없는 문헌 0건, 인용문 대조 실패 0건.

| topic | A cite (lenient) | A claim | D cite (lenient) | D claim |
|---|---|---|---|---|
| T1 | 38% (100%) | 71% | 60% (97%) | 92% |
| T2 | 68% (96%) | 89% | 69% (97%) | 92% |
| T3 | 65% (96%) | 78% | 83% (100%) | 100% |
| T4 | 38% (81%) | 67% | 83% (100%) | 85% |
| T6 | 50% (95%) | 75% | 94% (100%) | 100% |
| **평균** | **52%** (94%) | **76%** | **78%** (99%) | **94%** |

읽는 법: (1) **인용 실존 100% 와 지지율은 다른 지표**라는 문헌의 지적이 우리 데이터에서도 그대로 나온다 — 실존은 양쪽 다 100% 인데 "초록이 그 주장을 직접 뒷받침" 하는 비율은 A 52% · D 78%. (2) 차이의 대부분은 **partial** 에서 난다 (unsupported 는 A 7쌍 / D 2쌍 뿐): 베이스라인은 초록보다 넓은 집단·강한 표현으로 주장을 쓰고, 그래프는 evaluate 노드가 문헌마다 `finding` 을 먼저 적게 한 뒤 synthesize 가 그 필드만 보고 쓰므로 주장이 초록 범위 안에 머문다 — 구조가 보장하는 품질(O7)의 또 한 예. (3) 남은 unsupported 는 "문헌이 X 를 다루지 않는다" 류의 **부재 주장**을 그 문헌에 인용한 경우가 대부분 (예: T4 A c5 "비안내형으로의 일반화 문제" 를 안내형 RCT 2편에 인용) — Gap 성격의 문장이 §4 종합에 섞인 것이라, synthesize 프롬프트에서 부재 주장은 Gap 으로 보내도록 하는 것이 개선점.

## 4. 불변 지표 PASS 여부 (goals.md O2·O7)

| 지표 | 기준 | 결과 (sonnet, 20회) | 판정 |
|---|---|---|---|
| 완주율 | 사람 개입 없이 끝까지 | 20/20 (주제 5개 × 조건 4개) | PASS |
| 인용 검증률 | 100% | 20/20 실행 100% (실행당 인용 수십 편, T6 D 는 93편) | PASS |
| 주장-출처 연결률 | 모든 claim 에 출처 ≥ 1 | 20/20 실행 100% | PASS |
| Gap 당 근거 문헌 ≥ 2 | 100% | 20/20 실행 100% | PASS |
| sub-RQ 커버리지 (evidence ≥ 3) | 최종 구조(D) 100% | D 5/5 주제 100%, C 5/5, B 4/5, A 4/5 | PASS (D 기준) |
| 비용·시간 상한 | ≤ $1 · ≤ 10분 | 최대 $0.825 · 7.5분 (T1 D) | PASS |
| 분야 범용성 (O1) | 서로 다른 분야 5개 이상 | 교육·사회과학, CS, 경영·회계, 의학·보건, NLP | PASS — 단 §6 한계 참고 |
| 주장-근거 지지율 (ADR-10, 보조) | 목표 없음 — 기록 | D claim 94% · cite 78% (A 76% · 52%) | 기록 (§3.6) |
| 정답 서베이 참고문헌 회수율 (ADR-10, 보조) | 목표 없음 — 기록 | D retrieved 3.6% · cited 1.7% (A 0.6% · 0.5%) | 기록 (§3.6) |
| 클린룸 재현 (goals.md L1·L2) | 새 clone + 키 1개 + README 명령 3개로 완주 | 2026-10-08, T1: sonnet $0.811·7.3분 / `--model claude-haiku-4-5` $0.297·7.7분, 둘 다 위 결정적 지표 100% (§4.1) | PASS |

### 4.1 클린룸 재현 (W4 4.3, 2026-10-08)

스크래치 폴더에 `git clone` → `uv sync` → `.env` 에 Anthropic 키만 입력 → README 3단계 명령을 그대로 실행. 도구 캐시가 없는 상태라 검색은 전부 live (OpenAlex 34~35회/실행).

| 모델 | status | cost | min | calls | cite_ok | claim_src | subrq | gaps_ok | critic | replans | LLM Critic 최종 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| claude-sonnet-5-5 (기본) | ok | $0.811 | 7.3 | 26 | 98/98 | 13/13 | 6/6 | 5/5 | 3 | 2 | pass |
| claude-haiku-4-5 (`--model`) | ok | $0.297 | 7.7 | 26 | 95/95 | 12/12 | 6/6 | 5/5 | 3 | 2 | fail → §7 한계 4건 자동 기재 |

읽는 법: 모델을 바꿔도 리포트 구조(7개 섹션)·인용 검증·주장-출처·Gap 근거는 그대로이고, 달라지는 것은 LLM Critic 의 엄격함(Haiku 는 W3 와 같이 "실험 연구 없음" 류를 끝까지 major 로 판정)과 비용뿐이다. 미통과 항목이 리포트에서 사라지지 않고 한계로 남는 것까지가 구조가 보장하는 범위다 (O7).

## 5. 반복 실행 편차 (goals.md O7-L3)

같은 주제 T1 을 **최종 구조(D)로 독립 실행한 7회** — 모델·날짜·네트워크 상태가 다른 조건을 일부러 섞었다 (`uv run python scripts/compare_repeats.py "생성형" --since 20261004T1200`; 계획을 재사용한 B/C 2회는 독립 실행이 아니라 제외).

| run (UTC) | 조건 | 모델 | 비고 | cost | min | calls | cite_ok | claim_src | subrq | gaps_ok | replans | LLM Critic 최종 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 10-04 12:07 | W3 반복 1 | haiku | OpenAlex 소진 → Crossref 폴백 | $0.236 | 6.0 | 24 | 100% | 13/13 | **5/6** | 6/6 | 2 | fail |
| 10-04 12:13 | W3 반복 2 | haiku | Crossref 폴백 | $0.322 | 8.1 | 26 | 100% | 13/13 | 6/6 | 5/5 | 2 | fail |
| 10-04 12:33 | W3 반복 3 | haiku | Crossref 폴백 | $0.320 | 7.5 | 23 | 100% | 10/10 | 6/6 | 7/7 | 1 | fail |
| 10-05 00:00 | ablation D | sonnet | OpenAlex 정상, arXiv 전면 차단 | $0.825 | 7.5 | 25 | 100% | 13/13 | 6/6 | 5/5 | 2 | fail |
| 10-08 02:26 | 클린룸 | sonnet | 새 clone, 캐시 없음 | $0.811 | 7.3 | 26 | 100% | 13/13 | 6/6 | 5/5 | 2 | pass |
| 10-08 02:33 | 클린룸 | haiku | 새 clone | $0.297 | 7.7 | 26 | 100% | 12/12 | 6/6 | 5/5 | 2 | fail |
| 10-08 06:09 | ADR-12 검증 | haiku | OpenAlex 소진 → 48쿼리 전부 Crossref 폴백, evaluate 배치 병렬 4 | $0.405 | 7.1 | 31 | 100% (116/116) | 12/12 | 6/6 | 6/6 | 2 | fail |
| 10-10 14:34 | 웹(research-brief-web) 경유 1회 | sonnet | 워커가 `run_graph` 를 그대로 호출, Supabase 에 이벤트·산출물 업로드, 자동 한국어 번역 포함. OpenAlex 정상(후보 444편) | $0.780 | 5.3 | 24 | 100% (84/84) | 11/11 | 6/6 | 5/5 | 2 | fail |

**불변 지표 (달라지면 안 되는 것)**

| 지표 | 7회 결과 | 판정 |
|---|---|---|
| 완주 | 7/7 | PASS |
| 인용 검증률 100% | 7/7 (실행당 93~116편) | PASS |
| 모든 claim 에 출처 | 7/7 (10~13 claim) | PASS |
| Gap 당 근거 ≥ 2 | 7/7 (5~7 Gap) | PASS |
| 리포트 7개 섹션 | 7/7 | PASS |
| sub-RQ evidence ≥ 3 | 6/7 — 12:07 실행 5/6 | 조건부: 미달 sub-RQ 는 §7 한계에 자동 기재됨. Crossref 폴백 상태(초록 부족)에서만 발생 |

**편차 (달라져도 되는 것)**: 비용 haiku $0.24~0.41 / sonnet $0.81~0.83, 시간 6.0~8.1분, Gap 수 5~7, Replan 1~2.

**ADR-12 검증 실행 (10-08 06:09) 읽는 법**: 진행 표시·evaluate 병렬화·자동 번역 연결을 붙인 뒤 첫 live 실행. (1) evaluate 가 1라운드 7배치를 병렬 4로 0.7분에 끝냈다 (배치당 호출이 순차였다면 ≈ 2분). 전체 7.1분이 클린룸 haiku 7.7분과 비슷한 이유는 이 실행이 Critic 3라운드를 다 돌고(Replan 2) 문헌을 116편 평가해 일이 더 많았기 때문 — 라운드 수가 같은 실행끼리 비교하면 단축 폭이 드러난다. (2) OpenAlex 일일 한도가 소진된 상태라 48개 쿼리 전부 Crossref 폴백 — 초록이 적은 불리한 조건에서도 결정적 지표는 전부 통과. (3) 자동 한국어 번역은 **Anthropic 크레딧 소진(400 credit balance too low)** 으로 실패했고 CLI 가 영어 리포트를 그대로 두고 재시도 명령을 안내했다 — 번역 실패가 완주를 막지 않는 설계가 실제로 작동. 크레딧 충전 뒤 `agent translate` 로 추가. 인용 문헌 집합의 쌍 평균 Jaccard **0.13**, Gap 근거집합 겹침 **0.03** — 계획 노드가 내는 sub-RQ 문구와 쿼리가 실행마다 달라 선택 문헌은 거의 겹치지 않는다. 그럼에도 리포트 구조·검증률·출처 연결은 전부 같다 — "달라지는 것 / 아닌 것" (§2) 표가 실제로 성립함을 보여주는 데이터다.

**모델에 따라 달라지는 것 하나**: LLM Critic 최종 판정. Haiku 는 7회 중 5회 모두 "실험 연구·객관 지표 측정 연구가 없다" 류를 끝까지 major 로 냈고, Sonnet 은 2회 중 1회 통과. 둘 다 결정적 지표는 같으며 차이는 §7 한계에 적히는 `[auto]` 항목 수(0~4건)로만 드러난다. 평가자가 상위 모델로 돌리면 한계 항목이 줄어들 뿐 구조는 같다.

## 6. 한계

**측정·평가 방법의 한계**

- **judge 자기 채점 편향**: 실행(sonnet)과 다른 모델(opus)로 채점하고 근거 인용을 강제했지만 같은 제품군이다. 결정적 지표가 주, judge 는 보조. judge 의 변별력도 낮다 — 조건 간 평균 차 0.5 이내, J3 는 20회 중 대부분 3점.
- **분야 분산 약화**: 2026-10-06 에 T5(경제·공공정책) 를 빼고 T6(NLP) 를 넣어 사회과학은 T1 이 겸하고 T2·T6 은 넓게 보면 둘 다 CS 다 (plan.md §6.1). 경제·법학·인문 주제는 검증하지 못했다.
- **검색 캐시 위 비교**: B/C/D 는 같은 검색 스냅샷을 쓰므로 "검색 변동" 은 통제됐지만 측정되지도 않았다. live 재현은 `--no-cache`. §5 의 독립 반복(캐시 미적중)이 이를 일부 보완한다.
- **반복 횟수**: OpenAlex 일일 한도(검색 ≈ 100회/IP, 그래프 1회 ≈ 35회) 때문에 주제당 반복은 T1 6회뿐이고 나머지 주제는 조건당 1회다. 조건별 평균(§3.3)의 신뢰구간은 넓다.
- **지지 검증도 초록 기준**: `agent support` 는 초록만 보고 판정하므로 본문에만 있는 결과는 partial/unsupported 로 나올 수 있고, 반대로 초록이 과장된 경우를 잡지 못한다. judge 와 같은 자기 채점 편향도 있다 (인용문 verbatim 대조로 일부 완화).
- **정답 서베이 선택의 임의성**: 주제당 1~2편을 OpenAlex 검색 상위에서 골랐다 (`eval/gold.yaml`). 서베이의 범위가 주제보다 넓거나(T6 의 토크나이징 전반 서베이) 좁으면 회수율이 그만큼 왜곡된다. 조건 간 상대 비교로만 쓴다.

**파이프라인의 한계 (다음 개선점 순)**

- **검색 레이어의 회수율이 낮다** (§3.6): 사람 서베이 참고문헌의 ≤ 6% 만 후보에 들어온다. 키워드 검색(OpenAlex 상위 15편 × 쿼리)만 쓰고 인용 그래프를 따라가지 않기 때문. 개선안: evaluate 상위 문헌의 `referenced_works`·`cited_by` 를 한 홉 확장하는 snowballing (OpenAlex 호출 ≈ 편당 1회 → 일일 한도 안에서 sub-RQ 당 3~5편). 파이프라인 변경이라 ablation 재실행이 필요해 이번 제출에선 넣지 않는다.
- **sub-RQ 커버리지는 편수 기준**: T6 D 가 보여주듯 편수는 채워도 언어·대상이 빗나간 문헌일 수 있다. LLM Critic 이 이를 잡지만 결정적 지표에는 반영되지 않는다. 한국어 입력 주제라도 검색은 영어 쿼리라 **한국어 문헌(KCI 등)은 거의 잡히지 않는다** — OpenAlex 의 한국어 색인이 얇고 키 없는 한국어 학술 API 가 없다.
- **초록만 사용 (ADR-4)**: J3(근거 평가) 가 모든 조건에서 가장 낮은 이유. method·sample 을 초록에서 못 읽으면 공란 또는 추정이 된다. Crossref 폴백 상태에선 초록 자체가 적어 커버리지가 더 떨어진다 (§5 12:07 실행).
- **"부재 주장" 이 종합에 섞인다** (§3.6): "문헌이 X 를 다루지 않는다" 류 문장이 §4 종합에 들어가 특정 문헌에 인용되면 unsupported 가 된다. synthesize 프롬프트에서 부재 주장을 Gap 으로 보내는 것이 개선점.
- **Replan 은 쿼리 재작성까지만**: 문헌 자체가 없는 sub-RQ 는 2회 재검색으로도 못 채운다. 구조가 보장하는 것은 "채움" 이 아니라 "솔직한 기재" 다 (§2).
- **Critic 이 작성자와 같은 모델**: synthesize·gap 을 쓴 sonnet 이 critic 도 맡는다. 같은 모델은 맹점을 공유하므로 독립 검토의 효과가 제한된다 — 역할 분리의 이득은 페르소나가 아니라 맥락 격리(digest·JSON 만 읽음)·검증 장치(결정적 5종)에서 나오고, **모델 다양성은 기본값에 없다** (judge 만 opus). 2026-10-16 에 `llm.critic_model`(기본 null = 실행 모델, CLI `--critic-model`) 을 추가하고 **조건 E(Critic 만 opus) 를 T1 에 1회** 돌렸다 — 10-10 D 실행의 계획을 `--plan-from` 으로 재사용, 실행 sonnet, judge·support 는 둘 다 opus:

  | 조건 | run | cost | min | calls | replans | stop_reason | cite_ok | claim_src | subrq | gaps_ok | judge (J1~J7) | cite_sup (strict / lenient) | claim_sup |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|---|
  | D (critic = sonnet) | 10-10 14:34 | $0.780 | 5.3 | 24 | 2 | replan_limit | 100% | 11/11 | 6/6 | 5/5 | **4.00** (4 4 3 4 4 5 4) | 22% / 100% | 36% |
  | E (critic = opus) | 10-16 03:22 | $0.639 (+critic $0.18) | 4.5 | 16 | 1 | replan_budget | 100% | 10/10 | 6/6 | 5/5 | 3.86 (4 4 3 4 4 4 4) | **79%** / 100% | **100%** |

  읽는 법 (n = 1 이라 방향만): (1) 결정적 지표는 둘 다 전부 통과 — 구조가 보장하는 하한은 검토자 모델과 무관하다 (§2 의 주장 그대로). (2) judge 는 0.14 차이로 변별 범위 안이고 J6 하나가 다르다. (3) 지지율 strict 는 79% vs 22% 로 크게 갈리지만 **원인은 검토자가 아니라 claim 의 알갱이**다 — D 10-10 의 claim 11개는 문헌 여러 편의 결과와 유보("all self-reported…")를 한 문장에 묶은 긴 복합문이라 쌍마다 "일부만 지지" = partial(31/40) 로 떨어지고, E 의 claim 10개는 짧아 23/29 가 supported 다. unsupported 는 둘 다 0 (lenient 100%). 즉 `agent support` 의 strict 지표는 **claim 길이에 민감**하다 — 측정 방법의 한계로 위 "지지 검증도 초록 기준" 항목과 함께 봐야 한다. (4) opus Critic 은 1라운드부터 "rq1 생산성은 자기보고뿐" 을 major 로 짚어 sonnet Critic(2라운드에서 같은 지적)보다 한 라운드 빨랐지만, 예산 60% 가드에 걸려 Replan 1회로 끝났다 (critic 호출이 비싸 가드가 일찍 온다). (5) 비교의 교란: E 는 D 의 **최종** 계획(Replan 2회로 덧붙은 쿼리 포함)에서 출발해 1라운드 결정적 검사를 바로 통과했으므로 라운드 수·검색 수는 비교 대상이 아니다. 결론: 이종 검토자는 비용 +$0.07/라운드에 지적이 한 라운드 빨라지는 정도이고, 지표 차이를 주장하려면 주제 5개 × 반복이 필요하다 — 제출 기본값은 그대로(critic_model null), `quality.md` D2 에 실험 설계로 남긴다.
- **주장-근거 지지 검증을 Critic 안에 넣지 않았다** (ADR-10): 사후 지표로만 측정했으므로 실행 중에 partial/unsupported 주장이 걸러지지는 않는다. 실행당 +$0.1~0.2 로 Critic 에 넣을 수 있으나 ablation 재실행이 필요해 보류.
- 위 파이프라인 한계를 포함해 "제품 수준" 기준의 개선 항목 17개(우선순위·설계·확인 방법·제출 전/후 구분)는 [`quality.md`](quality.md) 에 있다. 제출 전에는 지표를 바꾸지 않는 7개만 넣었다 (ADR-12: evaluate 병렬화, 진행 표시, 한국어 주제 자동 번역, 체크포인트·`--resume`, `--exclude/--include`, BibTeX/RIS 내보내기, 캐시 키 정규화).

**재현 환경의 한계**

- OpenAlex 하루 ≈ 100회 한도: 평가자가 같은 IP 에서 주제를 연속으로 3개 이상 돌리면 4번째부터 Crossref 폴백 상태(초록 부족)로 들어간다. 리포트 §7 에 자동 기재되지만 품질은 떨어진다. `.env` 의 `CONTACT_EMAIL` 로 polite pool 에 들어가면 안정적이다.
- arXiv 는 상태가 불안정하다 (10/05 전면 차단). circuit breaker 로 완주는 지키지만 CS 주제의 프리프린트 보강이 빠질 수 있다.
- 모델 deprecation: `config/models.yaml` 의 `model`·`pricing` 만 바꾸면 되지만, 단가표에 없는 모델은 Opus 단가로 보수적으로 집계되어 `max_cost_usd` 에 일찍 걸릴 수 있다.
