# 평가 루브릭

두 층으로 나눈다. **결정적 지표**가 주 지표이고, **LLM-judge** 는 결정적으로 잴 수 없는 질을 보조로 본다.
judge 도 Claude 로 돌리므로 자기 채점 편향이 있다 → judge 는 항목마다 리포트의 근거 문장을 인용해야 하고, 결정적 지표와 모순되면 결정적 지표를 따른다 (plan.md §6.2).

## A. 결정적 지표 (cost.json → checks)

| 지표 | 계산 | 목표 (goals.md) |
|---|---|---|
| 완주율 | 완주 / 실행 | 100% (O1) |
| 인용 검증률 | 검증된 인용 / 전체 인용 | 100% (O2) |
| 주장-출처 연결률 | 출처 있는 claim / 전체 claim | 100% (O2) |
| sub-RQ 커버리지 | evidence ≥3 인 sub-RQ / 전체 | ≥ 80% (O3) |
| Gap 근거 | 모든 Gap 에 evidence ≥2 | 100% (O3) |
| 스키마 1차 통과율 | 재시도 없이 통과 / 호출 | 기록 (L2) |
| 비용 / 시간 | cost_usd, elapsed_sec | ≤ $1, ≤ 10분 (O6) |

## B. LLM-judge (1~5점, 항목마다 근거 인용 필수)

| # | 항목 | 5점 기준 | 1점 기준 |
|---|---|---|---|
| J1 | 주제 이해의 정확성 | 변수·모집단·맥락이 원 주제를 왜곡 없이 분해. 동의어가 실제 문헌 용어 | 범위를 임의로 좁히거나 넓힘, 핵심 변수 누락 |
| J2 | 조사 계획의 완결성 | sub-RQ 가 주제를 빠짐없이 덮고 서로 겹치지 않음 | sub-RQ 가 한 측면만 반복하거나 주제와 무관 |
| J3 | 근거 평가의 충실성 | method·sample·finding 이 초록 내용과 일치. 신뢰도 점수가 설계(RCT vs 사례연구)를 반영 | 초록에 없는 내용 서술, 점수가 일률적 |
| J4 | 종합의 깊이 | 합의·상충·조건부가 구분되고, 상충의 원인 가설이 구체적(표본·측정·맥락) | 요약 나열에 그침, 상충을 인지하지 못함 |
| J5 | Research Gap 의 타당성 | Gap 이 실제로 근거 문헌에서 다루지 않은 것이고, 근거 2편 이상이 그 공백을 보여줌 | 일반론("더 많은 연구가 필요")이거나 이미 연구된 것 |
| J6 | 향후 연구 제안의 구체성 | RQ·방법·데이터가 실행 가능한 수준 | 방법·데이터 없음 |
| J7 | 한계 서술의 정직성 | Agent 가 못 찾은 것, 확신 못 하는 것을 명시 | 한계 없음 또는 형식적 |

judge 출력 형식: 항목별 `{score, quote, reason}` JSON. 총점은 단순 평균.

구현 (W4): `src/research_agent/judge.py` + `prompts/judge.md`, 실행은 `uv run agent judge <실행 폴더>` 또는 `--all`.
결과는 그 실행 폴더의 `judge.json` (`scores`, `mean`, `items[{id,name,score,quote,reason}]`, `overall_comment`, `flags`, 비용) 과
`judge_events.jsonl`. 원 실행의 `cost.json` 에는 judge 비용이 섞이지 않는다. `flags` 는 결정적 지표가 목표 미달인데 4점 이상을 준
항목(예: sub-RQ 커버리지 < 80% 인데 J2 ≥ 4) — 점수는 그대로 두고 표시만 한다. 모델은 `config/models.yaml` 의 `judge_model`.

## C. 설계평가 대응 (교수자 평가, 문서로 증빙)

| 항목 | 증빙 위치 |
|---|---|
| Reasoning / Planning / Tool Use / Reflection / Replanning 적용 | runs/*/events.jsonl 의 노드별 이벤트, docs/design.md |
| 접근 방식의 비교 | ablation 매트릭스 (조건 A~D) |
| 재현성 | README 3단계 실행, 반복 실행 편차 표, 키 없는 공개 API |
| 설계 의도·대안·기각 이유 | plan.md ADR → design.md |
