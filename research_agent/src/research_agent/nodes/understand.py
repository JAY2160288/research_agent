"""① Understand — 주제 → TopicFrame (plan.md §3.2 첫 행).

입력: state.topic (한국어/영어 자유 텍스트)
출력: state.topic_frame
결정적 검증: concepts ≥ 3, synonyms_en ≥ 3, 독립·종속변수 비어있지 않음 (TopicFrame.check)
"""

from __future__ import annotations

from ..schemas import RunState, TopicFrame
from . import NodeContext, checked_call


def run(state: RunState, ctx: NodeContext) -> None:
    tf, issues = checked_call(
        ctx, role="understand", schema=TopicFrame,
        user=f"Research topic: {state.topic}",
        check=lambda t: t.check(),
    )
    state.topic_frame = tf
    if issues:
        state.notes.append(f"understand: unresolved checks {issues}")
    ctx.log.save("topic_frame", tf)
