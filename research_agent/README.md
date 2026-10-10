# AI Research Agent

연구 주제 한 줄을 넣으면 **주제 이해 → 조사 계획 → 문헌 탐색 → 평가 → 종합 → Research Gap 제안** 6단계를 수행해
연구 착수용 브리프(Research Brief)를 만드는 에이전트입니다. 연세대 DAS6035 *AI에이전트설계및응용* 중간 해커톤 제출물.

**한눈에**

| 항목 | 내용 |
|---|---|
| 입력 | 연구 주제 한 줄 (한국어·영어 모두 가능) |
| 출력 | `report.md` — 요약, 먼저 읽을 문헌 Top 10, 7개 섹션(지침 6단계 + 한계), 품질 카드, 번호 인용 `[n]` + 참고문헌 |
| 필요한 키 | **Anthropic 키 하나.** 문헌 검색은 키 없는 공개 학술 API(OpenAlex·arXiv·Crossref)만 사용 |
| 1회 실행 | ≈ $0.7 · 6~8분 (`claude-sonnet-5-5`, 상한 $1 · 10분) |
| 품질 보장 | 인용 실존 검증 100%, 모든 주장에 출처, Gap 마다 근거 ≥ 2편 — LLM 이 아니라 **코드(스키마·결정적 검사·Critic)가** 보장 |
| 검증 | 주제 5개 × 조건 4개 ablation 20회 완주, 같은 주제 독립 반복 6회, 새 환경 클린룸 2회 — 전부 위 지표 100% ([docs/design.md](docs/design.md)) |

---

## 1. 실행 (3단계)

```bash
# 1. 설치  (uv 가 없으면: curl -LsSf https://astral.sh/uv/install.sh | sh)
uv sync

# 2. 키 설정 — Anthropic 키 하나면 됩니다. 학술 API 는 키가 필요 없습니다.
cp .env.example .env     # ANTHROPIC_API_KEY 입력

# 3. 실행 (최종 구조 = graph 모드가 기본. 1회 ≈ $0.7 + 한국어 번역 $0.12 · 6~8분)
uv run agent run --topic "생성형 AI 활용이 대학원생의 연구 생산성과 연구 품질에 미치는 영향"
```

요구 환경: Python 3.12 (`uv sync` 가 받아줍니다), 인터넷 (Anthropic API + OpenAlex·arXiv·Crossref 공개 API). 추가 키·설치 없음.
실행 중에는 노드 전이·후보/평가 편수·Critic 판정·Replan 쿼리·누적 비용이 한 줄씩 찍히고, 끝나면 결과 폴더와 리포트 경로가 나옵니다.
**`runs/<UTC타임스탬프>_graph_<주제>/report.md` 를 열면 됩니다.**

**리포트 언어**: 파이프라인은 요약만 한국어, 나머지는 영어로 씁니다 (검색 쿼리·초록이 영어라 토큰·검사 측면에서 안전).
주제가 한국어면 실행이 끝난 뒤 **자동으로** 리포트 산문을 한국어로 번역해 `report.md` 는 한국어본, 영어 원문은 `report.en.md` 로 남깁니다
(brief 의 산문 필드만 LLM 1회 ≈ $0.12, `brief.json` 불변. `--lang en` 으로 끄고 `--lang ko` 로 강제).
논문 제목·저자·DOI·검색 쿼리·초록 인용문은 번역하지 않습니다. 번역이 숫자·DOI 를 빠뜨리지 않았는지 코드가 검사하고, 걸린 항목은 영어로 남깁니다.
중간에 끊긴 실행은 `uv run agent run --resume runs/<결과 폴더>` 로 이어갈 수 있습니다 (끝난 검색·평가는 다시 하지 않음).

**바로 볼 수 있는 결과물**: 제출 zip 의 `runs/` 에 실행 결과가 들어 있습니다. 폴더 안에 `cleanroom.json` 이 있는 2개가 새 clone + 새 키로 README 명령을 그대로 돌린 클린룸 실행이고,
`ablation.json` 이 있는 20개가 주제 5개 × 조건 4개 ablation 실행입니다. 전부 `report.md`(한국어본은 번역한 실행만)·`brief.json`·`events.jsonl`·`cost.json` 을 포함합니다.

### 결과 폴더 구성

