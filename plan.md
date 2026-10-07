# AI Research Agent — 구현 계획 (plan.md)

- 상위 문서: `goals.md` (O1~O7, 성공 기준). 이 문서는 "어떻게"를 다룸
- 작성일: 2026-10-02 · 상태: **W4 Day 4 완료 (2026-10-07): ablation 주제 5개 × 조건 4개 = 20회 전부 완주 (sonnet, judge opus), `research_agent/docs/design.md` 초안 — §8. 다음은 W4 Day 5 (10/08) 클린룸 재현 + 누출 검사 + config `model` → sonnet (§5 W4 일별 계획)** (`research_agent/README.md` 참고)
- 갱신 규칙: 설계가 바뀌면 §4 ADR에 결정 추가, §8 변경 로그에 날짜와 이유 기록. goals.md는 건드리지 않음

---

## 1. 아키텍처

### 1.1 베이스라인 (W1): 단일 ReAct

```
[Topic] → ReAct loop (LLM + tools: search_openalex, search_arxiv, verify_doi)
         → 최대 15 step → [Research Brief 스키마로 강제 출력]
```

- 목적: O5 ablation의 비교 기준. 이것만으로도 ①~⑥이 "형식상" 채워지는지 확인
- 예상 약점(측정 대상): sub-RQ 커버리지 누락, 인용 검증 생략, 종합 단계 얕음

### 1.2 최종 구조 (W2~W3): 역할 분리 그래프

```
[Topic]
  │
  ▼
① Understand ──→ TopicFrame
  │
  ▼
② Plan ──→ ResearchPlan (sub-RQ 3~6, 쿼리 세트)
  │
  ▼  (sub-RQ별 병렬)
③ Search ──→ 후보 문헌 풀 ──→ ④ Evaluate ──→ EvidenceTable
  │                                             │
  ▼                                             │
⑤ Synthesize ──→ 합의/상충/조건부 매트릭스 ◄────┘
  │
  ▼
  Critic ──(미달)──→ Replan (부족한 sub-RQ만 새 쿼리로 재검색 → 새 후보만 재평가, 최대 2회) ──→ ③
  │ (통과)
  ▼
⑥ Gap & Direction ──→ Writer ──→ ResearchBrief (스키마 검증) ──→ 리포트 + run log
```

| 역할 | 책임 | 호출 모델 | 비고 |
|---|---|---|---|
| Planner | ①②, Replan | 상위 모델 | 전체 1~3회 호출 |
| Searcher | ③ | LLM 없음 (쿼리는 Planner가 생성) | 순수 API 호출 + 캐시 |
| Evaluator | ④ 관련성·신뢰도 점수화 | 상위 모델, 문헌 배치 처리 | 실존 검증은 LLM 없이 Crossref/OpenAlex로 |
| Synthesizer | ⑤ | 상위 모델 | 토큰 최다 소비 지점. 초록만 입력 |
| Critic | 품질 게이트 (O2·O3·L3 체크) | 결정적 검사 + 상위 모델 | 결정적 검사 먼저, 통과 시에만 LLM 비판 |
| Writer | ⑥ + 리포트 조립 | 상위 모델 | 스키마 실패 시 최대 2회 재시도 |

**상태 객체**: 모든 노드는 하나의 `RunState`(Pydantic)를 읽고 쓴다. 노드 간 전달은 전부 스키마 타입. 자유 텍스트는 리포트 본문 필드에만 허용.

---

## 2. 기술 스택

| 영역 | 선택 | 대안 | 선택 이유 |
|---|---|---|---|
| 언어/환경 | Python 3.12, `uv` | poetry, pip | lock 파일 + 단일 명령 설치 (L1) |
| 그래프 실행 | **직접 구현** (노드 = 함수, 상태 = Pydantic, 러너 ~100줄) | LangGraph | §4 ADR-1 |
| LLM | **Anthropic SDK 직접 사용** (Claude 단일 공급자), `llm.py` 하나로 감쌈 | LiteLLM, instructor | §4 ADR-2 |
| 구조화 출력 | tool use로 Pydantic 스키마 강제(`tools=[schema]`, `tool_choice` 고정) + 검증, 실패 시 재시도 | instructor | SDK만으로 가능. 의존성 최소화 |
| 학술 검색 | **OpenAlex**(기본), **arXiv**(CS·물리 보강), **Crossref**(DOI 검증) | Semantic Scholar | §4 ADR-3 |
| 웹 검색 | 없음 (W4에 여유 있으면 Tavily 선택 추가, 키 없으면 자동 비활성) | Tavily, Brave | 키 의존·재현 리스크 (L1) |
| 캐시 | `diskcache` (키: 도구명+정규화 쿼리) | requests-cache | ablation 공정성용. live 실행 시 `--no-cache` |
| 로깅 | `runs/<ts>/` 에 JSONL 이벤트 + 최종 리포트 md + cost.json | LangSmith 등 | 외부 서비스 없이 재현 (L1) |
| 비용 추적 | 응답 `usage` 토큰 × config의 단가표로 집계 | – | O6 상한 자동 체크. 단가는 config에 두어 모델 변경 시 수정 |
| CLI | `typer` | argparse | `agent run --topic ... --model <claude 모델명>` |
| 테스트 | `pytest` (도구 어댑터, 스키마, Critic 결정적 검사) | – | LLM 호출은 녹화 응답으로 |

**비사용 결정**: UI 없음, DB 없음(JSON 파일로 충분), 벡터 DB 없음(문헌 30편 이내는 인메모리 임베딩이면 충분, 그것도 W3에 필요할 때만)

---

## 3. 모듈 명세

### 3.1 디렉터리

```
src/research_agent/
├── llm.py            # Anthropic SDK 래퍼: call(messages, schema, role) → Pydantic. 재시도·비용 기록
├── schemas.py        # TopicFrame, ResearchPlan, Paper, Evidence, Synthesis, Gap, ResearchBrief, RunState
├── tools/
│   ├── openalex.py
│   ├── arxiv.py
│   ├── crossref.py   # verify_doi(doi) → bool + 메타데이터
│   └── cache.py
├── nodes/
│   ├── understand.py
│   ├── plan.py
│   ├── search.py
│   ├── evaluate.py
│   ├── synthesize.py
│   ├── critic.py     # 결정적 5종 + LLM 비판 (ADR-7)
│   ├── replan.py     # Critic 미달 → 걸린 sub-RQ 의 새 쿼리 (W3)
│   ├── gap.py
│   └── write.py
├── graph.py          # 노드 순서·루프 정의, 러너
├── baseline.py       # 단일 ReAct (ablation용)
├── report.py         # 렌더링·사후 지표 (베이스라인·그래프 공용)
├── runlog.py         # runs/ 이벤트 기록
├── judge.py          # LLM-judge (W4): 끝난 실행의 report.md → J1~J7 점수 + 인용. `agent judge` (초안의 eval/judge.py 는 패키지 안으로 옮김)
└── cli.py            # run / judge / models / schema
prompts/<node>.md     # 노드별 시스템 프롬프트 + judge.md. 코드에 문자열 없음
config/models.yaml    # model, judge_model, 단가, max_cost_usd, max_minutes, 노드 상한, graph.critic / max_replans
schemas/brief.json    # ResearchBrief JSON Schema export (문서용)
scripts/              # smoke_tools, smoke_llm, summarize_runs(--ablation), compare_repeats, run_ablation
eval/
├── topics.yaml       # 테스트 주제 5개 (priority 필드 = 중요도)
└── rubric.md         # LLM-judge 루브릭
```

### 3.2 노드 입출력

| 노드 | 입력 | 출력 | 결정적 검증 (Critic 전 자체 체크) |
|---|---|---|---|
| understand | topic: str | `TopicFrame{concepts[], variables{X,Y,population,context}, synonyms_en[], domain}` | 필드 비어있지 않음, synonyms_en ≥ 3 |
| plan | TopicFrame | `ResearchPlan{sub_rqs[3..6]{id, question, queries[2..4], source_pref}}` | sub-RQ 간 쿼리 중복률 < 50% |
| search | ResearchPlan | `papers: list[Paper]` (sub_rq_id 태그) | sub-RQ당 ≥ 10편, DOI 또는 arXiv id 필수 |
| evaluate | papers | `evidence: list[Evidence{paper, relevance 0-5, reliability 0-5, method, sample, finding, verified: bool}]` | verified=False 는 즉시 제외 |
| synthesize | evidence | `Synthesis{consensus[], conflicts[]{claim, sides, hypothesis_for_conflict}, conditional[]}` | 모든 claim에 evidence_id ≥ 1 |
| critic | RunState | `Critique{pass: bool, uncovered_sub_rqs[], weak_claims[], actions[]}` | §3.3 |
| gap | Synthesis, evidence | `gaps[]{description, evidence_ids[≥2], proposed_rq, method, data}` | evidence_ids ≥ 2 |
| write | RunState | `ResearchBrief` (goals.md §5 의 7개 섹션) + 마크다운 | 스키마 통과 |

