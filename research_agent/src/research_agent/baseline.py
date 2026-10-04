"""베이스라인: 단일 ReAct 루프 (plan.md §1.1, ablation 조건 A).

LLM 하나가 도구 3개를 자유롭게 부르며 ①~⑥을 한 번에 수행하고, 마지막에 `submit_brief` 도구로
ResearchBrief 스키마를 강제 출력한다. 계획·검증 노드가 따로 없으므로, 최종 구조와 비교할 때
"구조가 품질을 얼마나 끌어올리는가" 를 보여주는 기준점이 된다.

사후 결정적 검사(실존 인용·주장-출처 연결)는 똑같이 적용하되, 통과 못 해도 재시도하지 않고
결과를 그대로 기록한다 — 그것이 베이스라인의 약점을 측정하는 방법이다.
"""

from __future__ import annotations

from typing import Any

from .config import Settings, load_prompt
from .llm import LLM, CostLimitExceeded, TimeLimitExceeded, schema_as_tool
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
                        brief = ResearchBrief.model_validate(tu.input)
                        results.append({"type": "tool_result", "tool_use_id": tu.id, "content": "accepted"})
                    except Exception as e:  # noqa: BLE001
                        err = str(e)[:800]
                        log.event("submit_rejected", error=err)
                        results.append({"type": "tool_result", "tool_use_id": tu.id, "is_error": True,
                                        "content": f"schema error: {err}. Fix and call submit_brief again."})
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
    checks = _post_checks(brief, tools) if brief else {"submitted": False}
    if brief:
        log.save("brief", brief)
        log.save("report.md", render_markdown(brief))
    log.save("papers", {k: v.model_dump() for k, v in tools.papers.items()})
    log.finish(status, checks=checks, papers_seen=len(tools.papers))
    return brief, log


def _post_checks(brief: ResearchBrief, tools: Tools) -> dict[str, Any]:
    known = {pid for pid, p in tools.papers.items() if p.verified}
    cited = {i for c in brief.synthesis.all_claims() for i in c.evidence_ids}
    cited |= {i for g in brief.gaps.gaps for i in g.evidence_ids}
    cited |= {e.paper_id for e in brief.evidence.items}
    verified = cited & known
    claims = brief.synthesis.all_claims()
    return {
        "submitted": True,
        "citations_total": len(cited),
        "citations_verified": len(verified),
        "citation_verified_rate": round(len(verified) / len(cited), 3) if cited else None,
        "claims_total": len(claims),
        "claims_with_source": sum(1 for c in claims if c.evidence_ids),
        "sub_rqs": len(brief.plan.sub_rqs),
        "sub_rqs_covered": sum(1 for s in brief.plan.sub_rqs
                               if sum(1 for e in brief.evidence.items if s.id in e.sub_rq_ids) >= 3),
        "gaps": len(brief.gaps.gaps),
        "unknown_ids": sorted(cited - set(tools.papers)),
    }


def render_markdown(b: ResearchBrief) -> str:
    tf, lines = b.topic_frame, []
    lines += [f"# Research Brief: {tf.original_topic}", "", "## 요약", b.executive_summary, ""]
    lines += ["## 1. 주제 재정의", f"- RQ: {tf.research_question}", f"- 독립변수: {', '.join(tf.variables.independent)}",
              f"- 종속변수: {', '.join(tf.variables.dependent)}", f"- 대상: {tf.variables.population}",
              f"- 핵심 개념: {', '.join(tf.concepts)}", ""]
    lines += ["## 2. 조사 계획", f"전략: {b.plan.search_strategy}", ""]
    for s in b.plan.sub_rqs:
        lines.append(f"- **{s.id}** {s.question}  \n  쿼리: {'; '.join(s.queries)}")
    lines += ["", "## 3. Evidence Table", "", "| id | rel | reli | method | sample | finding | sub-RQ |", "|---|---|---|---|---|---|---|"]
    for e in b.evidence.items:
        lines.append(f"| {e.paper_id} | {e.relevance} | {e.reliability} | {e.method} | {e.sample} | {e.finding} | {','.join(e.sub_rq_ids)} |")
    lines += ["", "## 4. 종합", "### 합의"]
    lines += [f"- {c.statement} [{', '.join(c.evidence_ids)}]" for c in b.synthesis.consensus]
    lines += ["### 상충"]
    for c in b.synthesis.conflicts:
        lines += [f"- **{c.claim}**", f"  - A: {c.side_a.statement} [{', '.join(c.side_a.evidence_ids)}]",
                  f"  - B: {c.side_b.statement} [{', '.join(c.side_b.evidence_ids)}]", f"  - 가설: {c.hypothesis_for_conflict}"]
    lines += ["### 조건부"]
    lines += [f"- {c.statement} [{', '.join(c.evidence_ids)}]" for c in b.synthesis.conditional]
    lines += ["", f"커버리지: {b.synthesis.coverage_note}", "", "## 5. Research Gap"]
    for g in b.gaps.gaps:
        lines += [f"- **{g.description}** [{', '.join(g.evidence_ids)}]", f"  - 제안 RQ: {g.proposed_rq}",
                  f"  - 방법: {g.method}", f"  - 데이터: {g.data}"]
    lines += ["", "## 6. 향후 연구 방향", "(§5 의 제안 RQ 참조)", "", "## 7. 한계와 신뢰도"]
    lines += [f"- {x}" for x in b.limitations]
    return "\n".join(lines) + "\n"
