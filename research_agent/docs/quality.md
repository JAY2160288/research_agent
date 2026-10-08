# 품질 개선안 — "제품 수준" 기준으로 본 결함과 고칠 순서

> 작성 2026-10-08. 기준은 하나: **평가자(교수님)가 처음 보는 주제를 넣고 README 명령 3개를 쳤을 때, 나오는 리포트와 실행 경험이 완성된 제품 수준인가.**
> 각 항목에 "무엇이 부족한지(측정된 근거) → 어떻게 고치는지(파일·스키마·config) → 어떻게 확인하는지" 를 적는다.
> 파이프라인(노드·스키마·프롬프트)을 바꾸는 항목은 ablation 20회·judge 점수가 무효가 되고 재실행할 크레딧·OpenAlex 예산이 없으므로 **제출 전/후를 구분**한다 (§4, plan.md ADR-12).

## 0. 지금 리포트·실행이 제품 수준에 못 미치는 지점 (측정된 것만)

| # | 증상 | 근거 | 원인 |
|---|---|---|---|
| P1 | **중요한 문헌을 놓친다** | 사람 서베이 참고문헌 회수율 retrieved ≤ 6%, cited ≤ 2% (design.md §3.6) | 키워드 검색 상위 15편 × 쿼리만. 인용 그래프를 안 탄다. `openalex.search` 가 `referenced_works` 를 받지 않음 |
| P2 | **Evidence 표가 비어 있거나 얕다** | judge J3(근거 평가) 가 전 조건 최저(대부분 3점), `sample` 공란 다수 | 초록만 사용 (ADR-4). 초록에 없는 method·sample 은 빈 문자열 |
| P3 | **종합에 "문헌이 없다" 류 문장이 섞여 근거가 안 맞는다** | unsupported 주장의 대부분이 부재 주장 (§3.6) | synthesize 가 Gap 성격 문장을 claim 으로 냄. 스키마에 분리 필드 없음 |
| P4 | **같은 논문이 두 번 근거로 센다** | judge 지적: 프리프린트·출판본 별개 레코드, 같은 논문이 상충 A·B 양측 인용 (plan.md 10/04) | `Paper.id` 가 DOI 와 `arxiv:` 로 따로 정규화, 병합 없음 |
| P5 | **한국어 주제인데 한국 문헌이 0건** | design.md §6 | OpenAlex 한국어 색인 얇음, 키 없는 한국 학술 API 없음 |
| P6 | **6~8분을 깜깜이로 기다린다** | CLI 가 끝날 때만 출력 | 진행 표시 없음, 중간 산출물은 파일로만 |
| P7 | **하루 3회 넘기면 품질이 떨어진다** | OpenAlex 100회/일/IP, 4회째부터 Crossref 폴백 → 초록 부족 → sub-RQ 커버리지 5/6 (§5 12:07) | 키 없는 공개 API 만 (ADR-3, 재현성 조건) |
| P8 | **중간에 끊기면 처음부터** | 네트워크·시간 상한·Ctrl-C 뒤 재실행 = 검색·평가 전부 다시 | 체크포인트·재개 없음 |
| P9 | **결과를 다른 도구로 못 가져간다** | report.md·brief.json 만 | BibTeX/RIS 없음 |
| P10 | **느리다** | D 조건 6.9분, evaluate 가 호출 수의 절반 | evaluate 배치가 **순차** 실행 (`nodes/evaluate.py` 에 ThreadPool 없음) |

---

## 1. 개선 항목 우선순위

효과 = 평가자가 느끼는 리포트·실행 품질 차이, 비용 = 구현 난이도 + 실행당 추가 비용, 영향 = 파이프라인 출력(지표·ablation)이 바뀌는가.