### 3.3 Critic 품질 게이트 (goals.md O2·O3·L3의 코드화)

| 검사 | 종류 | 실패 시 |
|---|---|---|
| 인용 검증률 = 100% | 결정적 | 미검증 인용 제거 후 재종합 |
| 모든 claim에 출처 ≥ 1 | 결정적 | 출처 없는 claim 삭제 또는 재검색 |
| sub-RQ별 evidence ≥ 3 | 결정적 | 해당 sub-RQ만 Replan |
| Gap당 근거 ≥ 2 | 결정적 | gap 노드 재실행 |
| 상충 결과에 원인 가설 존재 | 결정적 | synthesize 재실행 |
| 종합의 깊이·논리 | LLM 비판 (결정적 5종 통과 시에만, `graph.critic: full`) | major 이슈 → actions 로 Replan 지시 (`search rqN: ...` / `synthesize: ...`) |

Replan 상한 2회(`graph.max_replans`). 상한 도달 시 미달 항목을 리포트 §7 "한계"에 자동 기재하고 종료 (실패로 죽지 않음 — O1). 구현은 ADR-7.

---

## 4. 설계 결정 기록 (ADR)

### ADR-1. 그래프 프레임워크 없이 직접 구현
- 결정: 노드=함수, 상태=Pydantic, 러너 직접 작성
- 대안: LangGraph
- 이유: 설계평가에서 Planning·Reflection·Replanning이 **내 코드에 명시적으로** 보여야 함. LangGraph는 이를 프레임워크 안으로 숨기고, 버전 변동이 잦아 L1 재현 리스크. 파이프라인이 선형+루프 1개라 직접 구현 비용이 낮음
- 재검토 조건: W3에서 병렬·체크포인트 구현이 하루 이상 걸리면 LangGraph로 전환

### ADR-2. Claude 단일 공급자, Anthropic SDK 직접 사용
- 결정: 모든 LLM 호출은 `llm.py` 하나를 통해 Anthropic SDK로. 모델명·temperature·단가는 `config/models.yaml`
- 대안: LiteLLM(다중 공급자 추상화) / instructor
- 이유: 교수님이 제출물에 명시된 공급자(Claude)로 재현하실 것이 확인됨. 추상화 계층은 의존성과 디버깅 지점만 늘림. 모델명 교체는 config로 충분(deprecation 대비)
- 구조화 출력: Pydantic → JSON Schema → tool 정의로 전달, `tool_choice`로 호출 강제. 검증 실패 시 오류 메시지를 붙여 최대 2회 재요청
- 재검토 조건: 교수님이 다른 공급자로 돌리신다는 말이 나오면 LiteLLM 도입 (llm.py 한 파일만 교체되도록 인터페이스 유지)

### ADR-3. OpenAlex를 기본 검색으로, Semantic Scholar 제외
- 이유: OpenAlex는 키 없이 넉넉한 rate limit, 전 분야 커버, DOI·초록 포함 → 교수님 환경에서 추가 키 불필요(L1·L2). Semantic Scholar는 키 없이는 분당 제한이 심해 재현 시 실패 가능
- 보강: CS 주제는 arXiv로 보강. Crossref는 DOI 실존 검증 전용
- 키 정책: **학술 API 키는 어떤 것도 제출물에 포함하지 않음**. 폴라이트 풀용 `mailto` 이메일만 config에. 추후 Semantic Scholar·Tavily 등 키 필요 도구를 넣더라도 선택 도구 + 키 없으면 자동 폴백으로만 허용 (L1 유지)
- 한계(문서에 기재): OpenAlex 초록은 inverted index 형태라 복원 필요. 일부 논문 초록 누락 → 누락 시 Evaluate에서 reliability 감점

### ADR-4. 전문(full text) 미사용
- 이유: goals.md non-goal. 초록+메타데이터로 ①~⑥ 수행 가능, 비용·시간 상한 유지

### ADR-5. 품질은 Critic이 보장, 모델 출력의 운에 의존하지 않음
- 이유: L3. 실행마다 문장·문헌이 달라져도 결정적 검사가 하한을 지킴. LLM 비판은 그 위에서만

### ADR-7. Critic 루프: 결정적 검사 → (통과 시) LLM 비판 → Replan 은 증분 재검색·재평가 (2026-10-04)
- 결정: Critic 은 결정적 5종을 먼저 돌리고, **통과했을 때만** LLM 비판(`prompts/critic.md`, `LLMCritique`)을 부른다. LLM 지적은 major/minor 로 나뉘며 major 가 하나라도 있으면 미통과. 미통과 시 Replan 노드(`prompts/replan.md`, Planner 역할의 2차 호출)가 걸린 sub-RQ 에만 새 쿼리 1~3개를 만들고, search 는 그 쿼리만, evaluate 는 **아직 평가하지 않은 새 후보만** 평가해 기존 Evidence 에 합친다. synthesize·gap 은 직전 Critique 를 프롬프트에 붙여 다시 쓴다. 상한 `graph.max_replans`(기본 2)
- 대안: (a) 매 라운드 전체 재평가 — 토큰 2배, (b) LLM 비판을 항상 실행 — 결정적 실패가 뻔한 상태에 비용 낭비, (c) Replan 이 쿼리 대신 자유 지시문 출력 — search 가 기계적으로 실행할 수 없음
- 이유: 비용 상한(O6) 안에서 루프를 2회까지 돌리려면 증분이어야 한다. Critic 과 Planner 를 분리해 "판정"과 "재계획"이 각각 로그에 남는다(O4). 새 쿼리는 계획의 sub-RQ 에 덧붙여 리포트 §2 에 그대로 드러난다 — 재계획 흔적이 산출물에 보인다
- 미달 노트는 루프 종료 후 **최종 라운드 기준**으로만 남긴다. 중간 라운드에서 걸렸다가 Replan 으로 풀린 항목이 리포트 한계에 남으면 거짓 한계가 된다
- ablation 손잡이: `graph.critic` = none(B) | deterministic(C) | full(D), `graph.max_replans`. CLI `--critic`, `--max-replans`
- **루프 종료 규칙 2개 추가 (같은 날 반복 실행에서 필요해짐)**: (a) 이미 재검색한 sub-RQ 에 같은 `search` major 가 또 나오면 문헌이 없는 것이므로 한계로 기록하고 통과 — T1 에서 "rq2 에 실험 연구가 없다" 가 3라운드 연속 major 로 나와 재검색이 무의미했음. (b) 경과 시간·비용이 상한의 `graph.replan_budget_fraction`(0.6) 을 넘으면 Replan 을 생략하고 write 로 간다. 그래도 상한에 걸리면 `grace_write` 가 마지막 종합으로 브리프를 쓴다(`status=ok_after_limit`) — Replan 2회 뒤 write 직전 10.1분에 걸려 34회 호출을 통째로 잃은 사례
- 재검토 조건: 상위 모델(Sonnet)에서는 호출당 시간이 늘어 Replan 1회로도 10분을 넘길 수 있다. W4 제출 실행 전 `max_minutes` 또는 `replan_budget_fraction` 재조정 → **확인 (2026-10-05)**: sonnet D 실행 T1 7.5분(Replan 2회)·T2 7.1분(Replan 1회)으로 상한 안. 재조정 불필요

