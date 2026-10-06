"""Critic — 품질 게이트 (plan.md §3.3). 결정적 검사 5종 → 통과 시에만 LLM 비판.

| 검사 | 실패 시 (Replan 의 입력) |
|---|---|
| 인용 검증률 = 100% | 미검증 인용 제거 후 재종합 |
| 모든 claim 에 출처 ≥ 1 | 출처 없는 claim 삭제 또는 재검색 |
| sub-RQ 별 evidence(relevance ≥ min) ≥ min_evidence_per_subrq | 해당 sub-RQ 만 Replan |
| Gap 당 근거 ≥ 2 (평가된 문헌 안에서) | gap 재실행 |
| 상충 결과에 원인 가설 존재 | synthesize 재실행 |
| 종합의 깊이·논리 (LLM 비판, `graph.critic: full`) | major 이슈가 있으면 미통과 → Replan |

결과는 state.critiques 에 라운드별로 누적된다 — 몇 번째 라운드에 무엇이 걸렸고 Replan 뒤 풀렸는지가
Reflection 의 증거 (goals.md O4). 미달 노트는 루프가 끝난 뒤 graph 가 최종 라운드 기준으로만 남긴다
(중간 라운드에서 걸렸다가 풀린 항목이 리포트 한계에 남지 않도록).
"""

from __future__ import annotations

from ..schemas import Critique, LLMCritique, RunState
from . import NodeContext, checked_call
from .synthesize import evidence_digest


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


def _render_for_llm(state: RunState, min_relevance: int) -> str:
    assert state.topic_frame is not None and state.plan is not None and state.synthesis is not None and state.gaps is not None
    digest, ids = evidence_digest(state, min_relevance)
    return (
        f"Research question: {state.topic_frame.research_question}\n"
        "Sub-questions:\n" + "\n".join(f"  {sq.id}: {sq.question}" for sq in state.plan.sub_rqs) +
        f"\n\nEvidence table ({len(ids)} papers with relevance >= {min_relevance}):\n{digest}" +
        "\n\nSynthesis (JSON):\n" + state.synthesis.model_dump_json(indent=1) +
        "\n\nGaps (JSON):\n" + state.gaps.model_dump_json(indent=1)
    )


def llm_critique(state: RunState, ctx: NodeContext) -> LLMCritique:
    """결정적 검사를 통과한 상태에 대한 LLM 비판. sub_rq_id 가 계획에 없는 지적은 되먹여 재호출."""
    assert state.plan is not None
    rq_ids = {sq.id for sq in state.plan.sub_rqs}
    out, issues = checked_call(
        ctx, role="critic", schema=LLMCritique, user=_render_for_llm(state, ctx.settings.tools.min_relevance),
        check=lambda c: c.check(rq_ids),
    )
    if issues:  # 끝까지 틀린 sub_rq_id 는 버린다 — 비판 자체는 살림
        out.issues = [i for i in out.issues if i.sub_rq_id is None or i.sub_rq_id in rq_ids]
    return out


def run(state: RunState, ctx: NodeContext) -> None:
    cfg = ctx.settings.tools
    cr = deterministic_checks(state, cfg.min_relevance, cfg.min_evidence_per_subrq)
    cr.round = len(state.critiques) + 1
    if cr.passed and ctx.settings.graph.critic == "full":
        llm = llm_critique(state, ctx)
        cr.llm_ran = True
        cr.llm_issues = llm.issues
        # 같은 sub-RQ 를 이미 재검색했는데도 같은 'search' 지적이 남으면 문헌 자체가 없는 것 — 다시 돌아도 못 고친다.
        # 한계로 기록하고 통과시킨다 (2026-10-04 T1: rq2 "실험 연구 없음" 을 3라운드 연속 major → 10분 상한 초과).
        searched = {it.sub_rq_id for rp in state.replans for it in rp.items}
        persisting = [i for i in llm.major if i.sub_rq_id in searched and i.action.lower().startswith("search")]
        actionable = [i for i in llm.major if i not in persisting]
        if actionable:
            cr.passed = False
            cr.actions += [i.action for i in actionable]
            cr.uncovered_sub_rqs = sorted({i.sub_rq_id for i in actionable if i.sub_rq_id and i.action.startswith("search")})
        elif persisting:
            # problem 은 스키마상 "한 문장" — 자르지 않는다. 160자에서 자르자 리포트 §7 [auto] 항목이 문장 중간에서 끊겼음 (2026-10-06 T3 D, judge J7 지적)
            state.notes.append("critic: major issue(s) persist after re-search, recorded as limitation: " +
                               " | ".join(f"{i.sub_rq_id}: {i.problem}" for i in persisting))
            ctx.log.event("critic_persisting", sub_rqs=sorted({i.sub_rq_id for i in persisting if i.sub_rq_id}))
    state.critiques.append(cr)
    ctx.log.event("critique", round=cr.round, passed=cr.passed, issues=cr.deterministic_issues, llm_ran=cr.llm_ran,
                  llm_major=[i.problem for i in cr.llm_issues if i.severity == "major"],
                  llm_minor=[i.problem for i in cr.llm_issues if i.severity == "minor"],
                  uncovered=cr.uncovered_sub_rqs, actions=cr.actions)
    ctx.log.save(f"critique_{cr.round}", cr)
