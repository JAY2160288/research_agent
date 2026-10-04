"""④ Evaluate — 후보 문헌 → EvidenceTable (plan.md §3.2 넷째 행).

- 후보 선별(LLM 없음): sub-RQ 마다 verified 문헌 중 초록 있음 → 피인용 → 최신 순으로 evaluate_per_subrq 편. 합집합을 평가.
- LLM 배치 평가: evaluate_batch 편씩 묶어 Evidence 를 채운다. 초록에 없는 내용은 쓰지 않도록 프롬프트에서 제한.
- 결정적 검증(배치): paper_id 가 배치 안의 id 여야 하고 중복 없음, sub_rq_ids ⊆ 계획의 sub-RQ. 실패 시 1회 재호출.
- 결정적 검증(전체): EvidenceTable.check — 미검증 문헌 참조 금지.
"""

from __future__ import annotations

from ..schemas import Evidence, EvidenceTable, Paper, RunState
from . import NodeContext, checked_call


def select_candidates(state: RunState, per_subrq: int) -> list[Paper]:
    assert state.plan is not None
    chosen: dict[str, Paper] = {}
    for sq in state.plan.sub_rqs:
        pool = [p for p in state.papers.values() if sq.id in p.sub_rq_ids and p.verified]
        pool.sort(key=lambda p: (p.abstract is None, -(p.cited_by_count or 0), -(p.year or 0)))
        for p in pool[:per_subrq]:
            chosen.setdefault(p.id, p)
    return list(chosen.values())


def _render_batch(state: RunState, batch: list[Paper]) -> str:
    tf, plan = state.topic_frame, state.plan
    assert tf is not None and plan is not None
    lines = [f"Research question: {tf.research_question}", "Sub-questions:"]
    lines += [f"  {sq.id}: {sq.question}" for sq in plan.sub_rqs]
    lines.append(f"\nEvaluate each of the following {len(batch)} papers. Return exactly one Evidence item per paper id.\n")
    for p in batch:
        ab = (p.abstract or "(no abstract — judge from title only, reliability <= 2)")[:1200]
        lines += [f"--- id: {p.id}", f"title: {p.title}", f"year: {p.year} | venue: {p.venue or '?'} | cited_by: {p.cited_by_count}",
                  f"found_for: {', '.join(p.sub_rq_ids)}", f"abstract: {ab}", ""]
    return "\n".join(lines)


def _check_batch(table: EvidenceTable, batch_ids: set[str], rq_ids: set[str]) -> list[str]:
    issues = []
    seen = set()
    for e in table.items:
        if e.paper_id not in batch_ids:
            issues.append(f"paper_id not in this batch: {e.paper_id}")
        if e.paper_id in seen:
            issues.append(f"duplicate paper_id: {e.paper_id}")
        seen.add(e.paper_id)
        bad = [r for r in e.sub_rq_ids if r not in rq_ids]
        if bad:
            issues.append(f"{e.paper_id}: unknown sub_rq_ids {bad}")
    missing = batch_ids - seen
    if missing:
        issues.append(f"missing items for: {sorted(missing)[:5]}")
    return issues


def run(state: RunState, ctx: NodeContext) -> None:
    assert state.plan is not None and state.topic_frame is not None
    cfg = ctx.settings.tools
    candidates = select_candidates(state, cfg.evaluate_per_subrq)
    rq_ids = {sq.id for sq in state.plan.sub_rqs}
    items: list[Evidence] = []
    B = max(1, cfg.evaluate_batch)
    for i in range(0, len(candidates), B):
        batch = candidates[i:i + B]
        batch_ids = {p.id for p in batch}
        table, issues = checked_call(
            ctx, role="evaluate", schema=EvidenceTable, user=_render_batch(state, batch),
            check=lambda t, b=batch_ids: _check_batch(t, b, rq_ids),
        )
        items += [e for e in table.items if e.paper_id in batch_ids and e.paper_id not in {x.paper_id for x in items}]
        if issues:
            state.notes.append(f"evaluate batch {i // B + 1}: {issues[:2]}")
    state.evidence = EvidenceTable(items=items)
    issues = state.evidence.check(state.papers)
    if issues:
        state.evidence.items = [e for e in items if state.papers.get(e.paper_id) and state.papers[e.paper_id].verified]
        state.notes.append(f"evaluate: dropped unverified refs {issues[:3]}")
    ctx.log.event("node_check", node="evaluate", attempt=1, issues=issues,
                  candidates=len(candidates), evaluated=len(state.evidence.items))
    ctx.log.save("evidence", state.evidence)
