"""③ Search — ResearchPlan → 후보 문헌 풀 (plan.md §3.2 셋째 행). LLM 없음.

- **OpenAlex 가 모든 sub-RQ 의 주력** (전 분야 + arXiv 프리프린트도 색인). 병렬(search_workers).
  OpenAlex 가 실패한 쿼리(429 — 일일 크레딧 소진, 5xx, 타임아웃)는 **Crossref works 검색으로 폴백** (ADR-8). 결과 구조는 같다.
- arXiv 는 source_pref 가 arxiv/both 인 sub-RQ 의 **보강**. 순차 + arxiv_interval_sec 간격, sub-RQ 당 arxiv_max_queries_per_subrq 개.
  도구가 타임아웃·429·5xx 를 재시도하되(ADR-15), 라운드당 arxiv_time_budget_sec 의 deadline 안에서만 요청·대기한다.
  예산 소진 또는 연속 arxiv_max_failures 회 실패면 이 라운드의 나머지 arXiv 쿼리를 건너뛴다 (circuit breaker) —
  arXiv 가 429·지연을 돌려줘도 파이프라인이 시간 상한 안에 끝나야 한다 (goals.md O1·O7-L1: 평가자 환경의 외부 API 상태에
  결과 구조가 흔들리면 안 됨). 다음 라운드(Replan 재검색)에서는 다시 시도한다.
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

    def _oa(job: tuple[str, str]) -> bool:
        sid, q = job
        try:
            ctx.tools.search_openalex(q, sub_rq_id=sid)
            return True
        except Exception as e:  # noqa: BLE001 — 검색 하나 실패로 전체가 죽지 않게
            ctx.log.event("tool_error", name="search_openalex", query=q, error=str(e)[:200])
            return False

    def _cr(job: tuple[str, str]) -> bool:
        sid, q = job
        try:
            ctx.tools.search_crossref(q, sub_rq_id=sid)
            return True
        except Exception as e:  # noqa: BLE001
            ctx.log.event("tool_error", name="search_crossref", query=q, error=str(e)[:200])
            return False

    with ThreadPoolExecutor(max_workers=max(1, cfg.search_workers)) as ex:
        ok = list(ex.map(_oa, jobs_oa))
        failed = [job for job, good in zip(jobs_oa, ok) if not good]
        if failed:  # OpenAlex 폴백: 실패한 쿼리만 Crossref 로 (ADR-8)
            ctx.log.event("openalex_fallback", failed_queries=len(failed), total=len(jobs_oa))
            cr_ok = list(ex.map(_cr, failed))
            n_cr = sum(cr_ok)
            state.notes.append(f"search: OpenAlex failed for {len(failed)}/{len(jobs_oa)} queries (rate limit or outage); "
                               f"Crossref fallback answered {n_cr}")

    # arXiv 보강: 순차 + 간격. 라운드당 시간 예산(deadline) 을 도구에 넘겨 재시도·대기가 예산을 넘지 않게 하고 (ADR-15),
    # 예산 소진 또는 연속 실패면 나머지 쿼리를 건너뛴다. 최악의 경우에도 이 라운드의 arXiv 시간 ≈ 예산.
    def _disable(reason: str, done: int, failures: int) -> None:
        skipped = len(jobs_ax) - done
        ctx.log.event("arxiv_disabled", reason=reason, after_failures=failures, skipped_queries=skipped,
                      budget_sec=cfg.arxiv_time_budget_sec)
        why = (f"time budget {cfg.arxiv_time_budget_sec:.0f}s exhausted" if reason == "time_budget"
               else f"disabled after {failures} failures")
        state.notes.append(f"search: arXiv unavailable ({why}, {skipped} queries skipped); OpenAlex only")

    failures = 0
    deadline = time.monotonic() + cfg.arxiv_time_budget_sec
    for i, (sid, q) in enumerate(jobs_ax):
        if time.monotonic() >= deadline:
            _disable("time_budget", i, failures)
            break
        try:
            ctx.tools.search_arxiv(q, sub_rq_id=sid, deadline=deadline)
            failures = 0
        except Exception as e:  # noqa: BLE001 — 재시도까지 소진한 실패 (TimeoutError = 예산 소진 포함)
            failures += 1
            ctx.log.event("tool_error", name="search_arxiv", query=q, error=str(e)[:200])
            if failures >= cfg.arxiv_max_failures:
                _disable("failures", i + 1, failures)
                break
        if i < len(jobs_ax) - 1:
            time.sleep(cfg.arxiv_interval_sec)

    if extra_queries is None and ctx.tools.include_ids:   # --include: 첫 라운드에 한 번, 모든 sub-RQ 의 후보로 (pinned)
        all_rqs = [sq.id for sq in state.plan.sub_rqs]
        got = [p.id for pid in ctx.tools.include_ids if (p := ctx.tools.include_paper(pid, all_rqs)) is not None]
        ctx.log.event("include_papers", requested=ctx.tools.include_ids, registered=got)
        missing = [pid for pid in ctx.tools.include_ids if pid not in got]
        if missing:
            state.notes.append(f"search: --include papers not found in OpenAlex, skipped: {missing}")

    state.papers = ctx.tools.papers  # 같은 객체 공유 — evaluate 가 verified 플래그를 그대로 본다
    counts = {sq.id: sum(1 for p in state.papers.values() if sq.id in p.sub_rq_ids) for sq in state.plan.sub_rqs}
    short = [f"{sid}: {n} < {cfg.search_min_per_subrq}" for sid, n in counts.items() if n < cfg.search_min_per_subrq]
    ctx.log.event("node_check", node="search", attempt=1, issues=short, counts=counts,
                  replan_queries=sum(len(v) for v in (extra_queries or {}).values()) if extra_queries is not None else None)
    if short and extra_queries is None:  # 재검색 라운드에서는 같은 노트를 또 쌓지 않는다 — 최종 판정은 Critic 몫
        state.notes.append(f"search: candidate shortfall {short}")
