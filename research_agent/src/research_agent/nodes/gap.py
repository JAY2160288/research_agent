"""⑥ Gap & Direction — Synthesis + Evidence → GapList (plan.md §3.2 일곱째 행).

- 입력: 종합 결과(합의·상충·조건부·커버리지 노트) + evidence 압축 표. Gap 마다 근거 문헌 2개 이상 (스키마), 제안 RQ·방법·데이터 포함.
- 결정적 검증: evidence_ids 가 평가된 문헌 안에 있음 (GapList.check).
"""

from __future__ import annotations

from ..schemas import GapList, RunState
from . import NodeContext, checked_call
from .synthesize import evidence_digest


def run(state: RunState, ctx: NodeContext) -> None:
    assert state.synthesis is not None and state.evidence is not None and state.topic_frame is not None
    digest, ids = evidence_digest(state, ctx.settings.tools.min_relevance)
    syn = state.synthesis
    user = (
        f"Research question: {state.topic_frame.research_question}\n\n"
        "Synthesis so far (JSON):\n" + syn.model_dump_json(indent=1) +
        f"\n\nEvidence ({len(ids)} papers; cite ONLY these ids as the basis for each gap):\n{digest}"
    )
    gaps, issues = checked_call(
        ctx, role="gap", schema=GapList, user=user,
        check=lambda g: g.check(ids),
    )
    state.gaps = gaps
    if issues:
        state.notes.append(f"gap: unresolved checks {issues[:3]}")
    ctx.log.save("gaps", gaps)
