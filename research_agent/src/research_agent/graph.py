"""그래프 러너 — 프레임워크 없이 직접 구현 (plan.md ADR-1).

    understand → plan → ┌ search → evaluate → synthesize → gap → critic ┐ → write
                        └──────────── replan (미달, 상한 max_replans) ◄──┘

- 루프 본체는 `LOOP` 순서, 라운드마다 `round` 번호와 함께 node_start/node_end 이벤트를 남긴다 —
  Planning(plan) / Reflection(critique) / Replanning(replan) 이 실제로 일어났음을 events.jsonl 로 보여준다 (goals.md O4).
- 재검색 라운드는 Replan 이 고른 sub-RQ 의 새 쿼리만 검색하고, 새 후보만 평가해 기존 Evidence 에 합친다 (비용 절약).
- 상한 도달 시 미달 항목을 state.notes → 리포트 §7 한계에 적고 write 로 넘어간다. 실패로 죽지 않는다 (goals.md O1).
- `graph.critic` = none(ablation B) | deterministic(C) | full(D). `graph.max_replans` = 0 이면 루프 없음.
"""

from __future__ import annotations

from .config import Settings
from .llm import LLM, CostLimitExceeded, TimeLimitExceeded
from .nodes import NodeContext, critic, evaluate, gap, plan, replan, search, synthesize, understand, write
from .report import post_checks
from .runlog import RunLogger
from .schemas import RunState
from .tools import Tools

# `--until` 로 지정할 수 있는 노드 이름 (실행 순서)
NODES: list[str] = ["understand", "plan", "search", "evaluate", "synthesize", "gap", "critic", "replan", "write"]


class _Until(Exception):
    """`--until <node>` 도달 — 정상 부분 종료."""


def _budget_allows_replan(settings: Settings, log: RunLogger) -> bool:
    f = settings.graph.replan_budget_fraction
    return log.elapsed_min < settings.limits.max_minutes * f and log.cost_usd < settings.limits.max_cost_usd * f


def grace_write(state: RunState, ctx: NodeContext) -> bool:
    """비용·시간 상한에 걸렸지만 종합·Gap 이 이미 있으면 write 1회(재시도 포함 2호출)를 허용해 브리프를 남긴다.
    2026-10-04 T1 반복 실행: 34회 호출을 다 하고 write 직전에 10.1분 → 브리프 없이 종료. 그 손실을 막는다."""
    if state.brief is not None or state.synthesis is None or state.gaps is None:
        return False
    ctx.log.event("grace_write", elapsed_min=round(ctx.log.elapsed_min, 2), cost_usd=round(ctx.log.cost_usd, 4))
    state.notes.append(f"run hit the budget limit after {len(state.critiques)} critic round(s); brief written from the last completed synthesis")
    ctx.llm.grace_calls = 2
    try:
        write.run(state, ctx)
        return state.brief is not None
    except Exception as e:  # noqa: BLE001
        ctx.log.event("grace_write_failed", error=str(e)[:300])
        return False
    finally:
        ctx.llm.grace_calls = 0


def run_graph(topic: str, settings: Settings, *, use_cache: bool = True,
              until: str | None = None) -> tuple[RunState, RunLogger]:
    if until is not None and until not in NODES:
        raise ValueError(f"unknown node {until!r}; choose from {NODES}")
    log = RunLogger(topic, "graph")
    ctx = NodeContext(settings=settings, llm=LLM(settings, log), tools=Tools(settings, log, use_cache=use_cache), log=log)
    state = RunState(topic=topic)
    g = settings.graph
    status = "ok"
    rnd = 0

    def step(name: str, fn, **kw) -> None:
        log.event("node_start", node=name, round=rnd)
        fn(state, ctx, **kw)
        log.event("node_end", node=name, round=rnd)
        if until == name:
            raise _Until

    try:
        step("understand", understand.run)
        step("plan", plan.run)
        extra: dict[str, list[str]] | None = None   # 첫 라운드는 계획의 모든 쿼리, 이후는 Replan 쿼리만
        while True:
            step("search", search.run, extra_queries=extra)
            targets = None if rnd == 0 else {it.sub_rq_id for it in state.replans[-1].items}
            step("evaluate", evaluate.run, only_sub_rqs=targets)
            step("synthesize", synthesize.run)
            step("gap", gap.run)
            if g.critic == "none":
                break
            step("critic", critic.run)
            cr = state.critiques[-1]
            if cr.passed:
                break
            unresolved = cr.deterministic_issues + [i.problem for i in cr.llm_issues if i.severity == "major"]
            if state.replan_count >= g.max_replans:
                state.notes.append(f"critic: unresolved after {state.replan_count} replan(s): {unresolved}")
                log.event("replan_limit", replans=state.replan_count, unresolved=unresolved)
                break
            if not _budget_allows_replan(settings, log):  # 완주가 우선 — 남은 예산으로 write 까지 못 가면 루프를 멈춘다
                state.notes.append(f"critic: unresolved, replan skipped for budget ({log.elapsed_min:.1f}/{settings.limits.max_minutes:.0f} min, "
                                   f"${log.cost_usd:.2f}/{settings.limits.max_cost_usd:.2f}): {unresolved}")
                log.event("replan_skipped_budget", elapsed_min=round(log.elapsed_min, 2), cost_usd=round(log.cost_usd, 4))
                break
            step("replan", replan.run)
            extra = state.replans[-1].as_extra_queries()
            rnd += 1
        step("write", write.run)
    except _Until:
        status = f"partial:{until}"
    except (CostLimitExceeded, TimeLimitExceeded) as e:
        status = "limit_exceeded"
        log.event("limit_exceeded", error=str(e))
        if grace_write(state, ctx):   # 종합·Gap 까지 끝난 상태면 브리프를 버리지 않는다
            status = "ok_after_limit"
    except Exception as e:  # noqa: BLE001 — 예상 밖 오류에도 상태·비용을 남기고 정상 종료 (goals.md O1: 죽지 않는다)
        status = "error"
        log.event("error", error=f"{type(e).__name__}: {str(e)[:500]}")
        import traceback
        log.save("traceback.txt", traceback.format_exc())
    log.save("state", state)
    log.save("papers", {k: v.model_dump() for k, v in ctx.tools.papers.items()})
    checks = (post_checks(state.brief, state.papers, settings.tools.min_evidence_per_subrq, settings.tools.min_relevance)
              if state.brief else {"submitted": False})
    log.finish(status, checks=checks, notes=state.notes, papers_seen=len(ctx.tools.papers),
               critic_rounds=len(state.critiques), replans=state.replan_count,
               critic_mode=g.critic, final_critic_passed=(state.critiques[-1].passed if state.critiques else None))
    return state, log
