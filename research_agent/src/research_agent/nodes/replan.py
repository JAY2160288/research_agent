"""Replan — Critic 미달 → 부족한 sub-RQ 의 새 쿼리 (plan.md §1.2 루프, §3.3). Planner 역할의 두 번째 호출.

입력: 마지막 Critique(결정적 이슈 + LLM 지적), 계획(sub-RQ·기존 쿼리), sub-RQ 별 후보/관련 문헌 수
출력: state.replans 에 ReplanPlan 추가, 새 쿼리를 계획의 sub-RQ 에 덧붙임(리포트 §2 에 그대로 드러남), replan_count += 1
결정적 검증: sub_rq_id 가 계획에 있고 쿼리가 기존과 겹치지 않음 (ReplanPlan.check)

items 가 비면 재검색은 없고, graph 가 synthesize·gap 만 비판을 붙여 다시 돌린다.
"""

from __future__ import annotations

import re

from ..schemas import ReplanItem, ReplanPlan, RunState
from . import NodeContext, checked_call

MAX_QUERIES = 3  # sub-RQ 당 재검색 쿼리 상한 (plan.md ADR-7)

_STOP = {"what", "how", "does", "do", "is", "are", "the", "a", "an", "of", "in", "on", "to", "and", "or", "for", "with",
         "by", "among", "between", "which", "that", "this", "their", "its", "effect", "effects", "impact", "affect"}


def fallback_query(question: str) -> str:
    """LLM 없이 sub-RQ 질문에서 뽑은 키워드 쿼리 (불용어 제거, 최대 6단어) + 'empirical study'. Replan 이 비어 오면 쓴다."""
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z0-9\-]*", question) if w.lower() not in _STOP]
    return " ".join(words[:6]).lower() + " empirical study"


def _counts(state: RunState, min_relevance: int) -> dict[str, tuple[int, int]]:
    assert state.plan is not None
    out = {}
    for sq in state.plan.sub_rqs:
        cand = sum(1 for p in state.papers.values() if sq.id in p.sub_rq_ids)
        rel = sum(1 for e in (state.evidence.items if state.evidence else [])
                  if sq.id in e.sub_rq_ids and e.relevance >= min_relevance)
        out[sq.id] = (cand, rel)
    return out


def run(state: RunState, ctx: NodeContext) -> None:
    assert state.plan is not None and state.topic_frame is not None and state.critiques, "replan requires plan + critique"
    cr = state.critiques[-1]
    counts = _counts(state, ctx.settings.tools.min_relevance)
    lines = [f"Research question: {state.topic_frame.research_question}", "", "Sub-questions (queries already used):"]
    for sq in state.plan.sub_rqs:
        c, r = counts[sq.id]
        flag = " <-- flagged" if sq.id in cr.uncovered_sub_rqs else ""
        lines.append(f"  {sq.id}: {sq.question}{flag}\n      candidates={c}, relevant evaluated={r}\n      queries: " +
                     "; ".join(sq.queries))
    lines += ["", f"Critic round {cr.round} findings:"]
    lines += [f"- {x}" for x in cr.feedback_lines()] or ["- (none)"]
    lines += ["Critic actions:"] + [f"- {a}" for a in cr.actions]
    if state.replans:
        lines += ["", "Queries already added by earlier replanning (do not repeat):"]
        lines += [f"- {it.sub_rq_id}: {'; '.join(it.queries)}" for rp in state.replans for it in rp.items]

    required = set(cr.uncovered_sub_rqs)
    rp, issues = checked_call(
        ctx, role="replan", schema=ReplanPlan, user="\n".join(lines),
        check=lambda r: r.check(state.plan, required),  # type: ignore[arg-type]
    )
    if issues:  # 끝까지 틀린 항목은 버리고, 빠진 sub-RQ 는 결정적 fallback 쿼리로 채운다 — 라운드를 비워 보내지 않는다
        by_id = {s.id: s for s in state.plan.sub_rqs}
        kept = []
        for it in rp.items:
            sq = by_id.get(it.sub_rq_id)
            if sq is None:
                continue
            old = {q.strip().lower() for q in sq.queries}
            it.queries = [q for q in it.queries if q.strip().lower() not in old]
            if it.queries:
                kept.append(it)
        for sid in sorted(required - {it.sub_rq_id for it in kept}):
            kept.append(ReplanItem(sub_rq_id=sid, reason="fallback: LLM gave no queries",
                                   queries=[fallback_query(by_id[sid].question)]))
        rp.items = kept
        state.notes.append(f"replan: LLM output incomplete, used fallback ({issues[0][:80]})")

    for it in rp.items:  # 새 쿼리를 계획에 반영 — 최종 리포트 §2 에 재계획 흔적이 남는다
        it.queries = it.queries[:MAX_QUERIES]  # 스키마에 상한을 두면 SDK 가 parse 단계에서 죽는다(2026-10-04 관찰) → 코드에서 자른다
        sq = next(s for s in state.plan.sub_rqs if s.id == it.sub_rq_id)
        sq.queries += [q for q in it.queries if q not in sq.queries]
    state.replans.append(rp)
    state.replan_count += 1
    ctx.log.event("replan", round=state.replan_count, rationale=rp.rationale,
                  queries={it.sub_rq_id: it.queries for it in rp.items})
    ctx.log.save(f"replan_{state.replan_count}", rp)
