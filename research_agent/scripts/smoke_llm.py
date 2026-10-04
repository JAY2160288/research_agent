"""W1-1.3 스모크 테스트 — 실제 Anthropic API 로 구조화 출력이 동작하는지 확인.

실행:  uv run python scripts/smoke_llm.py
필요:  .env 에 ANTHROPIC_API_KEY

확인 항목
  1. 계정에서 쓸 수 있는 모델 목록 (config/models.yaml 의 model 이 그 안에 있는지)
  2. TopicFrame 스키마로 한 번 호출 → 파싱 성공, 토큰·비용 기록
  3. runs/ 아래에 events.jsonl, cost.json 생성
"""

from __future__ import annotations

import sys

from research_agent.config import load_settings, load_prompt
from research_agent.llm import LLM
from research_agent.runlog import RunLogger
from research_agent.schemas import TopicFrame

TOPIC = "생성형 AI 활용이 대학원생의 연구 생산성과 연구 품질에 미치는 영향"


def main() -> int:
    s = load_settings()
    if not s.anthropic_api_key:
        print("ANTHROPIC_API_KEY 가 없습니다. .env.example 을 .env 로 복사하고 키를 넣으세요.")
        return 1

    log = RunLogger(TOPIC, "smoke")
    llm = LLM(s, log)

    # 1. 모델 목록
    print("== 사용 가능한 모델 ==")
    ids = []
    try:
        for m in llm.client.models.list(limit=50):
            ids.append(m.id)
            print("  ", m.id)
    except Exception as e:  # noqa: BLE001
        print("  (목록 조회 실패:", e, ")")
    for key in ("model", "judge_model"):
        name = getattr(s.llm, key)
        # 별칭(claude-haiku-4-5)은 목록에 날짜 붙은 id(claude-haiku-4-5-20251001)로만 나오므로 접두어 일치도 허용
        found = not ids or any(i == name or i.startswith(name + "-") for i in ids)
        flag = "OK" if found else "!! 목록에 없음 → config/models.yaml 수정 필요"
        print(f"  config.{key} = {name}  {flag}")

    # 2. 구조화 출력 1회
    print("\n== TopicFrame 호출 ==")
    tf = llm.call(
        role="understand",
        system=load_prompt("understand"),
        user=f"Research topic: {TOPIC}",
        schema=TopicFrame,
    )
    print(tf.model_dump_json(indent=2, ensure_ascii=False))
    issues = tf.check()
    print("\n자체 검증:", "통과" if not issues else issues)

    # 3. 기록
    summary = log.finish("ok", smoke=True)
    log.save("topic_frame", tf)
    print("\n== 비용·시간 ==")
    print(summary)
    print("로그 폴더:", log.dir)
    return 0 if not issues else 2


if __name__ == "__main__":
    sys.exit(main())