### ADR-8. OpenAlex 일일 크레딧 소진 시 Crossref works 검색으로 자동 폴백 (2026-10-04)
- 발견: OpenAlex 가 크레딧 기반 제한을 적용 중 — 응답 헤더 `x-ratelimit-limit: 1000`, 검색 1회 = 10 크레딧, 소진 시 429 + `retry-after` 약 12시간. 즉 **IP 당 하루 검색 약 100회**. 그래프 1회 실행이 sub-RQ 6 × 쿼리 4 + Replan ≈ 30회를 쓰므로 하루 3회 실행이면 막힌다. 반복 실행 측정 도중 3회 연속으로 당했다 (W3 §8). ADR-3 의 "키 없이 넉넉한 rate limit" 전제가 깨짐 — 평가자가 주제 5개를 연속으로 돌리면 3번째부터 실패할 수 있는 L1 리스크
- 결정: search 노드에서 OpenAlex 가 실패한 쿼리(429·5xx·타임아웃)만 **Crossref `works?query.bibliographic`** 로 다시 검색한다. Crossref 는 DOI 등록기관이라 결과가 곧 실존 검증(verified=True), 키 없음, polite pool(mailto) 로 50 req/s. 초록은 일부(스모크에서 15편 중 1~5편)만 있어 Evaluate 가 "no abstract → reliability ≤ 2" 로 감점한다. tool use(베이스라인)에는 노출하지 않는다 — 베이스라인 조건은 그대로 두어 ablation 비교를 흔들지 않는다
- 대안: (a) Semantic Scholar — 키 없이는 공유 풀 100 req/5분이라 더 불안정, (b) OpenAlex API 키 — 키 필요 도구 금지(ADR-3), (c) 실행 간 캐시 재사용 — 계획 쿼리가 실행마다 달라 적중률 낮음
- 기록: 폴백이 일어나면 `openalex_fallback` 이벤트 + notes → 리포트 §7 에 "OpenAlex failed for N/M queries; Crossref fallback answered K" 로 투명하게 남는다
- 재검토 조건: Crossref 폴백 실행의 결정적 지표가 OpenAlex 실행과 다르게 나오면(초록 부족으로 evidence 가 얇아짐) 폴백 시 `evaluate_per_subrq` 를 올리거나 arXiv 쿼리 상한을 늘린다

### ADR-6. OpenAlex 가 모든 sub-RQ 의 주력, arXiv 는 보강 + circuit breaker (2026-10-04)
- 결정: search 노드는 `source_pref` 와 무관하게 모든 쿼리를 OpenAlex 로 보낸다. arXiv 는 arxiv/both 인 sub-RQ 에만 sub-RQ 당 2개 쿼리, 3초 간격, 연속 2회 실패 시 그 실행에서 차단
- 계기: T1·T2 그래프 실행에서 arXiv 가 429·타임아웃으로 28회 연속 실패, search 노드가 5.7~8분 소요 → 10분 상한 위협. OpenAlex 는 arXiv 프리프린트(DOI 10.48550/arxiv.*)도 색인하므로 CS 주제 커버리지 손실이 작음 (T2: arXiv 없이 sub-RQ 당 54~59편)
- 이유: 평가자 환경의 외부 API 상태에 리포트 구조·완주 여부가 흔들리면 안 됨 (O1, O7-L1). 차단 사실은 `notes` → 리포트 §7 한계에 자동 기재되어 투명함
- 재검토 조건: Semantic Scholar 등 키 없는 보조 소스가 필요해지면 같은 breaker 패턴으로 추가

---

### ADR-9. ablation 의 B/C 조건은 D 실행의 TopicFrame·Plan 을 재사용한다 (`--plan-from`, 2026-10-04)

- 결정: 한 주제에서 D(최종 구조)를 먼저 돌려 `topic_frame.json`·`plan.json` 을 만들고, B(critic none)·C(critic deterministic) 는 그 둘을 그대로 읽어 understand·plan 노드를 건너뛴다. 주제 문자열이 다르면 거부.
- 이유: (1) **공정성** — 조건 간 차이가 "계획이 달라서" 가 아니라 "품질 게이트가 달라서" 임을 보장한다. W3 반복 실행에서 계획 쿼리가 실행마다 달라 인용 문헌 Jaccard 가 0.06 이었으므로, 계획을 고정하지 않으면 B/C/D 비교는 검색 변동에 묻힌다. (2) **OpenAlex 예산** — 첫 라운드 쿼리가 완전히 같아 검색 캐시가 그대로 맞고(캐시 키 = 도구명 + 인자, TTL 없음) B 는 OpenAlex 호출 0, C 는 Replan 분만 쓴다. 그래프 1회 ≈ 30회·하루 ≈ 100회 한도에서 주제 5개 × 4조건을 3일로 나눌 수 있다.
- 대안·기각: 조건마다 독립 실행(계획까지 포함한 분산 측정) — 반복 3회 × 4조건 × 5주제 = 60회로 예산·일정 밖. 베이스라인 A 는 계획 노드가 없으므로 재사용 대상이 아니다 (A 의 검색은 모델이 고르는 것 자체가 측정 대상).
- 흔적: `cost.json` 의 `plan_from`, `events.jsonl` 의 `node_reused`, 실행 폴더의 `ablation.json`.

### ADR-10. 외부 벤치마크의 평가 방식을 **사후 지표 2종**으로 들여온다 — 파이프라인은 그대로 (2026-10-07)

- 배경: 공개 벤치마크 조사 (ReportBench, DeepScholar-bench, DeepResearch Bench RACE/FACT, ScholarQABench, ADRA-Bank). 우리 과제(주제 → 착수 브리프)를 그대로 재는 벤치마크는 없고, 한국어 과제도 없다. 다만 공통 지적이 하나 있다: **"인용 링크가 유효하다" 와 "인용이 주장을 뒷받침한다" 는 다른 지표**이고 프런티어 모델도 전자 94%+ · 후자 39~77% 다. 우리 `citation_verified_rate` 100% 는 전자(실존)만 뜻한다.
- 결정: (1) **주장-근거 지지 검증** `agent support` (`judge.support_run`, `prompts/support.md`, 결과 `support.json`): §4 종합의 (claim, 인용 문헌) 쌍마다 그 초록이 주장을 supported / partial / unsupported 로 뒷받침하는지 judge 모델이 판정. 인용문은 초록에서 그대로 베끼게 강제하고 코드가 문자열 대조로 확인 — 못 대면 supported 로 세지 않는다. 지표: `citation_support_rate`(쌍 단위, FACT 의 citation accuracy) · `claim_support_rate`(claim 단위, 지지 문헌 ≥1 — FACT 의 effective citation). (2) **정답 서베이 참고문헌 회수율** `scripts/gold_recall.py` (`eval/gold.yaml`, 캐시 `eval/gold_refs.json`): ReportBench 방식으로 주제별 사람 서베이의 참고문헌을 정답으로 두고 검색(retrieved) → 평가(evaluated) → 인용(cited) 단계별 회수율. 결정적, LLM 비용 0.
- 둘 다 **파이프라인 밖**에 둔다. 이유: W4 ablation 20회가 끝난 뒤라 파이프라인(Critic)에 넣으면 조건 비교를 다시 해야 하고, 지지 판정은 실행 중 비용(+$0.1~0.2)보다 사후 측정이 싸다. Critic 에 넣는 것은 §7 열린 질문으로 남긴다.
- 대안·기각: 벤치마크 전체 실행(DeepResearch Bench 100과제·ScholarQABench 2,967질의) — 언어·비용·OpenAlex 한도 밖. 아이디어 참신성 벤치마크(IdeaBench 등) — "미래 논문" 이 정답이라 지식 누출 문제, non-goal. gpt-researcher·STORM 등과 직접 비교 — 웹 검색 키 전제(ADR-3 충돌)이고 검색 소스가 달라 공정 비교 불가.
- 흔적: `support.json`·`support_events.jsonl`(실행 폴더), `summarize_runs.py --ablation` 의 `cite_sup`·`claim_sup` 열, `gold_recall.py` 표. 비용·호출은 judge 와 같이 원 `cost.json` 에 섞지 않는다.

## 5. 작업 분해

### W1 (10/2–10/8) — 기반 + 베이스라인

