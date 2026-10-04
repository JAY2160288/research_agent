"""노드 공통 규약 (plan.md §1.2, §3.2).

- 노드 = `run(state, ctx) -> None` 함수. RunState 를 읽고 자기 필드만 채운다. 자유 텍스트 반환 없음.
- `ctx` 는 LLM·도구·로거 묶음 (NodeContext). 노드는 모델명·단가를 모른다 (config 가 담당).
- `checked_call` 은 "LLM 구조화 호출 → 스키마 자체 검증(check) → 실패 시 이슈를 되먹여 재호출" 의 공통 루프.
  LLM 의 운에 기대지 않고 결정적 검사가 하한을 지킨다 (goals.md O7-L3, ADR-5).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TypeVar

from pydantic import BaseModel

from ..config import Settings, load_prompt
from ..llm import LLM
from ..runlog import RunLogger
from ..tools import Tools

T = TypeVar("T", bound=BaseModel)


@dataclass
class NodeContext:
    settings: Settings
    llm: LLM
    tools: Tools
    log: RunLogger


def checked_call(
    ctx: NodeContext,
    *,
    role: str,
    user: str,
    schema: type[T],
    check: Callable[[T], list[str]],
    max_fix: int = 1,
    prompt_name: str | None = None,
) -> tuple[T, list[str]]:
    """구조화 호출 + 결정적 검증. 검증 이슈가 남으면 이슈 목록을 붙여 최대 max_fix 회 재호출.

    반환: (마지막 결과, 남은 이슈). 이슈가 남아도 결과는 돌려준다 — 죽지 않고 리포트 '한계' 에 적는 것이
    호출자(그래프) 의 책임 (goals.md O1).
    """
    system = load_prompt(prompt_name or role)
    issues: list[str] = []
    obj: T | None = None
    for attempt in range(max_fix + 1):
        prompt = user if not issues else (
            f"{user}\n\nYour previous answer failed these deterministic checks:\n- " + "\n- ".join(issues) +
            "\nFix every item and return the complete object again."
        )
        obj = ctx.llm.call(role=role, system=system, user=prompt, schema=schema,
                           max_tokens=ctx.settings.llm.node_max_tokens)  # 노드 출력은 짧다 — 폭주 출력을 일찍 끊는다
        issues = check(obj)
        ctx.log.event("node_check", node=role, attempt=attempt + 1, issues=issues)
        if not issues:
            break
    assert obj is not None
    return obj, issues
