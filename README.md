# AI Research Agent

연구 주제 하나를 입력하면 **주제 이해 → 조사 계획 → 문헌 탐색 → 평가 → 종합 → Research Gap 제안**을 수행해
연구 착수용 브리프(Research Brief)를 만드는 에이전트.

연세대학교 DAS6035 *AI에이전트설계및응용* 중간 해커톤 제출물 (제출 2026-11-02).

## 빠른 시작

설치·키 설정·실행 방법은 **[`research_agent/README.md`](research_agent/README.md)** 에 있습니다.

```bash
cd research_agent
uv sync
cp .env.example .env          # ANTHROPIC_API_KEY 입력 — 필요한 키는 이것 하나
uv run agent run --topic "생성형 AI 활용이 대학원생의 연구 생산성과 연구 품질에 미치는 영향"
```

## 저장소 구조

| 경로 | 내용 |
|---|---|
| [`goals.md`](goals.md) | 목표 체계 — 평가 기준에서 도출한 Objective O1~O7, 성공 지표, non-goal |
| [`plan.md`](plan.md) | 구현 계획 — 아키텍처, 설계 결정 기록(ADR), 주차별 작업 분해, 테스트 주제·지표·ablation 설계 |
| [`research_agent/`](research_agent/) | 소스 코드, 프롬프트, 설정, 테스트, 평가 세트 |
| `research_agent/runs/` | 실행 로그·리포트 (제출용 실행 결과는 마감 전 선별 추가) |

## 설계 요점

- **키는 Anthropic 하나.** 문헌 검색은 키가 필요 없는 공개 학술 API(OpenAlex·arXiv·Crossref)만 사용합니다.
- **출력 구조 고정.** 모든 단계가 Pydantic 스키마로 주고받고, 최종 리포트도 스키마 검증을 통과해야 저장됩니다.
- **품질 하한은 코드가 보장.** 인용 실존 검증, 주장-출처 연결 등은 LLM이 아니라 결정적 검사가 확인합니다.
- 실행마다 문장과 선택 문헌은 달라질 수 있으나, 리포트 구조·필드 채움·인용 검증률은 달라지지 않습니다.

## 진행 상태

| 주차 | 내용 | 상태 |
|---|---|---|
| W1 | 스키마, LLM 래퍼, 학술 도구, 베이스라인 ReAct, 평가 세트 | 완료 |
| W2 | 역할 분리 그래프(Planner·Searcher·Evaluator·Synthesizer·Critic·Writer) | 완료 (Critic 결정적 검사까지. Replan 루프는 W3) |
| W3 | Reflection·Replanning 루프, 반복 실행 안정성 | 완료 (Critic LLM 비판 + Replan 루프, 같은 주제 3회 반복 측정) |
| W4 | 베이스라인 vs 최종 구조 ablation, LLM-judge, 클린룸 재현 테스트 | 예정 |
