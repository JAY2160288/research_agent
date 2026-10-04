"""그래프 러너 — 프레임워크 없이 직접 구현 (plan.md ADR-1).

노드 순서는 NODES 리스트 하나로 정의한다. W2 에서 노드가 하나씩 늘어나고, W3 에서 Critic→Replan 루프가 붙는다.
각 노드 전후를 events.jsonl 에 남겨 Planning/Reflection/Replanning 이 실제로 일어났음을 보여준다 (goals.md O4).
"""

from __future__ import annotations

from typing import Callable

from .config import Settings
from .llm import LLM, CostLimitExceeded, TimeLimitExceeded
from .nodes import NodeContext, plan, understand
from .runlog import RunLogger
from .schemas import RunState
from .tools import Tools

Node = Callable[[RunState, NodeContext], None]

NODES: list[tuple[str, Node]] = [
    ("understand", understand.run),
    ("plan", plan.run),
    # W2: ("search", ...), ("evaluate", ...), ("synthesize", ...), ("gap", ...), ("write", ...)
    # W3: critic → replan 루프
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
    log.finish(status, notes=state.notes, papers_seen=len(ctx.tools.papers))
    return state, log
