# AI Research Agent — 구현 계획 (plan.md)

- 상위 문서: `goals.md` (O1~O7, 성공 기준). 이 문서는 "어떻게"를 다룸
- 작성일: 2026-10-02 · 상태: **W1 코드 완료, 맥에서 스모크 테스트 대기** (`research_agent/README.md` 참고)
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
  Critic ──(미달)──→ Replan (부족한 sub-RQ만 재검색, 최대 2회) ──→ ③
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
│   ├── critic.py
│   ├── gap.py
│   └── write.py
├── graph.py          # 노드 순서·루프·병렬 정의, 러너
├── baseline.py       # 단일 ReAct (ablation용)
├── logging.py        # runs/ 이벤트 기록
└── cli.py
prompts/<node>.md     # 노드별 시스템 프롬프트. 코드에 문자열 없음
config/models.yaml    # provider, model, temperature, max_cost_usd, max_minutes
schemas/brief.json    # ResearchBrief JSON Schema export (문서용)
eval/
├── topics.yaml       # 테스트 주제 5개
├── rubric.md         # LLM-judge 루브릭
└── judge.py
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
| 종합의 깊이·논리 | LLM 비판 | actions 로 Replan 지시 |

Replan 상한 2회. 상한 도달 시 미달 항목을 리포트 §7 "한계"에 자동 기재하고 종료 (실패로 죽지 않음 — O1).

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

---

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
| 3.1 | Critic LLM 비판 + Replan 루프 | 최소 1개 주제에서 Replan이 결과를 바꿈 (로그로 증명) |
| 3.2 | **같은 주제 3회 반복 실행, 편차 측정** | 결정적 지표 전부 100% 유지. Gap 겹침 비율·비용 편차 기록 |
| 3.3 | 프롬프트 다듬기 | 불안정 노드(스키마 재시도 잦은 곳) 우선 |
| 3.4 | MCP 적용 여부 결정 | 도구 하나를 MCP 서버로 노출할지 — 수업 7주차 내용 보고 판단. 설계평가 가산 가능성 vs 재현 복잡도 |

### W4 (10/23–10/29) — 실험 + 클린룸

| # | 태스크 | DoD |
|---|---|---|
| 4.1 | ablation: 조건 A~D × 주제 5개 | 매트릭스 (품질 지표, 비용, 시간) |
| 4.2 | LLM-judge 채점 | rubric 점수표 |
| 4.3 | **클린룸**: 새 컨테이너/Colab, 새 키, README만으로 L1~L3. 다른 Claude 모델명으로도 1회 | 체크리스트 전부 통과 |
| 4.4 | 키·경로 누출 검사, zip 용량 확인 (1GB 한도, 예상 100MB 미만). **config `model` 을 개발용 haiku → 제출용 sonnet-5-5 로 교체했는지 확인** | – |

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
| T5 | 한국어 입력 + 공공정책 | 전기차 보조금 정책이 중고차 시장 가격에 미치는 영향 | 한국어 → 영어 쿼리 확장, 경제학 문헌 |

T5는 한국어로 입력, 나머지는 한·영 둘 다 1회씩 돌려 언어 민감도 확인.

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

LLM-judge도 Claude로 채점하므로 자기 채점 편향이 있음. 완화: 실행과 **다른 모델명** 사용, 루브릭을 항목별 근거 인용 필수로 작성, 결정적 지표를 주 지표로 두고 judge 점수는 보조로만 해석. 이 한계는 design.md에 명시.

### 6.3 ablation 설계

| 조건 | 설명 |
|---|---|
| A | 베이스라인 ReAct |
| B | 그래프, Critic 없음 |
| C | 그래프 + Critic 결정적 검사만 |
| D | 그래프 + Critic 전체 + Replan (최종) |

같은 검색 캐시 위에서 실행해 검색 변동을 통제. 주제 5개 × 조건 4개 = 20회 (+ D 조건 반복 3회 = 10회 추가). 비용 상한 고려해 A·D는 전수, B·C는 주제 2개로 축소 가능.

---

## 7. 열린 질문

| 질문 | 확인 대상 | 기한 |
|---|---|---|
| MCP 적용 여부 | 7주차 수업 후 본인 판단 | W3 |
| 웹 검색 추가 여부 | W4 여유 보고 | W4 |

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
| 2026-10-04 | **T1 베이스라인 첫 실행 실패 → 수정.** (1) `max_tokens` 8192 → 16384, (2) `stop_reason=max_tokens` 감지 시 잘린 tool_use 를 실행하지 않고 "압축해서 재제출" 피드백, (3) 프롬프트에 검색 6~10회·evidence 15~25편 상한, (4) `call_with_tools` 에 프롬프트 캐싱(system + 마지막 user 블록), 비용 집계에 캐시 읽기(10%)·생성(125%) 반영, (5) 비용·시간 상한 초과 시 예외로 죽지 않고 `status=limit_exceeded` 로 정상 종료 | 첫 실행: Haiku 가 문헌 190편을 전부 evidence 에 넣으려다 8192 토큰에서 7회 연속 잘림, $0.79 낭비 후 10분 상한. 수정 후 재실행: **$0.076 · 4 step · 1.4분**, 결정적 지표 전부 100% (인용 24/24 검증, claim 9/9 출처, sub-RQ 4/4 커버, gap 3). 캐시 적중으로 step 당 미적중 입력 ≤ 7 토큰 |