| 순위 | 항목 | 푸는 문제 | 효과 | 비용 | 파이프라인 영향 | 제출 전 가능 | 상태 |
|---|---|---|---|---|---|---|---|
| 1 | A1 스노볼링 (인용 그래프 1홉) | P1 | ★★★ | 중 (+OpenAlex 10~20회/실행) | 있음 | ✗ | 보류 |
| 2 | B1 부재 주장 분리 | P3 | ★★★ | 하 | 있음 (스키마·프롬프트) | ✗ | 보류 |
| 3 | A3 레코드 병합 | P4 | ★★ | 하 | 있음 (tools) | ✗ | 보류 |
| 4 | D1 evaluate 병렬화 | P10 | ★★ (시간 −2~3분) | 하 | 없음 | ✓ | **완료** |
| 5 | C1 진행 표시 | P6 | ★★ | 하 | 없음 | ✓ | **완료** |
| 6 | C2 한국어 주제 → 자동 한국어 리포트 | 평가자 기본 경험 | ★★ | 하 | 없음 (사후 단계) | ✓ | **완료** |
| 7 | C3 체크포인트·`--resume` | P8 | ★★ | 중 | 없음 | ✓ | **완료** |
| 8 | B2 지지 검증을 Critic 안으로 | P3·신뢰 | ★★★ | 중 (+$0.1~0.2/실행) | 있음 | ✗ | 보류 |
| 9 | B3 Evidence 정량 필드 | P2 | ★★ | 중 | 있음 | ✗ | 보류 |
| 10 | C5 내보내기 (BibTeX·RIS) | P9 | ★ | 하 | 없음 | ✓ | **완료** |
| 11 | A2 캐시 키 정규화 | 같은 주제 재실행 속도 | ★ | 하 | 없음 | ✓ | **완료** |
| 12 | C4 `--exclude`/`--include` | 잘못 잡힌 문헌 교정 | ★ | 중 | 없음 (선택 옵션) | ✓ | **완료** |
| 13 | A4 OA 본문 추출 | P2 | ★★★ | 상 | 있음 | ✗ | 보류 |
| 14 | A5 한국 학술 DB (KCI) | P5 | ★★ | 중 (키·약관 — ADR-3 과 충돌) | 있음 | ✗ | 보류 |
| 15 | B4 Critic 커버리지 검사의 질 | T6 류 대상 불일치 | ★★ | 중 | 있음 | ✗ | 보류 |
| 16 | D2 노드별 모델 티어 | 비용 −30~50% | ★ | 하 | 있음 (품질 재측정) | ✗ | 보류 |
| 17 | C6 재실행 diff | 반복 사용 | ★ | 하 | 없음 | ✓ | 보류 |

---

## 2. 항목별 설계

### A. 검색 — 놓치는 문헌을 줄인다

**A1. 스노볼링 (인용 그래프 1홉)**
- 왜: 회수율 손실의 대부분이 search 단계 (retrieved ≤ 6%). 사람 서베이는 키워드가 아니라 인용을 따라간다.
- 어떻게:
  - `tools/openalex.py`: `search` 의 `select` 에 `referenced_works` 추가 (응답 크기 소폭 증가, 호출 수 불변). `get_many(ids)` 추가 — `filter=openalex_id:W1|W2|…` 로 **한 호출에 50편** 조회. `cited_by(id)` 는 `filter=cites:W…` 1호출.
  - `nodes/search.py` 에 2단계 추가: evaluate 가 끝난 뒤 sub-RQ 당 관련성 ≥ 4 상위 3편의 `referenced_works` 합집합(보통 100~150편) → `get_many` 2~3회 → 제목·초록 있는 것만 후보에 합류 → **증분 평가**(Replan 때 쓰는 `only_sub_rqs` 경로 재사용). `cited_by` 는 최신 문헌 보강용으로 상위 1편만.
  - 그래프 순서: search → evaluate → **snowball → evaluate(증분)** → synthesize. `graph.py` NODES 에 노드 하나 추가, `config` 에 `tools.snowball_top_k: 3`, `snowball_hops: 1`, `snowball_max_new: 60`.
  - 예산: 실행당 OpenAlex +6~10회 (현 30~35회 → 40~45회). 하루 2회 안쪽.
- 확인: `gold_recall.py` retrieved/cited (목표 retrieved 6% → 20%+), evaluate 편수, 비용.
- 주의: 후보가 늘면 evaluate 비용이 는다 → `evaluate_per_subrq` 를 12 → 15 로만 올리고 나머지는 A3 재순위로 거른다.

**A2. 캐시 키 정규화** — 완료
- plan 노드가 낸 쿼리 문자열이 실행마다 달라 같은 주제 재실행에도 캐시 적중이 0 이었다 (클린룸 관찰). 소문자·공백·양끝 따옴표만 정규화 (`tools/cache.py`). 단어 순서는 유지 — 검색 순위가 달라질 수 있다.

