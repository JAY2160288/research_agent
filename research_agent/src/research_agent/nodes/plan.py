"""② Plan — TopicFrame → ResearchPlan (sub-RQ 3~6, 각 쿼리 2~4) (plan.md §3.2 둘째 행).

입력: state.topic_frame
출력: state.plan
결정적 검증: sub-RQ id 중복 없음, 쿼리 수 2~4, sub-RQ 간 쿼리 중복률 < 50% (ResearchPlan.check)
"""

from __future__ import annotations

from ..schemas import ResearchPlan, RunState
from . import NodeContext, checked_call


def run(state: RunState, ctx: NodeContext) -> None:
    assert state.topic_frame is not None, "plan requires topic_frame"
    tf = state.topic_frame
    user = (
        "Topic frame (JSON):\n" + tf.model_dump_json(indent=2, exclude={"original_topic"}) +
        f"\n\nOriginal topic (may be Korean): {tf.original_topic}"
    )
    plan, issues = checked_call(
        ctx, role="plan", schema=ResearchPlan, user=user,
        check=lambda p: p.check(),
    )
    state.plan = plan
    if issues:
        state.notes.append(f"plan: unresolved checks {issues}")
    ctx.log.save("plan", plan)