| 파일 | 내용 |
|---|---|
| `report.md` | **최종 리포트.** 요약 → 먼저 읽을 문헌 Top 10 → §1~§7 → 품질 카드(결정적 지표) → 참고문헌. 한국어 주제면 한국어본 |
| `report.en.md` | (번역한 실행만) 영어 원문 리포트 |
| `brief.json` | 같은 내용의 구조화 데이터 (스키마: `schemas/brief.json`). 영어 — 진실 원천 |
| `brief.ko.json` | (번역한 실행만) 산문 필드의 한국어 사전 + 번역 검사 결과 |
| `events.jsonl` | 모든 LLM 호출·도구 호출·단계 전이 로그 (Planning·Tool Use·RAG·Reflection·Replanning 증거, §3 참고) |
| `cost.json` | 토큰·비용·시간·결정적 품질 지표(`checks`)·Critic/Replan 횟수 |
| `papers.json` | 이번 실행에서 수집한 모든 문헌 (도구 출력 그대로) |
| `state.json` | 노드마다 갱신되는 체크포인트 (`--resume` 용) |
| `topic_frame.json`, `plan.json`, `evidence.json`, `critique_N.json`, `replan_N.json` | 노드별 중간 산출물 |

리포트 7개 섹션은 지침의 Agent 역할 6단계에 1:1 로 대응합니다: §1 주제 재정의(이해) → §2 조사 계획 → §3 Evidence Table(탐색·평가) → §4 종합(합의·상충·조건부) → §5 Research Gap → §6 향후 연구 방향 → §7 한계와 신뢰도.

---

## 2. 구조

### 2.1 파이프라인

```
[Topic]
  │
  ▼
understand ──→ TopicFrame (변수 X·Y, 모집단, 맥락, 영어 동의어)          Planning
  │
  ▼
plan ──→ ResearchPlan (sub-RQ 3~6개 × 검색 쿼리 2~4개)                    Planning
  │
  ▼  ┌─────────────────────────────────────────────────────────────┐
     │ search     OpenAlex(주력) + arXiv(CS 보강) + Crossref(폴백)    │  Tool Use  (LLM 없음)
     │   │        → Paper (도구 출력 그대로, DOI/arXiv id 필수)        │
     │   ▼                                                           │
     │ evaluate   sub-RQ 당 12편 선별 → 관련성·신뢰도·방법·표본·결과   │  RAG
     │   │        → Evidence (실존 검증 안 된 문헌은 제외)             │
     │   ▼                                                           │
     │ synthesize 합의 / 상충(+원인 가설) / 조건부 → Synthesis        │
     │   ▼                                                           │
     │ gap        Gap(근거 ≥ 2) + 제안 RQ·방법·데이터 → GapList        │
     │   ▼                                                           │
     │ critic     결정적 검사 5종 → (통과 시) LLM 비판 → Critique      │  Reflection
     └───┬────────────────────────────────────────────────┬──────────┘
         │ 통과 (또는 Replan 상한 2회·예산 소진)            │ 미달
         ▼                                                ▼
       write ──→ ResearchBrief ──→ report.md          replan ──→ 부족한 sub-RQ 의 새 쿼리 1~3개   Replanning
       (구조는 상태에서 조립,                           (새 후보만 증분 평가)
        LLM 은 요약·한계 문장만)                              └──→ search 로
```

- **모든 노드는 Pydantic 스키마(`schemas.py`)만 주고받습니다.** 각 스키마의 `check()` 가 LLM 없이 도는 결정적 자체 검증이고, 실패하면 이슈를 되먹여 재호출(최대 2회), 그래도 안 되면 `notes` 에 적고 계속 갑니다 — 어떤 노드도 실행을 죽이지 않습니다.
- **문헌은 LLM 이 만들 수 없습니다.** `Paper` 는 검색 도구 출력 그대로이고 DOI/arXiv id 가 없으면 버립니다. 그래서 인용 실존 검증률이 베이스라인에서도 100% 입니다.
- **Critic 이 미달 판정을 내면 Replan** 이 부족한 sub-RQ 에만 새 쿼리를 만들어 search 로 돌아갑니다 (최대 2회). 끝까지 못 채우면 "채움" 대신 **리포트 §7 에 자동 기재**합니다.
- `--mode baseline` 은 같은 도구·같은 렌더러·같은 지표를 쓰는 단일 ReAct 루프(ablation 조건 A) 입니다.