**A3. 레코드 병합 + 경량 재순위**
- 병합: OpenAlex 응답의 `ids.arxiv`·`locations[].landing_page_url` 로 arXiv id ↔ DOI 매핑, 없으면 제목 정규화(소문자·구두점 제거) 일치 + 연도 ±1 + 첫 저자 성 일치. `Paper` 에 `aliases: list[str]` 추가, 레지스트리(`tools/__init__.py` `papers`) 가 병합하고 인용 시 대표 id 로 치환. 렌더러는 참고문헌에 "preprint: arXiv:…" 병기.
- 재순위: 후보 300~400편 중 evaluate 에 보낼 12~15편을 지금은 (초록 있음 → 피인용 → 최신) 순으로 고른다 (`select_candidates`). 피인용은 오래된 문헌에 유리해 최신 연구가 밀린다. BM25 (`rank_bm25`, 의존성 1개, LLM 0) 로 sub-RQ 질문과의 점수 → 상위 선택.
- 확인: 중복 근거 0건 (judge), 회수율 cited, 최신 2년 문헌 비율.

**A4. OA 본문 추출 (초록 → Methods·Results)**
- OpenAlex `primary_location.pdf_url` 또는 `open_access.oa_url` 이 있는 문헌만 (실측 30~50%). `pypdf` 로 텍스트 → 섹션 헤더 정규식(Method/Methods/Participants/Results)으로 1,500자 이내 발췌 → `Paper.fulltext_excerpt`.
- evaluate 프롬프트에 발췌를 초록 뒤에 붙이고 `sample`·`method` 를 거기서 읽게. 비 OA 는 지금처럼 초록만 + Evidence 에 `source_depth: abstract|fulltext` 표시 → 리포트 표에 아이콘.
- 비용: 실행당 PDF 20~40편 다운로드(시간 +1~2분, 병렬), 토큰 +30%. `--depth deep` 옵션으로.
- 확인: `sample` 공란율, judge J3, support 지지율 (본문 기준 대조로 partial 감소 기대).

**A5. 한국 학술 DB (KCI OpenAPI)**
- KCI 가 논문 검색·초록 OpenAPI 를 무료 키로 제공한다. `tools/kci.py` 추가, `Paper.source` 에 `"kci"`. **ADR-3(키는 Anthropic 하나)과 충돌** — 평가자 재현 부담이 늘므로 선택 도구 + 키 없으면 자동 생략으로만.
- 한국어 쿼리는 TopicFrame 의 **한국어 원 개념어**로 (지금은 영어 동의어만 쿼리로 씀) → `ResearchPlan.queries` 에 `lang` 필드.
- 확인: 한국어 주제에서 한국 문헌 인용 편수 (현재 0).

### B. 분석 — 리포트의 주장이 더 정확하고 깊어진다

**B1. 부재 주장 분리**
- `schemas.Synthesis` 에 `absence_notes: list[AbsenceNote(statement, sub_rq_ids, searched_queries)]` 추가. `prompts/synthesize.md` 에 "문헌이 X 를 다루지 않는다는 관찰은 claim 이 아니라 absence_notes 에" 명시. `Synthesis.check()` 에 결정적 검사: claim 문장에 `no study|not addressed|lacks|absent` 류 패턴이 있고 근거가 1편이면 되먹임.
- `nodes/gap.py` 는 `absence_notes` 를 Gap 후보의 1차 입력으로. 렌더러 §4 에는 "문헌 공백 관찰" 소절로 따로, §5 Gap 과 링크.
- 확인: support unsupported 쌍 (D 2쌍 → 0), judge J4·J5.

**B2. 주장-근거 지지 검증을 Critic 안으로**
- 지금은 `agent support` 가 사후에만 돈다. `nodes/critic.py` 의 LLM 단계 앞에 `support_run` 을 호출해 **unsupported claim 이 1개라도 있으면 major** → synthesize 재호출 시 "이 claim 은 인용 초록이 뒷받침하지 않음: …" 을 되먹임 (Replan 이 아니라 synthesize 만 재실행하는 짧은 경로 — `graph.py` 에 `resynthesize` 분기).
- partial 은 "표현을 초록 범위로 좁혀라" 되먹임, major 는 아님.
- 비용 +$0.1~0.2/실행 (실행 모델 사용 시 +$0.05). 리포트 카드에 **지지율이 실행 시점에** 붙는다 — 평가자가 보는 가장 설득력 있는 숫자.
- 확인: cite 지지율 78% → 90%+, unsupported 0.

