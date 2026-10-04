"""③ Search — ResearchPlan → 후보 문헌 풀 (plan.md §3.2 셋째 행). LLM 없음.

- **OpenAlex 가 모든 sub-RQ 의 주력** (전 분야 + arXiv 프리프린트도 색인). 병렬(search_workers).
- arXiv 는 source_pref 가 arxiv/both 인 sub-RQ 의 **보강**. 순차 + arxiv_interval_sec 간격, sub-RQ 당 arxiv_max_queries_per_subrq 개.
  연속 arxiv_max_failures 회 실패하면 이 실행에서는 arXiv 를 끊는다 (circuit breaker) — arXiv 가 429·지연을 돌려줘도
  파이프라인이 시간 상한 안에 끝나야 한다 (goals.md O1·O7-L1: 평가자 환경의 외부 API 상태에 결과 구조가 흔들리면 안 됨).
- 결정적 검증: sub-RQ 당 후보 ≥ search_min_per_subrq. 미달은 state.notes 에 적고 계속 (W3 Critic 의 Replan 대상).
- `extra_queries` 를 주면 그 sub-RQ 만 추가 검색 (Replan 용).
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor

from ..schemas import RunState
from . import NodeContext


def run(state: RunState, ctx: NodeContext, extra_queries: dict[str, list[str]] | None = None) -> None:
    assert state.plan is not None, "search requires plan"
    cfg = ctx.settings.tools
    jobs_oa: list[tuple[str, str]] = []   # (sub_rq_id, query)
    jobs_ax: list[tuple[str, str]] = []
    for sq in state.plan.sub_rqs:
        queries = (extra_queries or {}).get(sq.id) if extra_queries is not None else sq.queries
        n_ax = 0
        for q in queries or []:
            jobs_oa.append((sq.id, q))
            if sq.source_pref in ("arxiv", "both") and n_ax < cfg.arxiv_max_queries_per_subrq:
                jobs_ax.append((sq.id, q))
                n_ax += 1

    def _oa(job: tuple[str, str]) -> int:
        sid, q = job
        try:
            return len(ctx.tools.search_openalex(q, sub_rq_id=sid))
        except Exception as e:  # noqa: BLE001 — 검색 하나 실패로 전체가 죽지 않게
            ctx.log.event("tool_error", name="search_openalex", query=q, error=str(e)[:200])
            return 0

    with ThreadPoolExecutor(max_workers=max(1, cfg.search_workers)) as ex:
        list(ex.map(_oa, jobs_oa))

    failures = 0
    for i, (sid, q) in enumerate(jobs_ax):
        try:
            ctx.tools.search_arxiv(q, sub_rq_id=sid)
            failures = 0
        except Exception as e:  # noqa: BLE001
            failures += 1
            ctx.log.event("tool_error", name="search_arxiv", query=q, error=str(e)[:200])
            if failures >= cfg.arxiv_max_failures:
                skipped = len(jobs_ax) - i - 1
                ctx.log.event("arxiv_disabled", after_failures=failures, skipped_queries=skipped)
                state.notes.append(f"search: arXiv unavailable (disabled after {failures} failures, {skipped} queries skipped); "
                                   "OpenAlex only")
                break
        if i < len(jobs_ax) - 1:
            time.sleep(cfg.arxiv_interval_sec)

    state.papers = ctx.tools.papers  # 같은 객체 공유 — evaluate 가 verified 플래그를 그대로 본다
    counts = {sq.id: sum(1 for p in state.papers.values() if sq.id in p.sub_rq_ids) for sq in state.plan.sub_rqs}
    short = [f"{sid}: {n} < {cfg.search_min_per_subrq}" for sid, n in counts.items() if n < cfg.search_min_per_subrq]
    ctx.log.event("node_check", node="search", attempt=1, issues=short, counts=counts)
    if short:
        state.notes.append(f"search: candidate shortfall {short}")