### 2.2 디렉터리

```
research_agent/
├── README.md               ← 이 문서
├── pyproject.toml, uv.lock   의존성 고정 (Python 3.12)
├── .env.example              ANTHROPIC_API_KEY 자리 (+ 선택 CONTACT_EMAIL — OpenAlex polite pool 용, 키 아님)
├── config/models.yaml        모델명·단가·비용/시간 상한·노드 손잡이. 모델 교체는 여기서만
├── prompts/                  노드별 프롬프트 (understand·plan·evaluate·synthesize·gap·critic·replan·write, baseline, judge·support·translate)
├── schemas/brief.json        최종 리포트 JSON Schema (`agent schema` 가 생성)
├── src/research_agent/
│   ├── cli.py                `agent run | judge | support | translate | render | models | schema`
│   ├── graph.py              최종 구조 러너 — 노드 순서 + Critic → Replan 루프 (프레임워크 없이 직접 구현, ≈150줄)
│   ├── baseline.py           베이스라인 단일 ReAct (ablation 조건 A)
│   ├── nodes/                understand · plan · search · evaluate · synthesize · gap · critic · replan · write
│   ├── tools/                openalex · arxiv · crossref · cache (디스크 캐시)
│   ├── schemas.py            모든 노드 입출력 Pydantic 타입 + 결정적 `check()`
│   ├── llm.py                프로젝트의 유일한 LLM 호출 지점 (구조화 출력, 재시도, 토큰·비용 기록)
│   ├── report.py             report.md 렌더러 + 결정적 지표 `post_checks` (베이스라인·그래프 공유)
│   ├── judge.py              LLM-judge (J1~J7) + 주장-근거 지지 검증 (사후 평가)
│   ├── translate.py          리포트 산문 한국어화 (사후, brief.json 불변)
│   ├── export.py             참고문헌 BibTeX/RIS 내보내기 (LLM 없음)
│   ├── progress.py           CLI 진행 표시 (RunLogger 이벤트 구독)
│   └── runlog.py             runs/ 에 events.jsonl · cost.json 기록
├── eval/                     topics.yaml (테스트 주제 5개) · rubric.md (judge 루브릭) · gold.yaml (정답 서베이)
├── scripts/                  run_ablation · summarize_runs · compare_repeats · gold_recall · smoke_tools · smoke_llm
├── tests/                    단위 테스트 97개 (네트워크·API 키 불필요 — HTTP·LLM 모킹)
├── docs/design.md            설계 문서 — 아키텍처, 설계 의도, ablation·반복·클린룸 결과, 한계
├── docs/quality.md           "제품 수준" 기준의 개선 항목 17개 (측정된 결함 → 설계 → 확인, 제출 전/후 구분)
└── runs/                     실행 결과 (제출 zip 에 포함)
```

설계 문서는 상위 폴더에 더 있습니다: [`../goals.md`](../goals.md) (목표 O1~O7·성공 기준·non-goal), [`../plan.md`](../plan.md) (ADR-1~11, 작업 분해, 변경 로그).

---

## 3. 설계 요점과 검증 결과

**원칙 (goals.md O7)**: 품질을 모델의 똑똑함에 맡기지 않고 **파이프라인 구조가 보장**합니다. 평가자가 본인 키와 다른 Claude 모델로 돌리면 문장·선택 문헌은 달라지지만, 아래 오른쪽 열은 달라지지 않습니다.

| 달라져도 되는 것 | 달라지면 안 되는 것 | 보장 장치 |
|---|---|---|
| 문장 표현, 선택된 개별 문헌, Gap 의 구체적 내용 | 리포트 7개 섹션 구조 | write 가 구조를 상태에서 조립, 스키마 검증 통과해야 저장 |
| | 인용 실존 검증률 100% | `Paper` 는 도구 출력 그대로, DOI 없으면 폐기 |
| | 모든 claim 에 출처 ≥ 1, Gap 당 근거 ≥ 2 | 스키마 `check()` 되먹임 + Critic 결정적 검사 |
| Replan 횟수(0~2), 비용($0.3~0.8), 시간(3~8분) | 비용 ≤ $1 · 시간 ≤ 10분 · 완주 | `RunLogger` 상한, 예산 소진 시 Replan 생략 후 write |
| LLM Critic 의 엄격함 | 미달 항목이 리포트에서 사라지지 않음 | Critic 미해결 노트 → §7 `[auto]` 자동 기재 |

