# AI Research Agent

연구 주제 하나를 입력하면 **주제 이해 → 조사 계획 → 문헌 탐색 → 평가 → 종합 → Research Gap 제안**을 수행해 연구 착수용 브리프를 만드는 에이전트.
연세대 DAS6035 *AI에이전트설계및응용* 해커톤 제출물.

## 재현 (3단계)

```bash
# 1. 설치  (uv 가 없으면: curl -LsSf https://astral.sh/uv/install.sh | sh)
uv sync

# 2. 키 설정 — Anthropic 키 하나면 됩니다. 학술 API(OpenAlex·arXiv·Crossref)는 키가 필요 없습니다.
cp .env.example .env     # ANTHROPIC_API_KEY 입력

# 3. 실행
uv run agent run --topic "생성형 AI 활용이 대학원생의 연구 생산성과 연구 품질에 미치는 영향"
```

결과는 `runs/<timestamp>_<mode>_<topic>/` 에 저장됩니다:

| 파일 | 내용 |
|---|---|
| `report.md` | 최종 리포트 (7개 섹션) |
| `brief.json` | 같은 내용의 구조화 데이터 (스키마: `schemas/brief.json`) |
| `events.jsonl` | 모든 LLM 호출·도구 호출·단계 전이 로그 |
| `cost.json` | 토큰·비용·시간·결정적 품질 지표 |
| `papers.json` | 이번 실행에서 수집한 모든 문헌 |

### 모델 바꾸기

`config/models.yaml` 의 `model` 을 수정하거나 `--model <이름>` 으로 한 번만 덮어씁니다.
계정에서 쓸 수 있는 모델명은 `uv run agent models` 로 확인합니다.

| 용도 | 모델 | 비고 |
|---|---|---|
| 개발·디버깅 (기본값) | `claude-haiku-4-5` | 동작·스키마 통과 확인용. 비용 최소 |
| 품질 측정·제출 실행 | `claude-sonnet-5-5` | `--model claude-sonnet-5-5` 또는 config 교체 |
| LLM-judge | `claude-opus-5-5` | 실행 모델과 다르게 두어 자기 채점 편향 완화 |

평가자가 다른 Claude 모델로 재현할 때는 `model` 과 `pricing` 표에 그 모델명을 추가하면 됩니다.
`pricing` 에 없는 모델은 `default` 단가(Opus 기준, 보수적)로 비용을 집계합니다.

### 실행 모드

| 모드 | 설명 | 상태 |
|---|---|---|
| `--mode baseline` | 단일 ReAct 루프 (ablation 기준점) | 구현 |
| `--mode graph` | 역할 분리 그래프 + Critic + Replanning (최종) | W2 |

`--no-cache` 를 붙이면 도구 캐시 없이 live 로 검색합니다.

## 재현성 설계

- **키는 Anthropic 하나.** 문헌 검색은 키 없는 공개 API 만 사용 → 평가자가 추가 발급 없이 실행 가능.
- **출력 구조 고정.** 모든 단계가 Pydantic 스키마로 주고받고, 최종 리포트도 스키마 검증을 통과해야 저장됨.
- **품질 하한은 코드가 보장.** 인용 실존 검증·주장-출처 연결 등은 LLM 이 아니라 결정적 검사가 확인.
- 실행마다 문장과 선택 문헌은 달라질 수 있으나, 리포트 구조·필드 채움·인용 검증률은 달라지지 않습니다.

## 개발

```bash
uv run pytest                          # 단위 테스트 (네트워크·API 불필요)
uv run python scripts/smoke_tools.py   # 학술 API 실제 호출 확인
uv run python scripts/smoke_llm.py     # Anthropic 구조화 출력 확인
```

설계 문서: `../goals.md` (목표·성공 기준), `../plan.md` (아키텍처·ADR·작업 분해).