**B3. Evidence 정량 필드**
- `Evidence` 에 `direction: Literal["positive","negative","null","mixed","na"]`, `effect: str`("d=0.42", "OR 1.8"), `population: str`, `design: Literal["rct","quasi","survey","qualitative","review","meta","other"]`. 초록에 없으면 `na`/빈 문자열 — **추정 금지** 는 지금 규칙 그대로.
- synthesize 가 상충을 "A n편 vs B m편" 이 아니라 **방향·설계별 집계**로 쓰고, 렌더러 §3 Evidence map 에 설계 × 방향 교차표 추가.
- 확인: judge J3·J4, 상충마다 원인 가설이 설계 차이를 지목하는 비율.

**B4. Critic 커버리지 검사의 질**
- 지금 결정적 검사는 "sub-RQ 당 relevance ≥ 3 문헌 ≥ 3편" 이라 T6 처럼 **편수는 채웠지만 대상·언어가 빗나간** 경우를 못 잡는다 (LLM Critic 만 잡음). TopicFrame 의 `population`·`context` 키워드가 Evidence `population`/초록에 한 번도 안 나오면 "대상 불일치" 결정적 이슈로. B3 의 `population` 필드가 전제.
- Gap 중복: `GapList.check()` 에 Gap 간 근거 집합 Jaccard > 0.8 이면 병합 요구, 제안 RQ 에 변수·대상·방법 중 둘 이상 없으면 되먹임.

### C. 실행 경험 — 기다림·중단·개입·내보내기

**C1. 진행 표시** — 완료 (`progress.py`)
- `RunLogger.listeners` 에 콜백을 두고 CLI 가 노드 전이·후보/평가 편수·Critic 판정·Replan 쿼리·누적 비용을 한 줄씩 찍는다. 의존성 없음. `--quiet` 로 끔. 파이프라인 코드 무변경.

**C2. 한국어 주제 → 자동 한국어 리포트** — 완료 (`cli.py` `--lang`)
- `run` 끝에 `translate_run` 을 이어 호출. 주제가 한국어면 기본 ko, `--lang en` 으로 끔. 번역 실패는 영어 리포트 유지 + 재시도 명령 안내. brief.json·cost.json 불변 (ADR-11).

**C3. 체크포인트·재개** — 완료 (`graph.py`)
- 노드가 끝날 때마다 `state.json` 저장. `--resume <실행 폴더>` 가 events.jsonl 의 마지막 `node_end` 다음부터 같은 폴더에 이어 쓴다 (끝난 노드는 `node_skipped`). 비용은 이어받고(`RunLogger.seed`) 시간은 새로. Ctrl-C 도 `interrupted` 로 상태를 남긴다.

**C4. 문헌 개입** — 완료 (`--exclude`, `--include`)
- 제외 문헌은 `Tools._register` 에서 걸러 레지스트리에 들어오지 않는다(인용 불가). 고정 문헌은 search 첫 라운드에 `get_by_doi` 로 가져와 모든 sub-RQ 후보에 `Paper.pinned=True` 로 넣어 evaluate 상한과 무관하게 평가한다. `cost.json` 에 `excluded`·`included` 기록.
- 남은 것: `--review-plan` (plan 뒤 멈춰 사용자가 `plan.json` 을 고치고 `--plan-from` 으로 재개 — 이미 있는 경로의 조합).

**C5. 내보내기** — 완료 (`export.py`, `agent export --format bibtex|ris`)
- `papers.json` 에서 직접. 번호·순서는 `render_markdown` 에 빈 `_Refs` 를 넘겨 report.md 와 동일. DOCX 는 의존성 추가라 보류.

**C6. 재실행 diff**
- `agent diff <폴더A> <폴더B>`: 새로 들어온/빠진 인용 문헌, Gap 제목 매칭(근거 집합 겹침), claim 수·지지율 변화. 반복 실행 편차(design.md §5)를 리포트 수준에서 보여준다.