**설계평가 증거 (`events.jsonl`)**: Planning = `node_start/node_end`(understand·plan), Tool Use = `tool_call`(openalex·arxiv·crossref), RAG = evaluate 배치 호출(초록을 프롬프트에 넣고 구조화 평가), Reflection = `critique`(round·passed·이슈), Replanning = `replan`(걸린 sub-RQ·새 쿼리) → 다음 라운드 `node_start`.

**Ablation (주제 5개, `claude-sonnet-5-5`, judge `claude-opus-5-5`, 20회 전부 완주)**

| 조건 | 구조 | cost | min | 인용 검증 | claim 출처 | sub-RQ 커버 | Gap 근거 | judge (5점) |
|---|---|---|---|---|---|---|---|---|
| A | 베이스라인 단일 ReAct | $0.185 | 1.2 | 100% | 100% | 0.96 | 100% | 3.60 |
| B | 역할 분리 그래프, Critic 없음 | $0.299 | 2.7 | 100% | 100% | 0.97 | 100% | 4.03 |
| C | 그래프 + 결정적 Critic + Replan | $0.332 | 3.1 | 100% | 100% | 1.00 | 100% | 3.95 |
| **D** | **그래프 + 결정적·LLM Critic + Replan (최종)** | $0.766 | 6.9 | 100% | 100% | 1.00 | 100% | 4.14 |

읽는 법: 인용 검증·출처·Gap 근거는 베이스라인에서도 100% — 도구·스키마 레이어가 보장하는 것. 조건 간 차이는 근거의 폭(평가 문헌 A 23편 vs D 73~87편), sub-RQ 커버리지, judge 점수에서 납니다. 주제 × 조건 전체 매트릭스, 주장-근거 지지율(A 52% vs D 78%), 반복 실행 편차, 클린룸 결과는 [docs/design.md](docs/design.md) §3~§5.

**클린룸 (2026-10-08, 새 clone + 키 1개 + 위 3단계 명령 그대로)**: sonnet $0.811 · 7.3분 · 인용 98/98 · claim 13/13 · sub-RQ 6/6 · Gap 5/5. `--model claude-haiku-4-5` 로도 $0.297 · 7.7분에 같은 지표 100% (LLM Critic 미통과 항목 4건은 §7 에 자동 기재).

---

## 4. 모델·모드·옵션

### 모델 바꾸기

`config/models.yaml` 의 `model` 을 수정하거나 `--model <이름>` 으로 한 번만 덮어씁니다. 계정에서 쓸 수 있는 모델명은 `uv run agent models` 로 확인합니다.

| 용도 | 모델 | 비고 |
|---|---|---|
| 제출·품질 측정 (기본값) | `claude-sonnet-5-5` | 본 문서의 실험 결과(ablation·클린룸)는 모두 이 모델 |
| 개발·디버깅 | `claude-haiku-4-5` | `--model claude-haiku-4-5`. 동작·스키마 통과 확인용, 1회 ≈ $0.3 |
| LLM-judge | `claude-opus-5-5` | 실행 모델과 다르게 두어 자기 채점 편향 완화 |

평가자가 다른 Claude 모델로 재현할 때는 `model` 과 `pricing` 표에 그 모델명을 추가하면 됩니다. `pricing` 에 없는 모델은 `default` 단가(Opus 기준, 보수적)로 비용을 집계합니다.

### 실행 모드·옵션

| 옵션 | 설명 |
|---|---|
| `--mode graph` (기본) | 최종 구조. Critic 미달 시 replan 이 부족한 sub-RQ 만 재검색해 루프 (최대 2회) |
| `--mode baseline` | 단일 ReAct 루프 (ablation 조건 A, 비교 기준점) |
| `--critic none\|deterministic\|full`, `--max-replans N` | 품질 게이트 끄기·줄이기 (ablation 조건 B/C/D) |
| `--no-cache` | 도구 캐시 없이 live 검색 |
| `--until <node>` | 그 노드까지만 실행 (개발·디버깅용) |
| `--plan-from <실행 폴더>` | 그 실행의 `topic_frame.json`·`plan.json` 을 재사용해 understand·plan 을 건너뜀 (조건 비교 시 계획 고정) |
| `--resume <실행 폴더>` | 중단된 실행을 같은 폴더에서 이어감. 끝난 노드는 건너뛰고 비용은 이어받음 (Ctrl-C 로 멈춘 실행도 가능) |
| `--exclude <id,…>` / `--include <doi,…>` | 특정 문헌 제외 / 꼭 평가할 문헌 고정 (DOI). 제외 문헌은 레지스트리에 들어오지 않아 인용될 수 없음 |
| `--lang ko\|en` | 끝난 뒤 한국어 번역 여부. 기본: 주제가 한국어면 ko |
| `--quiet` | 진행 표시 끄기 |

