"""그래프 러너 — 프레임워크 없이 직접 구현 (plan.md ADR-1).

노드 순서는 NODES 리스트 하나로 정의한다. W2 에서 노드가 하나씩 늘어나고, W3 에서 Critic→Replan 루프가 붙는다.
각 노드 전후를 events.jsonl 에 남겨 Planning/Reflection/Replanning 이 실제로 일어났음을 보여준다 (goals.md O4).
"""

from __future__ import annotations

from typing import Callable

from .config import Settings
from .llm import LLM, CostLimitExceeded, TimeLimitExceeded
from .nodes import NodeContext, critic, evaluate, gap, plan, search, synthesize, understand, write
from .report import post_checks
from .runlog import RunLogger
from .schemas import RunState
from .tools import Tools

Node = Callable[[RunState, NodeContext], None]

NODES: list[tuple[str, Node]] = [
    ("understand", understand.run),
    ("plan", plan.run),
    ("search", search.run),
    ("evaluate", evaluate.run),
    ("synthesize", synthesize.run),
    ("gap", gap.run),
    ("critic", critic.run),      # W2: 결정적 검사만 기록. W3: 미달 시 replan → search 로 되돌아가는 루프
    ("write", write.run),
]


def run_graph(topic: str, settings: Settings, *, use_cache: bool = True,
              until: str | None = None) -> tuple[RunState, RunLogger]:
    """노드를 순서대로 실행. `until` 을 주면 그 노드까지만 (개발 중 부분 실행용)."""
    log = RunLogger(topic, "graph")
    ctx = NodeContext(settings=settings, llm=LLM(settings, log), tools=Tools(settings, log, use_cache=use_cache), log=log)
    state = RunState(topic=topic)
    status = "ok"
    try:
        for name, fn in NODES:
            log.event("node_start", node=name)
            fn(state, ctx)
            log.event("node_end", node=name)
            if until == name:
                status = f"partial:{name}"
                break
    except (CostLimitExceeded, TimeLimitExceeded) as e:
        status = "limit_exceeded"
        log.event("limit_exceeded", error=str(e))
    log.save("state", state)
    log.save("papers", {k: v.model_dump() for k, v in ctx.tools.papers.items()})
    checks = (post_checks(state.brief, state.papers, settings.tools.min_evidence_per_subrq, settings.tools.min_relevance)
              if state.brief else {"submitted": False})
    log.finish(status, checks=checks, notes=state.notes, papers_seen=len(ctx.tools.papers),
               critic_rounds=len(state.critiques), replans=state.replan_count)
    return state, log