| # | 태스크 | 산출물 | DoD |
|---|---|---|---|
| 1.1 | 저장소 골격, `uv init`, config, `.env.example` | repo | `uv sync` 후 `agent --help` 동작 |
| 1.2 | `schemas.py` 전체 정의 | 스키마 | JSON Schema export 성공 |
| 1.3 | `llm.py` + tool use 기반 스키마 출력 스모크 테스트 | llm.py | TopicFrame 반환, 검증 실패 재시도 동작 |
| 1.4 | OpenAlex·arXiv·Crossref 도구 + 캐시 | tools/ | 단위 테스트 통과, 예시 주제로 30편 수집 |
| 1.5 | 베이스라인 ReAct | baseline.py | 주제 5개 완주, runs/ 기록 |
| 1.6 | 테스트 주제 5개 + 루브릭 확정 | eval/ | §6 |
| 1.7 | README·design.md에 재현성 설계 포인트 기재: "키가 필요 없는 공개 학술 API(OpenAlex·arXiv·Crossref)만 사용 → 평가자는 Anthropic 키 하나로 재현" | 문서 | – |

### W2 (10/9–10/15) — 노드 구현 + 품질 게이트

| # | 태스크 | DoD |
|---|---|---|
| 2.1 | understand, plan 노드 | 주제 5개 TopicFrame·Plan 결정적 검증 통과 |
| 2.2 | search(병렬), evaluate 노드 | sub-RQ당 ≥10편, 검증률 100% |
| 2.3 | synthesize, gap, write 노드 | 스키마 통과율 100% |
| 2.4 | Critic 결정적 검사 6종 | 단위 테스트 |
| 2.5 | graph.py 러너, end-to-end 1회 | 예시 주제 완주 |

### W3 (10/16–10/22) — 루프 + 반복 안정성

| # | 태스크 | DoD |
|---|---|---|
| 3.1 | Critic LLM 비판 + Replan 루프 (ADR-7) | 최소 1개 주제에서 Replan이 결과를 바꿈 (로그로 증명) — §8 2026-10-04 W3 항목 |
| 3.2 | **같은 주제 3회 반복 실행, 편차 측정** (`scripts/compare_repeats.py`) | 결정적 지표 전부 100% 유지. Gap 겹침 비율·비용 편차 기록 — §8 |
| 3.3 | 프롬프트 다듬기 | 불안정 노드(스키마 재시도 잦은 곳) 우선 — replan 프롬프트·결정적 검사 보강 (§8) |
| 3.4 | MCP 적용 여부 결정 | 잠정 미적용 (§7). 7주차 수업 후 최종 |

### W4 (당초 10/23–10/29, 실제 10/04 착수) — 실험 + 클린룸

| # | 태스크 | DoD |
|---|---|---|
| 4.1 | ablation: 조건 A~D × 주제 5개 (T1~T4, T6) (`scripts/run_ablation.py`, ADR-9) | 매트릭스 (품질 지표, 비용, 시간) — `summarize_runs.py --ablation --md` |
| 4.2 | LLM-judge 채점 (`agent judge`, `judge.py`, `prompts/judge.md`) | rubric 점수표 — 실행 폴더마다 `judge.json` |
| 4.3 | **클린룸**: 새 컨테이너/Colab, 새 키, README만으로 L1~L3. 다른 Claude 모델명으로도 1회 | 체크리스트 전부 통과 |
| 4.4 | 키·경로 누출 검사, zip 용량 확인 (1GB 한도, 예상 100MB 미만). **config `model` 을 개발용 haiku → 제출용 sonnet-5-5 로 교체했는지 확인** | – |
| 4.5 | (선택) judge 가 지적한 결정적 검사 2종 추가 검토: 프리프린트 중복 레코드(zenodo·techrxiv·SSRN 같은 제목) 병합, 같은 문헌이 상충 A·B 양측에 인용되면 Critic 미통과 | 단위 테스트. 시간 남을 때만 |

**일별 계획 (OpenAlex 하루 ≈ 100회 검색이 병목. 추정: D 36회 · C 12회 · B 0회(계획 재사용) · A 10회 → 주제당 58회).**
실행 모델은 sonnet-5-5 (품질 측정용, §8 2026-10-04 모델 운용), judge 는 opus-5-5. 예상 비용: 실행 20회 ≈ $8, judge 20회 × $0.2 ≈ $4, 합계 ≈ $12 (크레딧 $20 중 10/04 까지 $3.2 사용).

| Day | 날짜 | 작업 | OpenAlex | 끝났을 때 |
|---|---|---|---|---|
| 1 | 10/04 (일) | **4.2 judge + 4.1 인프라** — `judge.py`·`prompts/judge.md`·`agent judge`, graph `--plan-from`(ADR-9), `run_ablation.py`(예산 가드·dry-run·완료 조합 건너뛰기), `summarize_runs.py --ablation`. 단위 테스트 51 → 60. judge 실전 1회 (T1 D, Opus: 평균 3.57, 인용 7/7 원문 일치, $0.195, 34초) | 0 | ✅ 완료 |
| 2 | 10/05 (월) | ablation 1차: `run_ablation.py --topics T1,T2 --conditions D,B,C --model claude-sonnet-5-5 --judge --wait`. 6회 전부 완주, 결정적 불변 지표 6/6 통과, OpenAlex 실제 57회 (추정 96회보다 적음 — B/C 는 캐시 적중 0회, C 는 Replan 0회). 비용 $2.74 + judge $0.81 | 57 | ✅ 완료 (§8 2026-10-05) |
| 3 | 10/06 (화) | ablation 2차: T3, T4 × D,B,C + (당겨서) A × T1~T4. 실측 OpenAlex: D 26·30회, B/C 캐시 적중으로 0회, A 주제당 1~6회 → 하루 합계 ≈ 85회. T5 A 는 잔량 9회 < 추정 10회라 러너 예산 가드가 설계대로 중단. 하네스 결함 2건 수정 (§8 2026-10-06) | 85 | ✅ 완료 — 4주제 D/B/C + A 4주제 |
| 4 | 10/07 (수) | ablation 3차: T6 × D,B,C,A — 4회 전부 완주, `docs/design.md` 초안 (§3 매트릭스 20회 + 조건별 평균, §4 불변 지표 PASS 표). 비용 실행 $1.63 + judge $0.47 | 58 (추정) | ✅ **4.1·4.2 DoD** (§8 2026-10-07) |
| 5 | 10/08 (목) | **4.3 클린룸**: 임시 폴더에 `git clone` → 새 `.env` → README 3단계만으로 1회 완주(sonnet), `--model claude-haiku-4-5` 로 1회. **4.4**: `git grep -n "sk-ant\|/Users/"` 누출 검사, `git archive` zip 용량, config `model` → sonnet-5-5, README 최종 | ≈ 72 | 체크리스트 통과 |
| 4+ | 10/07 (수) | (당겨서) **ADR-10 사후 지표 2종**: `agent support` 구현 + A·D 10건 검증, `gold_recall.py` + `eval/gold.yaml` 정답 서베이 7편, design.md §3.5 외부 벤치마크 대응 | 13 (정답 참고문헌 캐시) | ✅ (§8 2026-10-07) |
| 6 | 10/09 (금) | (선택) D 조건 sonnet 반복 3회 (T1) → `compare_repeats.py` 로 L3 불변 지표 재확인. 4.5 검토 | ≈ 108 → 하루 전부 | 반복 편차 표 (sonnet) |
| – | 10/10~ | 마무리 5.1·5.2 (design.md, README) | 0 | 제출 |

OpenAlex 가 429 로 Crossref 폴백 상태에 들어가면 그날 ablation 은 중단한다 (폴백 상태는 초록이 적어 조건 비교가 오염됨). `run_ablation.py` 는 추정 누적이 예산을 넘기는 실행 앞에서 스스로 멈추고, 다음 날 같은 명령을 다시 돌리면 끝난 조합은 건너뛴다. 예산을 더 쓰려면 다른 네트워크(IP)에서 돌린다.

### 마무리 (10/30–11/2)

| # | 태스크 |
|---|---|
| 5.1 | `docs/design.md` = goals + plan + 실험 결과 + "달라지는 것/아닌 것" 표 + 한계 |
| 5.2 | README 최종, 제출 |

---

## 6. 테스트·평가 계획

### 6.1 테스트 주제 (5개, 분야 분산)

