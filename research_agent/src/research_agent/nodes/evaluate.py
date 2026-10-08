"""④ Evaluate — 후보 문헌 → EvidenceTable (plan.md §3.2 넷째 행).

- 후보 선별(LLM 없음): sub-RQ 마다 verified 문헌 중 초록 있음 → 피인용 → 최신 순으로 evaluate_per_subrq 편. 합집합을 평가.
- LLM 배치 평가: evaluate_batch 편씩 묶어 Evidence 를 채운다. 초록에 없는 내용은 쓰지 않도록 프롬프트에서 제한.
- 결정적 검증(배치): paper_id 가 배치 안의 id 여야 하고 중복 없음, sub_rq_ids ⊆ 계획의 sub-RQ. 실패 시 1회 재호출.
- 결정적 검증(전체): EvidenceTable.check — 미검증 문헌 참조 금지.
- 증분 평가(Replan 라운드): 이미 평가한 문헌은 건너뛰고, `only_sub_rqs` 로 지정된 sub-RQ 의 새 후보만 평가해 기존 표에 합친다.
- 배치는 서로 독립이라 `evaluate_workers` 개를 병렬로 호출한다 (2026-10-08). 결과는 배치 순서대로 합쳐 출력이 순차 실행과 같다.
  D 조건 실행에서 evaluate 가 LLM 호출의 절반(8~12회)이었고 순차라 2~3분을 먹었다 — 병렬화는 지표를 바꾸지 않고 시간만 줄인다.
- `--include` 로 고정(pinned)한 문헌은 sub-RQ 당 상한과 무관하게 항상 후보에 들어간다.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from ..schemas import Evidence, EvidenceTable, Paper, RunState
from . import NodeContext, checked_call


def select_candidates(state: RunState, per_subrq: int, exclude: set[str] | None = None,
                      only_sub_rqs: set[str] | None = None) -> list[Paper]:
    """sub-RQ 마다 (고정 → 초록 있음 → 피인용 → 최신) 순으로 per_subrq 편 + 고정 문헌 전부.
    exclude 는 이미 평가한 id, only_sub_rqs 는 재검색 대상."""
    assert state.plan is not None
    exclude = exclude or set()
    chosen: dict[str, Paper] = {}
    for sq in state.plan.sub_rqs:
        if only_sub_rqs is not None and sq.id not in only_sub_rqs:
            continue
        pool = [p for p in state.papers.values() if sq.id in p.sub_rq_ids and p.verified and p.id not in exclude]
        pool.sort(key=lambda p: (not p.pinned, p.abstract is None, -(p.cited_by_count or 0), -(p.year or 0)))
        for p in pool[:per_subrq]:
            chosen.setdefault(p.id, p)
        for p in pool[per_subrq:]:       # 상한 밖이라도 사용자가 고정한 문헌은 평가한다
            if p.pinned:
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


def run(state: RunState, ctx: NodeContext, only_sub_rqs: set[str] | None = None) -> None:
    assert state.plan is not None and state.topic_frame is not None
    cfg = ctx.settings.tools
    prior = list(state.evidence.items) if state.evidence else []
    evaluated = {e.paper_id for e in prior}
    candidates = select_candidates(state, cfg.evaluate_per_subrq, exclude=evaluated, only_sub_rqs=only_sub_rqs)
    rq_ids = {sq.id for sq in state.plan.sub_rqs}
    items: list[Evidence] = prior
    B = max(1, cfg.evaluate_batch)
    batches = [candidates[i:i + B] for i in range(0, len(candidates), B)]
    prompts = [_render_batch(state, b) for b in batches]   # 프롬프트는 state 를 읽으므로 스레드 밖에서 먼저 만든다

    def _one(k: int) -> tuple[EvidenceTable, list[str]]:
        batch_ids = {p.id for p in batches[k]}
        return checked_call(ctx, role="evaluate", schema=EvidenceTable, user=prompts[k],
                            check=lambda t, b=batch_ids: _check_batch(t, b, rq_ids))

    workers = max(1, min(getattr(cfg, "evaluate_workers", 1), len(batches) or 1))
    if workers == 1:
        results = [_one(k) for k in range(len(batches))]
    else:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            results = list(ex.map(_one, range(len(batches))))   # map 은 입력 순서를 지킨다 → 합치는 순서가 순차 실행과 같다
    ctx.log.event("evaluate_batches", batches=len(batches), workers=workers)
    for k, (table, issues) in enumerate(results):
        batch_ids = {p.id for p in batches[k]}
        items += [e for e in table.items if e.paper_id in batch_ids and e.paper_id not in {x.paper_id for x in items}]
        if issues:
            state.notes.append(f"evaluate batch {k + 1}: {issues[:2]}")
    state.evidence = EvidenceTable(items=items)
    issues = state.evidence.check(state.papers)
    if issues:
        state.evidence.items = [e for e in items if state.papers.get(e.paper_id) and state.papers[e.paper_id].verified]
        state.notes.append(f"evaluate: dropped unverified refs {issues[:3]}")
    ctx.log.event("node_check", node="evaluate", attempt=1, issues=issues, candidates=len(candidates),
                  prior=len(prior), evaluated=len(state.evidence.items), only_sub_rqs=sorted(only_sub_rqs or []))
    ctx.log.save("evidence", state.evidence)