### D. 속도·비용

**D1. evaluate 병렬화** — 완료 (`nodes/evaluate.py`, `tools.evaluate_workers: 4`)
- 배치(10편) 호출이 순차였다. sub-RQ 6 × 1~2배치 = 8~12회 → 4 워커. `ex.map` 이 입력 순서를 지켜 합치는 순서가 순차와 같다. `RunLogger` 에 락. 실측 단축은 다음 live 실행의 `cost.json` 으로 확인.

**D2. 노드별 모델 티어**
- `llm.model_per_node: {understand: haiku, plan: haiku, replan: haiku, evaluate: sonnet, synthesize: sonnet, gap: sonnet, critic: sonnet, write: haiku}`. 구조화 추출 노드는 haiku 로 충분 (W2 실측 1차 통과율 100%). 예상 −25~35%. 바꾸면 품질 재측정(judge) 필요 → 제출 후.

**D3. 견고성 잔여**
- arXiv 는 OpenAlex 가 이미 색인하므로 직접 호출을 **기본 off** 로 (503 리스크 제거, CS 주제는 `source_pref` 가 켜면 on).
- 10분 상한 도달 시 `grace_write` 가 부분 리포트를 쓴다 — 카드에 "시간 상한으로 Replan 생략" 을 명시 (지금은 §7 에만).

---

## 3. 확인 — 개선 전후를 같은 잣대로

| 지표 | 현재 (sonnet D) | 목표 | 도구 |
|---|---|---|---|
| 정답 서베이 회수율 retrieved / cited | 3.6% / 1.7% | 20% / 8% | `scripts/gold_recall.py` (골드셋 7편 → 20편) |
| 주장-근거 지지율 cite / claim | 78% / 94% | 90% / 100% | `agent support` → B2 로 실행 중 |
| unsupported 쌍 | 2 | 0 | 〃 |
| 중복 근거 레코드 | 있음 | 0 | 렌더러 검사 추가 |
| `sample` 공란율 | 높음 (미측정) | < 30% (OA 본문 시) | `summarize_runs` 열 추가 |
| 한국어 주제의 한국 문헌 인용 | 0 | ≥ 3편 | 〃 |
| judge J3 / 평균 | 3 / 4.14 | 4 / 4.4 | `agent judge` |
| 시간 / 비용 | 6.9분 / $0.77 | 4분 / $0.5 | `cost.json` |
| 캐시 적중률 (같은 주제 재실행) | ≈ 0 | > 60% | `events.jsonl` tool_call |

기존 결정적 불변 지표(인용 검증 100%, claim 출처 100%, Gap 근거 ≥ 2, 7섹션)는 **그대로 하한**이다. 어떤 개선도 이것을 깨면 안 된다 — `tests/` 가 지킨다.

---

## 4. 순서 — 제출 전 / 제출 후

**제출 전 (파이프라인 출력·지표 정의 불변, 크레딧 0, ablation 유효) — 2026-10-08 완료, plan.md ADR-12**
1. ✅ D1 evaluate 병렬화 (단위 테스트로 결과 동일성 확인)
2. ✅ C1 진행 표시 + C2 한국어 자동 번역
3. ✅ C3 `--resume` + C4 `--exclude/--include`
4. ✅ C5 BibTeX/RIS 내보내기
5. ✅ A2 캐시 키 정규화
6. ☐ 렌더러에서 A3 중복 **표시**(병합은 안 함: "같은 논문의 프리프린트로 보임" 각주)
7. ☐ live 실행 1회(haiku ≈ $0.3)로 병렬화 시간 단축·자동 번역·진행 표시 실측 → design.md §5 표에 행 추가

**제출 후 (파이프라인 변경 → D 조건 5주제 재실행 ≈ $4 + OpenAlex 2일)**
1. A1 스노볼링 + A3 병합·BM25 재순위 (회수율)
2. B1 부재 주장 분리 + B2 지지 검증 in-Critic (정확성)
3. B3 정량 필드 + B4 Critic 커버리지 질 (깊이)
4. A4 OA 본문 (`--depth deep`), A5 KCI (선택 도구)
5. D2 모델 티어, C6 diff

각 단계 끝에 §3 표를 다시 채우고 design.md §3·§5 형식 그대로 전후 비교를 남긴다.