| id | 분야 | 주제 | 선정 이유 |
|---|---|---|---|
| T1 | 교육·사회과학 | 생성형 AI 활용이 대학원생의 연구 생산성과 연구 품질에 미치는 영향 | 지침 예시 (기준점) |
| T2 | CS | LLM 에이전트의 장기 메모리 설계가 멀티스텝 과업 성공률에 미치는 영향 | arXiv 비중 높음, 수업 연계 |
| T3 | 경영·회계 | AI 기반 이상거래 탐지가 외부감사 품질과 감사 비용에 미치는 영향 | 본인 도메인 → 품질 판단 가능 |
| T4 | 의학·보건 | 디지털 치료제의 우울증 증상 완화 효과와 지속성 | 임상 문헌 — 방법론 필드(RCT 등) 테스트 |
| T6 | NLP·전산언어학 | 한국어 토크나이징 방법 개선 | 본인 연구 관심 주제. "X 가 Y 에 미치는 영향" 꼴이 아닌 짧고 열린 주제 → understand 노드의 범위 설정 테스트 |

한·영 둘 다 1회씩 돌려 언어 민감도 확인. ablation 은 한국어 입력(`--lang ko` 기본)으로 돈다.

**우선순위**: T1 (기준점) → T6 → 나머지. `eval/topics.yaml` 의 `priority` 필드에 적고, `run_ablation.py` 는 `--topics` 가 없으면 이 순서로 돈다. id 는 재번호하지 않는다 — `runs/*/ablation.json` 의 `topic_id` 와 §8 의 결과 표가 기존 id 를 가리키고 있기 때문.

**2026-10-06 주제 교체**: T6 추가, T5 (공공정책 — 전기차 보조금 정책이 중고차 시장 가격에 미치는 영향, 한국어만) 삭제 → T5 는 결번. T6 은 추가 시점 이후 실행(W4 Day 4 ablation, 클린룸·제출 실행)에만 적용하고, 이미 끝난 단계(W1 베이스라인 5주제 완주, W2·W3 검증)는 T6 으로 다시 돌리지 않는다. §8 의 과거 기록에 남은 T5 언급은 당시 기록 그대로 둔다.

분야 분포 (goals.md O1): 교육·사회과학(T1), CS(T2), 경영(T3), 의학(T4), NLP(T6). 사회과학 전용 주제였던 T5 가 빠져 사회과학은 T1 이 겸하고, T2·T6 은 둘 다 넓게 보면 CS 다 — design.md 한계에 적을 것.

### 6.2 지표

| 지표 | 계산 | 종류 |
|---|---|---|
| 완주율 | 완주 / 실행 | 결정적 |
| 인용 검증률 | 검증 인용 / 전체 인용 | 결정적 |
| 주장-출처 연결률 | 출처 있는 claim / 전체 claim | 결정적 |
| sub-RQ 커버리지 | evidence ≥3 인 sub-RQ / 전체 sub-RQ | 결정적 |
| 스키마 통과율 | 1차 통과 / 시도 | 결정적 |
| 비용·시간 | cost.json | 결정적 |
| 종합 깊이, Gap 타당성, 제안 구체성 | LLM-judge 1~5점, 루브릭 `eval/rubric.md` | LLM |
| 주장-근거 지지율 (ADR-10) | `agent support`: (claim, 인용 초록) 쌍 단위 supported / claim 단위 지지 문헌 ≥1. 인용문 verbatim 강제 | LLM + 결정적 대조 |
| 정답 서베이 참고문헌 회수율 (ADR-10) | `scripts/gold_recall.py`: 사람 서베이 참고문헌 ∩ {retrieved, evaluated, cited} / 참고문헌 | 결정적 |

LLM-judge도 Claude로 채점하므로 자기 채점 편향이 있음. 완화: 실행과 **다른 모델명** 사용, 루브릭을 항목별 근거 인용 필수로 작성, 결정적 지표를 주 지표로 두고 judge 점수는 보조로만 해석. 이 한계는 design.md에 명시.

### 6.3 ablation 설계

| 조건 | 설명 |
|---|---|
| A | 베이스라인 ReAct |
| B | 그래프, Critic 없음 |
| C | 그래프 + Critic 결정적 검사만 |
| D | 그래프 + Critic 전체 + Replan (최종) |

같은 검색 캐시 위에서 실행해 검색 변동을 통제. 주제 5개 × 조건 4개 = 20회 (+ D 조건 반복 3회 = 10회 추가). 비용 상한 고려해 A·D는 전수, B·C는 주제 2개로 축소 가능.

**실행 방식 확정 (2026-10-04~05, ADR-9):** 주제마다 D 를 먼저 돌려 계획을 만들고 B·C 는 `--plan-from` 으로 같은 TopicFrame·Plan 에서 출발 → 첫 라운드 검색이 동일(캐시 적중, OpenAlex 호출 0). 실행 모델 sonnet-5-5, judge opus-5-5. OpenAlex 일일 한도 때문에 3일로 분할 (§5 W4 일별 계획). Day 2 실측으로 sonnet 비용이 D $0.66~0.83 · B/C $0.31 이라 B·C 도 전수 가능 (총 ≈ $14.4). 진행 결과는 §8, 매트릭스는 `scripts/summarize_runs.py --ablation --md`.

---

## 7. 열린 질문

| 질문 | 확인 대상 | 기한 |
|---|---|---|
| MCP 적용 여부 | **잠정 결정(2026-10-04): 미적용.** 도구 3개가 이미 `TOOL_DEFS` 로 tool use 에 노출되어 있어 MCP 서버로 감싸도 기능은 같고, 평가자 환경에 MCP 서버 프로세스 하나가 추가되어 L1 재현 리스크만 늘어남. 7주차 수업에서 설계평가 가산이 명시되면 `tools/` 하나를 MCP 서버로 노출하는 선택 모드로 재검토 (Jay 확인 필요) | W3 → 보류 |
| 웹 검색 추가 여부 | **결정(2026-10-05): 미적용.** W4 는 ablation·클린룸에 예산(크레딧·OpenAlex 일일 한도)을 다 쓰고, 키 의존 도구는 L1 재현 리스크 (ADR-3 과 같은 이유) | 종결 |

---

## 8. 변경 로그

