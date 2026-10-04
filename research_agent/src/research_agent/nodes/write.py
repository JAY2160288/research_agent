"""Writer — RunState → ResearchBrief + 마크다운 (plan.md §3.2 마지막 행).

구조 섹션(1~6)은 상태에서 **결정적으로** 조립한다. LLM 은 요약(한국어)과 한계 목록만 쓴다 (BriefText).
Critic 미달 항목과 노드 노트는 한계 섹션에 자동으로 붙는다 — 상한 도달 시에도 실패로 죽지 않고 솔직하게 기록 (goals.md O1, §3.3).
"""

from __future__ import annotations

from ..report import post_checks, render_markdown
from ..schemas import BriefText, ResearchBrief, RunState
from . import NodeContext, checked_call


def run(state: RunState, ctx: NodeContext) -> None:
    assert all(x is not None for x in (state.topic_frame, state.plan, state.evidence, state.synthesis, state.gaps))
    syn, gaps = state.synthesis, state.gaps
    assert syn is not None and gaps is not None and state.topic_frame is not None
    last = state.critiques[-1] if state.critiques else None
    user = (
        f"Topic (original): {state.topic_frame.original_topic}\n"
        f"Research question: {state.topic_frame.research_question}\n\n"
        "Consensus:\n" + "\n".join(f"- {c.statement}" for c in syn.consensus) +
        "\n\nConflicts:\n" + "\n".join(f"- {c.claim} (hypothesis: {c.hypothesis_for_conflict})" for c in syn.conflicts) +
        "\n\nConditional:\n" + "\n".join(f"- {c.statement}" for c in syn.conditional) +
        f"\n\nCoverage note: {syn.coverage_note}\n\n"
        "Gaps:\n" + "\n".join(f"- {g.description} → {g.proposed_rq}" for g in gaps.gaps) +
        "\n\nQuality-gate findings (deterministic):\n" +
        ("\n".join(f"- {i}" for i in last.deterministic_issues) if last and last.deterministic_issues else "- all checks passed") +
        f"\n\nEvidence base: {len(state.evidence.items)} evaluated papers out of {len(state.papers)} candidates."  # type: ignore[union-attr]
    )
    text, issues = checked_call(ctx, role="write", schema=BriefText, user=user, check=lambda t: t.check())
    if issues:
        state.notes.append(f"write: unresolved checks {issues}")

    limitations = list(text.limitations) + [f"[auto] {n}" for n in state.notes]
    brief = ResearchBrief(
        topic_frame=state.topic_frame, plan=state.plan, evidence=state.evidence,  # type: ignore[arg-type]
        synthesis=syn, gaps=gaps, limitations=limitations, executive_summary=text.executive_summary,
    )
    state.brief = brief
    ctx.log.save("brief", brief)
    ctx.log.save("report.md", render_markdown(brief, state.papers))
    ctx.log.event("node_check", node="write", attempt=1, issues=issues,
                  checks=post_checks(brief, state.papers, ctx.settings.tools.min_evidence_per_subrq, ctx.settings.tools.min_relevance))
