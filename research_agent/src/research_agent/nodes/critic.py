"""Critic — 품질 게이트의 결정적 검사 (plan.md §3.3). LLM 없음 (LLM 비판은 W3).

| 검사 | 실패 시 (W3 Replan 의 입력) |
|---|---|
| 인용 검증률 = 100% | 미검증 인용 제거 후 재종합 |
| 모든 claim 에 출처 ≥ 1 | 출처 없는 claim 삭제 또는 재검색 |
| sub-RQ 별 evidence(relevance ≥ min) ≥ min_evidence_per_subrq | 해당 sub-RQ 만 Replan |
| Gap 당 근거 ≥ 2 (평가된 문헌 안에서) | gap 재실행 |
| 상충 결과에 원인 가설 존재 | synthesize 재실행 |

결과는 state.critiques 에 누적된다 — 몇 번째 라운드에 무엇이 걸렸는지가 Reflection 의 증거 (goals.md O4).
"""

from __future__ import annotations

from ..schemas import Critique, RunState
from . import NodeContext


def deterministic_checks(state: RunState, min_relevance: int, min_evidence_per_subrq: int) -> Critique:
    assert state.plan is not None and state.evidence is not None and state.synthesis is not None
    issues: list[str] = []
    actions: list[str] = []
    verified = state.verified_ids()
    evaluated = {e.paper_id for e in state.evidence.items}

    # 1. 인용 검증률
    cited = {i for c in state.synthesis.all_claims() for i in c.evidence_ids}
    if state.gaps:
        cited |= {i for g in state.gaps.gaps for i in g.evidence_ids}
    bad = sorted(cited - verified)
    if bad:
        issues.append(f"unverified citations: {bad[:5]}")
        actions.append("synthesize: remove unverified ids and re-synthesize")

    # 2. claim 출처
    weak = [c.statement[:60] for c in state.synthesis.all_claims() if not c.evidence_ids]
    if weak:
        issues.append(f"claims without source: {len(weak)}")
        actions.append("synthesize: drop or re-ground claims without sources")

    # 3. sub-RQ 커버리지
    uncovered = []
    for sq in state.plan.sub_rqs:
        n = sum(1 for e in state.evidence.items if sq.id in e.sub_rq_ids and e.relevance >= min_relevance)
        if n < min_evidence_per_subrq:
            uncovered.append(sq.id)
            actions.append(f"{sq.id}: only {n} relevant papers — add queries and re-search")
    if uncovered:
        issues.append(f"sub-RQs under-covered: {uncovered}")

    # 4. Gap 근거
    if state.gaps:
        thin = [g.description[:50] for g in state.gaps.gaps if len(set(g.evidence_ids) & evaluated) < 2]
        if thin:
            issues.append(f"gaps with < 2 evaluated evidence: {len(thin)}")
            actions.append("gap: re-run with evidence_ids restricted to evaluated papers")

    # 5. 상충 가설
    nohyp = [c.claim[:50] for c in state.synthesis.conflicts if not c.hypothesis_for_conflict.strip()]
    if nohyp:
        issues.append(f"conflicts without hypothesis: {len(nohyp)}")
        actions.append("synthesize: add a hypothesis for every conflict")

    return Critique(passed=not issues, deterministic_issues=issues, uncovered_sub_rqs=uncovered,
                    weak_claims=weak, actions=actions)


def run(state: RunState, ctx: NodeContext) -> None:
    cfg = ctx.settings.tools
    cr = deterministic_checks(state, cfg.min_relevance, cfg.min_evidence_per_subrq)
    state.critiques.append(cr)
    ctx.log.event("critique", round=len(state.critiques), passed=cr.passed, issues=cr.deterministic_issues,
                  uncovered=cr.uncovered_sub_rqs, actions=cr.actions)
    if not cr.passed:
        state.notes.append(f"critic round {len(state.critiques)}: {cr.deterministic_issues}")
    ctx.log.save(f"critique_{len(state.critiques)}", cr)