| 날짜 | 변경 | 이유 |
|---|---|---|
| 2026-10-02 | 초안. ADR-1~5, W1~W4 작업 분해, 테스트 주제 5개 | goals.md 확정 후 W1 설계 |
| 2026-10-02 | 제출 용량 1GB 확인 → 열린 질문에서 제거 | 사용자 확인 |
| 2026-10-02 | 학술 API 키 미포함 정책 확정, 교수님 확인 사항 0건 | 키 없는 공개 API만으로 충분. 키 업로드는 약관·유출·재현성 리스크 |
| 2026-10-02 | **W1 1.1~1.7 코드 작성 완료** (`research_agent/`). 단위 테스트 15개 통과. 실제 API 스모크(`scripts/smoke_*.py`)는 Jay 맥에서 실행 대기 | 클라우드·샌드박스 모두 학술 API·Anthropic 네트워크 차단 |
| 2026-10-02 | ADR-2 보완: Anthropic SDK 1.11 의 `messages.parse(output_format=PydanticModel)` 네이티브 구조화 출력 사용. tool use 강제는 베이스라인 최종 제출(`submit_brief`)에만. SDK 가 `temperature` 파라미터를 받지 않아 config 에서 제거 | SDK 확인 |
| 2026-10-02 | 공급자 전환(OpenAI↔Claude) 요구 제거. LiteLLM → Anthropic SDK 직접. 교차 테스트 → 반복 실행 편차 측정 | 교수님이 제출물의 공급자(Claude)로 재현하심을 확인 |
| 2026-10-04 | 모델 운용 2단계화: 개발(W2~W3 구현·디버깅)은 `claude-haiku-4-5`, 품질 측정·제출 run 은 `claude-sonnet-5-5`, judge 는 `claude-opus-5-5`. config 단가표를 현행 모델로 갱신 (sonnet-4-5·opus-4-1 제거) | API 크레딧 $20 로 시작. 동작 확인 단계에서 상위 모델은 낭비. 제출 전 config 의 `model` 을 sonnet-5-5 로 교체하는 것을 W4 체크리스트(4.4)에 포함 |
| 2026-10-07 | **ADR-10: 외부 벤치마크 조사 → 사후 지표 2종 추가.** (1) `agent support` (`judge.support_run`, `prompts/support.md`, `SupportResult.check` 가 인용문 verbatim 대조): A·D 10건 검증 $1.64 — 쌍 단위 supported A 52% / D 78% (lenient 94% / 99%), claim 단위 76% / 94%. 실존 검증 100% 와 지지율이 다르다는 문헌 지적이 그대로 재현됨; 차이는 대부분 partial(베이스라인이 초록보다 넓게 주장), unsupported 는 A 7쌍·D 2쌍이고 대부분 "부재 주장" 을 문헌에 인용한 경우. (2) `scripts/gold_recall.py` + `eval/gold.yaml`(정답 서베이 7편) + 캐시 `eval/gold_refs.json`(OpenAlex 13회, 평가자는 네트워크 불필요): 회수율 retrieved A 0.6% / B·C 3.4% / D 3.6%, cited 0.5~2.0% — 검색 레이어가 사람 서베이 참고문헌을 거의 못 건짐 → snowballing 이 다음 개선점 (design.md §6). `summarize_runs.py --ablation` 에 `cite_sup`·`claim_sup` 열, design.md §3.5(RACE/FACT/ReportBench 축 대응)·§3.6·§4·§6, rubric §A. 단위 테스트 62 → 71. 크레딧 누적 ≈ $15.2 / $20 | 벤치마크 조사 결과 우리 과제를 그대로 재는 공개 벤치마크는 없지만, "링크 유효 ≠ 주장 지지" 는 공통 지적이라 지표를 분리해 보고해야 설득력이 있음. 파이프라인은 ablation 20회가 끝난 뒤라 건드리지 않고 사후 지표로만 (ADR-10) |
| 2026-10-07 | **W4 Day 4 완료: ablation 3차 T6 × D/B/C/A (sonnet-5-5, judge opus-5-5) → 매트릭스 20회 완성, `docs/design.md` 초안.** 4회 전부 완주: D $0.765·6.7분·Replan 2, B $0.279·2.4분, C $0.421·3.7분·Replan 1, A $0.163·1.1분. judge D 4.29 (전 실행 중 최고) · B 4.14 · C 3.86 · A 3.71, flags 0. 조건별 평균 (5주제): A $0.185·1.2분·subrq 0.96·judge 3.60 / B $0.299·2.7분·0.97·4.03 / C $0.332·3.1분·1.00·3.95 / D $0.766·6.9분·1.00·4.14. 결정적 불변 지표(인용 검증·주장-출처·Gap 근거 2편) 는 A 포함 20/20 100% — 도구·스키마 레이어가 보장. 조건 간 차이는 sub-RQ 커버리지에만 남음 (A T4 4/5, B T6 5/6, C·D 전부 만점). **T6 에서 처음으로 C(결정적 검사만) 가 Replan 을 일으킴**: rq5 2편 → 재검색 → 통과. D 는 LLM Critic 이 "편수는 채웠지만 한국어 논문이 아니라 터키어·유럽어 결과" 라는 major 를 rq3·rq4 에 2라운드 연속 내고 재검색 뒤에도 안 풀려 §7 한계 `[auto]` 로 기록 — 짧고 열린 주제를 넣은 목적(범위 설정 검증)대로 동작. OpenAlex 실측: 시작 잔량 99회, 추정 58. 크레딧 누적 ≈ $13.5 / $20 | 4.1·4.2 DoD. design.md 는 §3·§4 만 채운 초안 — §1·2·5·6 은 5.1 에서 |
| 2026-10-06 | **테스트 주제 교체: T6 "한국어 토크나이징 방법 개선" (NLP) 추가 · 우선순위 2 (T1 다음), T5 "전기차 보조금 정책이 중고차 시장 가격에 미치는 영향" 삭제.** 주제 수는 5개 유지 (T1~T4, T6), id 는 재번호하지 않고 T5 는 결번 (§6.1). `eval/topics.yaml` 에 `priority` 필드 도입, `run_ablation.py` 의 `--topics` 기본값을 하드코딩(T1~T5)에서 "yaml 전체, priority 순" 으로 변경. W4 Day 4 (10/07) 의 ablation 대상을 T5 → T6 으로 교체, 나머지 일정은 그대로. T6 은 앞으로의 실행에만 적용 — 끝난 단계를 T6 으로 다시 돌리지 않는다. `runs/` 의 T5 실행 폴더(haiku 2건)는 지우지 않음 | 사용자 요청. T6: 본인 연구 관심 주제라 품질을 직접 판단할 수 있고, 기존 주제가 모두 "X 가 Y 에 미치는 영향" 꼴이라 짧고 열린 주제의 범위 설정을 볼 필요. T5 를 고른 이유: (1) sonnet ablation 을 아직 한 번도 안 돌려 버리는 결과가 없다 (T2~T4 는 4조건 완주), (2) 고유 목적이던 "한국어 입력 → 영어 쿼리 확장" 은 ablation 전체가 한국어 입력이라 이미 모든 주제에서 확인된다, (3) 크레딧 $20 중 $11.4 사용 (runs $9.27 + judge $2.17) — T5·T6 을 둘 다 돌리면 ≈ $4.8 로 클린룸·반복 실행 여유가 거의 없다. 대가: 경제·공공정책 분야가 빠진다 (§6.1 분야 분포) |
| 2026-10-06 | **W4 Day 3 완료: ablation 2차 (T3·T4 × D/B/C) + A 조건 당겨 실행 (T1~T4), 전부 sonnet-5-5, judge opus-5-5.** 10회 전부 완주, 결정적 불변 지표 그래프 8/8 통과. 결과 (sonnet 만, `summarize_runs.py --ablation --md --model claude-sonnet-5-5`):<br>`| topic | cond | cost | min | calls | cite_ok | claim_src | subrq | gaps_ok | replans | judge |`<br>`| T3 | D | $0.815 | 6.8 | 24 | 100% | 9/9 | 5/5 | 5/5 | 2 | 4.14 |`<br>`| T3 | B | $0.264 | 2.1 | 9 | 100% | 11/11 | 5/5 | 5/5 | 0 | 4.00 |`<br>`| T3 | C | $0.273 | 2.2 | 9 | 100% | 11/11 | 5/5 | 5/5 | 0 | 3.86 |`<br>`| T4 | D | $0.761 | 6.3 | 21 | 100% | 13/13 | 6/6 | 5/5 | 1 | 4.14 |`<br>`| T4 | B | $0.327 | 2.3 | 10 | 100% | 10/10 | 6/6 | 5/5 | 0 | 3.71 |`<br>`| T4 | C | $0.342 | 2.4 | 10 | 100% | 12/12 | 6/6 | 5/5 | 0 | 3.86 |`<br>`| T1 | A | $0.156 | 1.0 | 3 | 100% | 7/7 | 5/5 | 4/4 | - | 3.86 |`<br>`| T2 | A | $0.262 | 1.7 | 4 | 100% | 9/9 | 6/6 | 3/3 | - | 3.43 |`<br>`| T3 | A | $0.169 | 1.2 | 3 | 100% | 9/9 | 5/5 | 4/4 | - | 3.57 |`<br>`| T4 | A | $0.176 | 1.2 | 3 | 100% | 6/6 | 4/5 | 4/4 | - | 3.43 |`<br>**조건별 평균 (주제 4개, sonnet): A $0.19 · 1.3분 · judge 3.57 (subrq 0.95) / B $0.31 · 2.8분 · 4.00 / C $0.31 · 3.0분 · 3.97 / D $0.77 · 6.9분 · 4.10.** 관찰 (design.md 용): (1) **A→B 가 가장 큰 차이** — judge +0.43 (4주제 모두 A < B/C/D), 평가 문헌 A 23~25편 vs B/C 56~63편 vs D 73~87편, claim 6~8 vs 9~11, Gap 3~4 vs 5, sub-RQ 커버리지는 A 만 미달 1건(T4 4/5). 베이스라인도 결정적 지표(인용 검증·출처)는 100% 인데 이는 도구가 `Paper` 를 만들고 LLM 은 id 만 고르는 설계(ADR-3)를 양쪽이 공유하기 때문 — 차이는 "근거의 폭과 구조" 에서 난다. (2) B→C→D 는 Day 2 와 같은 패턴: 결정적 5종은 1라운드 통과(C 는 Replan 0), D 만 LLM 비판이 major 를 내 Replan 1~2회, 비용 2.5배에 judge +0.1. T3 D 는 rq3(감사 저널엔트리 수준 정확도) 문헌 부재를 2회 재검색 후 한계로 기재 — "채움" 이 아니라 "솔직한 기재" 를 보장. (3) judge 가 하네스 결함 2건을 잡아냄 → 즉시 수정: ① T3 D synthesize 출력의 `coverage_note` 끝에 `}</br>Correction: the JSON above must be a single object...{` 생성 잔해가 섞여 §4 에 노출(J4 3점). 스키마 파싱은 통과하므로 `nodes.residue_issues()` 를 `checked_call` 공통 검사에 추가(문자열 필드의 괄호·`<br>`·코드펜스 잔해 → 되먹여 재호출). 기존 산출물 142개 검사에 오탐 0. ② critic 의 "persist after re-search" 한계 노트가 `problem[:160]` 로 잘려 §7 `[auto]` 항목이 문장 중간에서 끊김(J7 지적) → 자르지 않음. 단위 테스트 60 → 62. (4) OpenAlex 실측: D 첫 라운드 20~24 + Replan 라운드당 3~6, B/C 는 캐시 적중 100%(0회), A 1~6회. 오늘 합계 ≈ 85회로 하루 예산 안. 러너의 사전 점검이 T5 A 앞에서 잔량 9회 < 추정 10회로 중단 — 가드 작동 확인. (5) 오늘 arXiv 정상 응답(Day 2 는 전 실행 차단) — T3 D 는 arXiv 6회 호출. (6) `summarize_runs.py --ablation --model` 필터 추가 — 조건별 평균에 개발용 haiku 실행이 섞이지 않게. 비용: 오늘 실행 $3.54 + judge $1.17, 누적 $11.45 (크레딧 $20) | 남은 계획: T5 × D/B/C/A (추정 58회, ≈ $1.4 + judge $0.6) → 4.1·4.2 DoD. 4.4 사전 점검 완료: `git grep "sk-ant\|/Users/"` 누출 0건(.env.example 자리표시자뿐), `git archive` 177KB |
| 2026-10-05 | **W4 Day 2 완료: ablation 1차 (T1·T2 × B/C/D, sonnet-5-5, judge opus-5-5).** 러너에 OpenAlex 잔량 사전 점검(`x-ratelimit-remaining` 헤더, 일일 리셋 00:00 UTC)과 `--wait` 추가. 결과:<br>`| topic | cond | cost | min | calls | cite_ok | claim_src | subrq | gaps_ok | replans | judge |`<br>`| T1 | D | $0.825 | 7.5 | 25 | 100% | 13/13 | 6/6 | 5/5 | 2 | 4.14 |`<br>`| T1 | B | $0.307 | 3.2 | 10 | 100% | 12/12 | 6/6 | 5/5 | 0 | 4.14 |`<br>`| T1 | C | $0.305 | 4.0 | 10 | 100% | 11/11 | 6/6 | 5/5 | 0 | 4.29 |`<br>`| T2 | D | $0.662 | 7.1 | 19 | 100% | 12/12 | 6/6 | 5/5 | 1 | 4.00 |`<br>`| T2 | B | $0.321 | 3.7 | 10 | 100% | 12/12 | 6/6 | 5/5 | 0 | 4.14 |`<br>`| T2 | C | $0.318 | 3.6 | 10 | 100% | 11/11 | 6/6 | 5/5 | 0 | 3.86 |`<br>**관찰 (design.md 에 그대로 쓸 것):** (1) ADR-9 작동 — B/C 는 understand·plan 재사용, OpenAlex 24/24 캐시 적중, 실제 호출 0. (2) **B(critic 없음)도 결정적 불변 지표를 전부 통과** — 노드별 `check()`(checked_call) 가 이미 인용 실존·출처·Gap 근거를 지키므로 Critic 의 결정적 5종은 두 주제에서 1라운드에 통과했고 C 는 B 와 사실상 같은 실행(Replan 0). (3) D 만 LLM 비판이 major 를 내 Replan 2회·1회를 돌았고 비용 2.1~2.7배(evaluate 11회·synthesize/gap/critic 3회씩)인데 **judge 평균은 B/C 와 같은 수준(D 4.07 vs B 4.14 vs C 4.08)** — LLM 비판·Replan 은 결정적 지표도 judge 점수도 올리지 못했다. 한계로 솔직히 쓰고, 구조가 보장하는 것은 "하한(불변 지표)" 이지 "judge 가 보는 깊이" 가 아님을 명시. (4) judge 변별력 낮음 — T1 D·T1 B·T2 B 가 항목별 점수까지 동일(5,4,3,4,4,5,4), J3 는 6회 전부 3점. 조건 비교의 주 지표는 결정적 지표 + 비용·시간, judge 는 보조로만 (rubric 원칙 그대로). (5) **arXiv 전 실행 차단** — API 자체가 503/타임아웃(직접 호출도 61초 후 503). circuit breaker 가 설계대로 작동해 완주엔 지장 없었으나 T2(CS) 는 arXiv 쿼리 10개를 건너뛰어 OpenAlex 만으로 구성됨 → 리포트 §7 에 자동 기재됨. 비용 누적 $6.74 (실행 $5.73 + judge $1.01). 남은 계획(T3~T5 D/B/C + A×5 + judge) 추정 ≈ $7.7 → 총 ≈ $14.4 로 B/C 축소 불필요 | sonnet D 1회 $0.66~0.83 은 Haiku 의 2.1~2.6배. 10분 상한엔 7.1~7.5분으로 여유. Day 3 는 T3·T4 × D/B/C (추정 실제 ≈ 60회) |
| 2026-10-04 | **W4 Day 1 완료 (4.2 + 4.1 인프라).** (1) LLM-judge: `src/research_agent/judge.py`(초안의 `eval/judge.py` 대신 패키지 안 — llm.py 단일 호출점 유지), `prompts/judge.md`(J1~J7 5점/1점 기준, 인용 verbatim 강제, 결정적 지표를 ground truth 로 제시), `JudgeResult.check()`(7항목 정확히 1회·점수 1~5·인용 비어있지 않음 — 범위는 스키마 ge/le 가 아니라 코드 검사), `consistency_flags`(지표 미달인데 ≥4점이면 표시만, 점수 수정 없음), `agent judge <dir>|--all`. 결과는 실행 폴더의 `judge.json`·`judge_events.jsonl` 로, 원 `cost.json` 과 분리(ablation 비용 비교 오염 방지) — `RunLogger(into=, prefix=)` 추가. **실전 1회 (T1 D 12:33 실행, Opus): 평균 3.57 (J1 4·J2 4·J3 3·J4 3·J5 3·J6 4·J7 4), 인용 7/7 리포트 원문과 일치, flags 0, $0.195, 34초, 1회 호출.** judge 지적: 프리프린트 중복 레코드가 별개 근거로 수록, 같은 논문이 상충 A·B 양측에 인용, 지역 편중 Gap 이 표의 근거와 모순 → 4.5 선택 과제. (2) ablation 인프라: graph `plan_from`(ADR-9, CLI `--plan-from`), `scripts/run_ablation.py`(D→B→C→A 순, 완료 조합 건너뛰기, OpenAlex 추정 예산 가드, `--dry-run`, `--judge`, 실행 폴더에 `ablation.json`), `summarize_runs.py --ablation`(주제×조건 매트릭스 + 조건별 평균, judge 평균·flags 포함, 옛 실행은 slug·critic_mode 로 추정). `cost.json` 에 `model`·`max_replans`·`plan_from` 기록. 단위 테스트 51 → 60 | W4 를 일별로 나눔(§5): OpenAlex 하루 ≈100회가 병목이라 주제 5개 × 조건 4개를 3일(10/05~07)로 분할, 클린룸 10/08. dry-run 추정: 주제 2개 × D/B/C ≈ 96회 |
| 2026-10-04 | **W3 완료 (3.1~3.4).** 3.1 Critic LLM 비판 + Replan 루프 (ADR-7, `nodes/critic.py`·`nodes/replan.py`, `prompts/critic.md`·`replan.md`). **Replan 이 결과를 바꾼 증거**: 11:34 실행에서 rq2 관련 문헌 1편 → Replan 1 → 2편 → Replan 2 → 3편 이상으로 결정적 검사 통과 (`critique_1~3.json`, `replan_1~2.json`). 3.2 **같은 주제(T1) 3회 반복, 최종 코드, Haiku, OpenAlex 소진으로 Crossref 폴백 상태**: <br>`| run | status | cost | min | calls | cite_ok | claim_src | subrq | gaps | gaps_ok | critic | replans |`<br>`| 12:07 | ok | $0.236 | 6.0 | 24 | 100% | 13/13 | 5/6 | 6 | 6 | 3 | 2 |`<br>`| 12:13 | ok | $0.322 | 8.1 | 26 | 100% | 13/13 | 6/6 | 5 | 5 | 3 | 2 |`<br>`| 12:33 | ok | $0.320 | 7.5 | 23 | 100% | 10/10 | 6/6 | 7 | 7 | 2 | 1 |`<br>**L3 불변 지표(인용 검증 100%, claim 출처 100%, Gap 근거 ≥2, 완주) 3/3 통과.** sub-RQ 커버리지는 5/6·6/6·6/6 — 문헌 자체가 없는 sub-RQ 는 Replan 2회로도 못 채우며, 그 경우 §7 한계에 자동 기재됨(구조가 보장하는 것은 "채움" 이 아니라 "솔직한 기재"). 달라져도 되는 것의 편차: 비용 $0.29±0.04, 시간 6.0~8.1분, Gap 5~7개, 인용 문헌 집합 Jaccard 0.06(계획 쿼리가 실행마다 달라 선택 문헌은 거의 겹치지 않음), Gap 근거집합 겹침 0. LLM 비판은 3회 모두 마지막 라운드까지 major 를 냄(Haiku 가 "실험 연구 없음" 류를 major 로 판정) → 상한·예산 규칙으로 종료. 3.3 프롬프트: 아래 결함 수정이 곧 다듬기. 3.4 MCP: §7 잠정 미적용. `scripts/compare_repeats.py` 추가 | 반복 측정은 Crossref 폴백 상태라 OpenAlex 정상 상태보다 초록이 적어 커버리지에 불리한 조건이었음. W4 ablation 은 OpenAlex 일일 예산(실행당 ~30회, 하루 ~100회)을 먼저 계산하고 날짜를 나눠 돌릴 것 |
| 2026-10-04 | **W3 하네스 결함 5건 — 실제 반복 실행에서 드러나 수정.** (0) evaluate 의 HTTP 요청 하나가 7분 넘게 멈춤(SDK 기본 타임아웃 600초) → 10분 상한을 통째로 소모. `llm.request_timeout_sec: 180`, `sdk_max_retries: 2` 로 config 화. (1) Replan 이 `items: []` + rationale 에만 쿼리를 글로 적음(Haiku, 2회 연속) → 라운드 통째 낭비. `ReplanPlan.check(required=Critic 이 지목한 sub-RQ)` 로 되먹이고, 끝까지 비면 sub-RQ 질문에서 뽑은 결정적 fallback 쿼리 사용. (2) `ReplanPlan.queries` 에 `max_length=3` 을 두자 Haiku 가 4~6개를 내서 SDK `messages.parse` 가 **SDK 안에서** pydantic ValidationError 를 던져 실행 전체가 죽음 (2회). `llm.call` 이 SDK 측 검증 실패도 잡아 되먹이도록 수정(응답·usage 는 SDK 가 삼켜 비용 0 으로 기록), 쿼리 상한은 스키마가 아니라 코드에서 자름. `graph.run_graph` 는 예상 밖 예외에도 `status=error` + traceback.txt + state.json 을 남기고 정상 종료 (O1). (3) Replan 라운드 gap 호출에서 Haiku 가 7만 자 JSON 을 쏟다 `max_tokens` 16384 에서 잘려 json_invalid → 3분×2회 → **10분 상한 초과, 완주 실패** (반복 2회차). 노드 호출 상한 `llm.node_max_tokens: 6000` 분리, json_invalid 에는 "더 짧게" 힌트 되먹임, gap·synthesize 프롬프트에 길이 상한 명시. (4) OpenAlex 일일 크레딧 소진 → ADR-8 Crossref 폴백 | 셋 다 "LLM 의 운" 이 아니라 하네스가 막아야 할 결함. 단위 테스트 31 → 47개. W3-3.3(프롬프트 다듬기)은 스키마 재시도가 아니라 이 결함들이 실제 불안정 지점이었음 |
| 2026-10-04 | **W2 완료 (2.1~2.5).** search(OpenAlex 병렬 + arXiv 보강)·evaluate(sub-RQ 당 12편 선별, 10편 배치)·synthesize·gap·critic(결정적 5종)·write(구조는 상태에서 조립, LLM 은 한국어 요약·한계만) 노드. `report.py` 로 렌더링·지표를 베이스라인과 공유. **T1 end-to-end: $0.113 · 11회 · 8.4분(arXiv 실패 342초 포함) · Critic 이 rq4 커버 부족 적발 → 한계에 자동 기재. T2: $0.125 · 13회 · 3.9분 · Critic 통과.** 두 주제 모두 인용 검증 100%(55편·72편), claim 출처 100%, 모든 노드 1차 시도에 스키마·검사 통과 | 베이스라인 대비 질적 차이가 이미 보임: method 에 설계·표본 수 명시, 리뷰·논평은 reliability 2~3, 상충마다 원인 가설, Gap 마다 설계·데이터 구체화. 2 gaps(T2) 처럼 적게 나오는 경우는 W3 LLM 비판 대상. ADR-6 추가 |
| 2026-10-04 | **W2-2.1 완료: understand·plan 노드 + 그래프 러너 골격.** `nodes/__init__.py` 의 `checked_call` 이 "구조화 호출 → 스키마 `check()` → 실패 시 이슈를 되먹여 1회 재호출" 공통 루프. `graph.py` 는 NODES 리스트 순서 실행, `--until <node>` 로 부분 실행. T1·T2·T5 실제 실행: 모두 1차 시도에 검사 통과, 각 2회 호출 $0.01. sub-RQ 5~6개, 쿼리 4개씩, source_pref 가 CS→arxiv·경제→openalex 로 분기 | 단위 테스트 24개. 관찰: sub-RQ 6 × 쿼리 4 = 최대 24회 검색 → 후보 문헌 200~300편. 2.2 search 노드는 sub-RQ 당 상한을 두고, evaluate 는 배치 처리로 토큰을 묶어야 함 |
| 2026-10-04 | **W1-1.5 완료: 베이스라인 주제 5개 완주 (Haiku, 합계 $0.73).** 인용 검증률·주장-출처 연결 5/5 주제 모두 100%, sub-RQ 커버리지 4/4·4/5·5/5·5/6·6/6. 로그에서 드러난 낭비 3종 수정: (1) 모델이 검색 결과를 `verify_doi` 로 재검증하느라 최대 7 step 소모 (T5: 35회) → 이미 verified 인 문헌·arxiv id 는 Crossref 호출 없이 즉시 응답 + 도구 설명·프롬프트에 "검색 결과는 이미 검증됨" 명시, (2) `{'brief': {...}}` 래퍼 제출 (T2, 2회 거절) → 자동 언래핑, (3) `limitations` 누락 재제출 (T4 2회·T5 1회, 회당 ~$0.04) → 누락 필드만 콕 집는 피드백 메시지 | 베이스라인 약점(측정 대상)과 하네스 낭비(수정 대상)를 구분. 수정한 셋은 모두 후자. 베이스라인 약점으로 기록할 것: evidence `sample` 컬럼 전부 공란, 리뷰·논평 논문에 reliability 5 부여, T2(CS) 인용 11편으로 적음 |
| 2026-10-04 | **T1 베이스라인 첫 실행 실패 → 수정.** (1) `max_tokens` 8192 → 16384, (2) `stop_reason=max_tokens` 감지 시 잘린 tool_use 를 실행하지 않고 "압축해서 재제출" 피드백, (3) 프롬프트에 검색 6~10회·evidence 15~25편 상한, (4) `call_with_tools` 에 프롬프트 캐싱(system + 마지막 user 블록), 비용 집계에 캐시 읽기(10%)·생성(125%) 반영, (5) 비용·시간 상한 초과 시 예외로 죽지 않고 `status=limit_exceeded` 로 정상 종료 | 첫 실행: Haiku 가 문헌 190편을 전부 evidence 에 넣으려다 8192 토큰에서 7회 연속 잘림, $0.79 낭비 후 10분 상한. 수정 후 재실행: **$0.076 · 4 step · 1.4분**, 결정적 지표 전부 100% (인용 24/24 검증, claim 9/9 출처, sub-RQ 4/4 커버, gap 3). 캐시 적중으로 step 당 미적중 입력 ≤ 7 토큰 |
