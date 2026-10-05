"""베이스라인: 단일 ReAct 루프 (plan.md §1.1, ablation 조건 A).

LLM 하나가 도구 3개를 자유롭게 부르며 ①~⑥을 한 번에 수행하고, 마지막에 `submit_brief` 도구로
ResearchBrief 스키마를 강제 출력한다. 계획·검증 노드가 따로 없으므로, 최종 구조와 비교할 때
"구조가 품질을 얼마나 끌어올리는가" 를 보여주는 기준점이 된다.

사후 결정적 검사(실존 인용·주장-출처 연결)는 똑같이 적용하되, 통과 못 해도 재시도하지 않고
결과를 그대로 기록한다 — 그것이 베이스라인의 약점을 측정하는 방법이다.
"""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from .config import Settings, load_prompt
from .llm import LLM, CostLimitExceeded, TimeLimitExceeded, schema_as_tool
from .report import post_checks, render_markdown
from .runlog import RunLogger
from .schemas import ResearchBrief
from .tools import TOOL_DEFS, Tools

SUBMIT = schema_as_tool(ResearchBrief, "submit_brief",
                        "Submit the final research brief. Call exactly once when finished.")

TRUNCATED_MSG = ("Your output hit the max_tokens limit and was cut off, so this call was NOT executed. "
                 "Make the brief compact and call submit_brief again in ONE call with ALL fields: "
                 "evidence table 15-25 papers only (the most relevant), finding <= 2 sentences, "
                 "no repetition of abstracts, limitations 3-6 bullets.")


def run_baseline(topic: str, settings: Settings, *, use_cache: bool = True) -> tuple[ResearchBrief | None, RunLogger]:
    log = RunLogger(topic, "baseline")
    llm = LLM(settings, log)
    tools = Tools(settings, log, use_cache=use_cache)
    system = load_prompt("baseline")
    messages: list[dict[str, Any]] = [{"role": "user", "content": f"Research topic: {topic}"}]
    brief: ResearchBrief | None = None
    status = "no_brief"
    max_steps = settings.limits.max_react_steps

    try:
        for step in range(1, max_steps + 1):
            force_submit = step == max_steps
            resp = llm.call_with_tools(
                role="react", system=system, messages=messages, tools=TOOL_DEFS + [SUBMIT],
                tool_choice={"type": "tool", "name": "submit_brief"} if force_submit else None,
            )
            messages.append({"role": "assistant", "content": resp.content})
            tool_uses = [b for b in resp.content if b.type == "tool_use"]
            thoughts = " ".join(b.text for b in resp.content if b.type == "text")
            truncated = resp.stop_reason == "max_tokens"
            log.event("react_step", step=step, thought=thoughts[:500], tools=[t.name for t in tool_uses],
                      truncated=truncated)

            if not tool_uses:
                # 도구 없이 끝내려 함 → 제출 강제
                messages.append({"role": "user", "content": "Call submit_brief now with the complete brief."})
                continue

            results = []
            for tu in tool_uses:
                if truncated:
                    # 잘린 tool_use 의 input 은 불완전 → 실행하지 않고 압축 지시만 돌려준다 (같은 오류 반복 방지)
                    results.append({"type": "tool_result", "tool_use_id": tu.id, "is_error": True, "content": TRUNCATED_MSG})
                elif tu.name == "submit_brief":
                    try:
                        brief = ResearchBrief.model_validate(_unwrap_submit(tu.input))
                        results.append({"type": "tool_result", "tool_use_id": tu.id, "content": "accepted"})
                    except ValidationError as e:
                        err = str(e)[:800]
                        log.event("submit_rejected", error=err)
                        results.append({"type": "tool_result", "tool_use_id": tu.id, "is_error": True,
                                        "content": _schema_feedback(e)})
                else:
                    out = tools.dispatch(tu.name, tu.input)
                    results.append({"type": "tool_result", "tool_use_id": tu.id, "content": out})
            messages.append({"role": "user", "content": results})
            if brief is not None:
                status = "ok"
                break
    except (CostLimitExceeded, TimeLimitExceeded) as e:
        # 상한 초과는 실패가 아니라 측정 결과다 (goals.md O1: 죽지 않고 기록). 베이스라인 약점으로 남긴다.
        status = "limit_exceeded"
        log.event("limit_exceeded", error=str(e))

    # ---- 사후 결정적 검사 (재시도 없음) ----------------------------------
    checks = post_checks(brief, tools.papers, settings.tools.min_evidence_per_subrq, settings.tools.min_relevance) if brief else {"submitted": False}
    if brief:
        log.save("brief", brief)
        log.save("report.md", render_markdown(brief, tools.papers))
    log.save("papers", {k: v.model_dump() for k, v in tools.papers.items()})
    log.finish(status, checks=checks, papers_seen=len(tools.papers), model=settings.llm.model)
    return brief, log


def _unwrap_submit(inp: Any) -> Any:
    """{'brief': {...}} 처럼 한 겹 감싼 제출을 벗긴다 (T2 실행에서 2회 거절 관찰). 그 외는 그대로."""
    if isinstance(inp, dict) and set(inp) == {"brief"} and isinstance(inp["brief"], dict):
        return inp["brief"]
    return inp


def _schema_feedback(e: ValidationError) -> str:
    """누락 필드를 콕 집어 알려 준다. 긴 pydantic 메시지보다 재제출 성공률이 높고 토큰도 적다."""
    errs = e.errors(include_url=False)
    missing = sorted({".".join(str(p) for p in x["loc"]) for x in errs if x["type"] == "missing"})
    other = [f"{'.'.join(str(p) for p in x['loc'])}: {x['msg']}" for x in errs if x["type"] != "missing"][:5]
    parts = []
    if missing:
        parts.append(f"MISSING required fields: {', '.join(missing)}. Resend the COMPLETE brief with these added "
                     "at the top level (no wrapper object); keep everything else the same.")
    if other:
        parts.append("Other errors: " + "; ".join(other))
    return "schema error — " + " ".join(parts) + " Call submit_brief again."
