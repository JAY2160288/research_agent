"""노드 공통 규약 (plan.md §1.2, §3.2).

- 노드 = `run(state, ctx) -> None` 함수. RunState 를 읽고 자기 필드만 채운다. 자유 텍스트 반환 없음.
- `ctx` 는 LLM·도구·로거 묶음 (NodeContext). 노드는 모델명·단가를 모른다 (config 가 담당).
- `checked_call` 은 "LLM 구조화 호출 → 스키마 자체 검증(check) → 실패 시 이슈를 되먹여 재호출" 의 공통 루프.
  LLM 의 운에 기대지 않고 결정적 검사가 하한을 지킨다 (goals.md O7-L3, ADR-5).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, TypeVar

from pydantic import BaseModel

from ..config import Settings, load_prompt
from ..llm import LLM
from ..runlog import RunLogger
from ..tools import Tools

T = TypeVar("T", bound=BaseModel)


# 구조화 출력의 문자열 필드에 섞인 "생성 잔해" — JSON 을 다시 쓰려다 남긴 괄호·HTML 줄바꿈·코드펜스.
# 2026-10-06 T3 D (sonnet): coverage_note 끝에 `}</br>Correction: the JSON above must be a single object; see below.</br>{` 가
# 그대로 들어와 리포트 §4 에 노출됨 (judge J4 감점). 스키마 파싱은 통과하므로 결정적 검사가 잡아야 한다 (ADR-5).
_RESIDUE = re.compile(r"</?br\s*/?>|```|^\s*[}\]]|[{\[]\s*$")


def residue_issues(obj: BaseModel, _path: str = "") -> list[str]:
    """모든 문자열 필드(중첩·리스트 포함)를 훑어 잔해가 있는 필드 경로를 돌려준다. 비어 있으면 깨끗함."""
    out: list[str] = []

    def walk(v: Any, path: str) -> None:
        if isinstance(v, str):
            if _RESIDUE.search(v):
                out.append(f"text field '{path}' contains JSON/markup residue (stray braces, <br>, or code fences); "
                           f"write clean prose only")
        elif isinstance(v, dict):
            for k, x in v.items():
                walk(x, f"{path}.{k}" if path else str(k))
        elif isinstance(v, list):
            for i, x in enumerate(v):
                walk(x, f"{path}[{i}]")

    walk(obj.model_dump(), _path)
    return out


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
        issues = check(obj) + residue_issues(obj)      # 노드별 검사 + 공통 잔해 검사
        ctx.log.event("node_check", node=role, attempt=attempt + 1, issues=issues)
        if not issues:
            break
    assert obj is not None
    return obj, issues
