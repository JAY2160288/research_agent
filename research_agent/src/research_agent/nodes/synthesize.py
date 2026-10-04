"""⑤ Synthesize — EvidenceTable → Synthesis (합의 / 상충 / 조건부) (plan.md §3.2 다섯째 행).

- 입력은 relevance ≥ min_relevance 인 evidence 의 압축 표 (id, 연도, 방법, 표본, 결과). 초록 전체는 넣지 않는다 (토큰 상한).
- 결정적 검증: 모든 claim 의 evidence_ids 가 평가된 문헌 안에 있고, 상충마다 원인 가설이 있다 (Synthesis.check).
"""

from __future__ import annotations

from ..schemas import RunState, Synthesis
from . import NodeContext, checked_call


def evidence_digest(state: RunState, min_relevance: int) -> tuple[str, set[str]]:
    assert state.evidence is not None and state.plan is not None
    rows = [e for e in state.evidence.items if e.relevance >= min_relevance]
    rows.sort(key=lambda e: (-e.relevance, -e.reliability))
    lines = []
    for e in rows:
        p = state.papers.get(e.paper_id)
        yr = p.year if p else "?"
        lines.append(f"[{e.paper_id}] ({yr}) rel={e.relevance} reli={e.reliability} | {e.method} | {e.sample or '-'} | "
                     f"{e.finding} | sub-RQ: {','.join(e.sub_rq_ids)}" + (f" | limits: {e.limitations}" if e.limitations else ""))
    return "\n".join(lines), {e.paper_id for e in rows}


def run(state: RunState, ctx: NodeContext) -> None:
    assert state.topic_frame is not None and state.plan is not None and state.evidence is not None
    digest, ids = evidence_digest(state, ctx.settings.tools.min_relevance)
    user = (
        f"Research question: {state.topic_frame.research_question}\n"
        "Sub-questions:\n" + "\n".join(f"  {sq.id}: {sq.question}" for sq in state.plan.sub_rqs) +
        f"\n\nEvidence ({len(ids)} papers; cite ONLY these ids):\n{digest}"
    )
    syn, issues = checked_call(
        ctx, role="synthesize", schema=Synthesis, user=user,
        check=lambda s: s.check(ids),
    )
    state.synthesis = syn
    if issues:
        state.notes.append(f"synthesize: unresolved checks {issues[:3]}")
    ctx.log.save("synthesis", syn)