Critic 판정과 Replan 쿼리는 `events.jsonl` 의 `critique` / `replan` 이벤트와 `critique_N.json` / `replan_N.json` 에 남습니다.
속도·비용 손잡이는 `config/models.yaml` 의 `tools.evaluate_workers`(평가 배치 병렬 수, 기본 4), `evaluate_per_subrq`, `graph.max_replans`.

### 재현 환경 주의

- **OpenAlex 는 IP 당 하루 검색 약 100회**로 제한됩니다. 그래프 1회가 약 30~35회를 쓰므로 하루 3회를 넘기면 429 가 납니다.
  이때 파이프라인은 실패한 쿼리만 **Crossref 검색으로 자동 폴백**하고 그 사실을 리포트 §7 에 적습니다. 실행이 멈추지는 않지만 초록이 적어 품질은 떨어집니다.
  `.env` 의 `CONTACT_EMAIL` 을 채우면 polite pool 로 들어가 안정적입니다 (키가 아니라 연락처입니다).
- arXiv 가 불안정한 날(503)에는 circuit breaker 가 arXiv 를 건너뛰고 OpenAlex 만으로 완주합니다. 역시 §7 에 자동 기재.

---

## 5. 평가·개발 명령

```bash
uv run pytest                                    # 단위 테스트 88개 (네트워크·API 키 불필요)
uv run python scripts/smoke_tools.py             # OpenAlex·arXiv·Crossref 실제 호출 확인
uv run python scripts/smoke_llm.py               # Anthropic 구조화 출력 실제 호출 확인 (비용 발생)

uv run agent judge runs/<실행 폴더> | --all       # LLM-judge J1~J7 (eval/rubric.md) → judge.json (opus, 회당 ≈ $0.2)
uv run agent support runs/<실행 폴더> | --all     # 주장-근거 지지 검증: §4 claim 마다 인용 초록이 실제로 뒷받침하는지 → support.json
uv run agent render runs/<실행 폴더> | --all      # brief.json·papers.json·cost.json 으로 report.md 다시 그리기 (LLM·키 불필요)
uv run agent translate runs/<실행 폴더> | --all   # 리포트 산문 한국어화 (LLM 1회 ≈ $0.12) — 한국어 주제 실행은 run 이 이미 했음
uv run agent export runs/<실행 폴더> --format bibtex|ris   # 참고문헌 내보내기 (LLM·키 불필요, 번호는 report.md 와 동일)

uv run python scripts/summarize_runs.py --md                      # runs/ 전체의 결정적 지표·비용·Critic/Replan 횟수 표
uv run python scripts/summarize_runs.py --ablation --md --model claude-sonnet-5-5   # 주제 × 조건(A~D) 매트릭스 + 조건별 평균
uv run python scripts/compare_repeats.py "<주제 slug 일부>" --since <타임스탬프>     # 같은 주제 반복 실행의 불변 지표·편차
uv run python scripts/gold_recall.py --md --model claude-sonnet-5-5                 # 정답 서베이 참고문헌 회수율 (캐시로 계산, 네트워크 불필요)
uv run python scripts/run_ablation.py --topics T1,T2 --conditions D,B,C,A --dry-run # ablation 러너 (계획·OpenAlex 예산만 출력)
```

judge 는 항목마다 리포트 문장을 그대로 인용해야 하며, 결정적 지표(`cost.json` 의 `checks`)와 모순되는 점수는 `judge.json` 의 `flags` 에 표시됩니다.
ablation 러너는 주제마다 D 를 먼저 돌리고 B·C 는 그 계획을 재사용합니다. 시작 전 OpenAlex 잔량을 헤더로 확인하고 부족하면 멈춥니다.
