"""LLM-judge — 끝난 실행(runs/<dir>)의 report.md 를 루브릭(eval/rubric.md §B) J1~J7 로 채점한다 (plan.md W4-4.2).

- 파이프라인 **밖**의 사후 작업이다. 실행 중 품질 보장은 Critic 이 하고, judge 는 결정적 지표가 못 재는 질을 보조로 본다.
- 자기 채점 편향 완화 (plan.md §6.2): 실행 모델과 다른 상위 모델(`llm.judge_model`), 항목마다 리포트 문장 인용 강제,
  결정적 지표(cost.json checks)를 프롬프트에 넣고 "모순이면 지표를 따르라" 고 지시. 그리고 코드에서 모순을 다시 잡아
  `flags` 로 남긴다 — 점수를 고치지는 않고 표시만 한다 (judge 가 지표를 무시했는지 사람이 볼 수 있게).
- 결과는 그 실행 폴더에 `judge.json` (점수·인용·비용), `judge_events.jsonl` (LLM 호출 기록) 으로 남는다.
  원 실행의 events.jsonl·cost.json 은 건드리지 않는다 — ablation 의 비용 비교에 judge 비용이 섞이면 안 된다.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import Settings, load_prompt
from .llm import LLM
from .runlog import RunLogger
from .schemas import JUDGE_ITEMS, JudgeResult

MAX_REPORT_CHARS = 150_000   # ~40k 토큰. 리포트는 60~90k 자 — 넘으면 Evidence Table 뒷부분이 잘린다 (notes 에 기록)


def _checks_block(checks: dict[str, Any]) -> str:
    """결정적 지표를 judge 가 읽을 표로. 없는 키는 '-'."""
    def frac(a: str, b: str) -> str:
        return f"{checks.get(a, '-')}/{checks.get(b, '-')}"
    rate = checks.get("citation_verified_rate")
    return "\n".join([
        f"- citation_verified_rate: {'-' if rate is None else f'{rate:.0%}'} ({frac('citations_verified', 'citations_total')})",
        f"- claims_with_source / claims_total: {frac('claims_with_source', 'claims_total')}",
        f"- sub_rqs_covered (evidence >= 3) / sub_rqs: {frac('sub_rqs_covered', 'sub_rqs')}",
        f"- gaps_with_2_evidence / gaps: {frac('gaps_with_2_evidence', 'gaps')}",
        f"- conflicts_with_hypothesis / conflicts: {frac('conflicts_with_hypothesis', 'conflicts')}",
    ])


def consistency_flags(result: JudgeResult, checks: dict[str, Any]) -> list[str]:
    """judge 점수가 결정적 지표와 모순되는 곳을 표시한다 (rubric: 모순이면 결정적 지표가 우선).
    점수는 바꾸지 않는다 — 표시만. 기준은 보수적으로: 지표가 목표(goals.md) 미달인데 4점 이상이면 모순."""
    score = {it.id: it.score for it in result.items}
    flags = []

    def ratio(a: str, b: str) -> float | None:
        x, y = checks.get(a), checks.get(b)
        return None if x is None or not y else x / y

    cov = ratio("sub_rqs_covered", "sub_rqs")
    if cov is not None and cov < 0.8 and score.get("J2", 0) >= 4:
        flags.append(f"J2={score['J2']} but sub-RQ coverage {cov:.0%} < 80%")
    gap_ok = ratio("gaps_with_2_evidence", "gaps")
    if gap_ok is not None and gap_ok < 1.0 and score.get("J5", 0) >= 4:
        flags.append(f"J5={score['J5']} but only {gap_ok:.0%} of gaps have >= 2 evaluated sources")
    cite = checks.get("citation_verified_rate")
    if cite is not None and cite < 1.0 and score.get("J3", 0) >= 4:
        flags.append(f"J3={score['J3']} but citation_verified_rate {cite:.0%} < 100%")
    hyp = ratio("conflicts_with_hypothesis", "conflicts")
    if hyp is not None and hyp < 1.0 and score.get("J4", 0) >= 4:
        flags.append(f"J4={score['J4']} but {hyp:.0%} of conflicts have a hypothesis")
    return flags


def judge_run(run_dir: Path, settings: Settings, *, model: str | None = None,
              client: Any | None = None) -> dict[str, Any]:
    """한 실행을 채점해 judge.json 을 쓰고 그 내용을 돌려준다. report.md 가 없으면(미완주) ValueError.
    client 는 테스트용 가짜 Anthropic 클라이언트 주입 (tests/test_judge.py)."""
    report_f, cost_f = run_dir / "report.md", run_dir / "cost.json"
    if not report_f.exists():
        raise ValueError(f"{run_dir.name}: report.md 없음 (완주하지 않은 실행은 채점하지 않는다)")
    cost = json.loads(cost_f.read_text(encoding="utf-8")) if cost_f.exists() else {}
    checks = cost.get("checks") or {}
    report = report_f.read_text(encoding="utf-8")
    notes: list[str] = []
    if len(report) > MAX_REPORT_CHARS:
        report = report[:MAX_REPORT_CHARS] + "\n\n[... truncated for grading ...]"
        notes.append(f"report truncated to {MAX_REPORT_CHARS} chars")

    model = model or settings.llm.judge_model
    log = RunLogger(run_dir.name, "judge", into=run_dir, prefix="judge_")
    llm = LLM(settings, log, client=client)
    system = load_prompt("judge")
    user = (
        "Deterministic metrics (computed by code — ground truth):\n" + _checks_block(checks) +
        f"\n- run status: {cost.get('status', '-')}, llm_calls: {cost.get('llm_calls', '-')}, "
        f"cost_usd: {cost.get('cost_usd', '-')}\n\n"
        "Research brief (Markdown):\n\n" + report
    )
    issues: list[str] = []
    result: JudgeResult | None = None
    for attempt in range(2):                       # 결정적 검증 실패(항목 누락 등) 시 1회 되먹임 — nodes.checked_call 과 같은 규약
        prompt = user if not issues else user + "\n\nYour previous answer failed these checks:\n- " + "\n- ".join(issues) + "\nFix and return the complete object."
        result = llm.call(role="judge", system=system, user=prompt, schema=JudgeResult, model=model,
                          max_tokens=settings.llm.node_max_tokens)
        issues = result.check()
        log.event("judge_check", attempt=attempt + 1, issues=issues)
        if not issues:
            break
    assert result is not None
    if issues:
        notes.append(f"unresolved checks: {issues}")

    out = {
        "model": model,
        "scores": {it.id: it.score for it in result.items},
        "mean": result.mean,
        "items": [{"id": it.id, "name": JUDGE_ITEMS[it.id], "score": it.score, "quote": it.quote, "reason": it.reason}
                  for it in sorted(result.items, key=lambda x: x.id)],
        "overall_comment": result.overall_comment,
        "flags": consistency_flags(result, checks),
        "notes": notes,
        "cost_usd": round(log.cost_usd, 4),
        "llm_calls": log.llm_calls,
        "elapsed_sec": round(log.elapsed_min * 60, 1),
    }
    (run_dir / "judge.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    log.event("judge_end", mean=out["mean"], flags=out["flags"], cost_usd=out["cost_usd"])
    return out


def judgeable_runs(runs_dir: Path, *, mode: str | None = None, since: str = "", force: bool = False) -> list[Path]:
    """report.md 가 있고(완주) 아직 judge.json 이 없는 실행 폴더. force 면 이미 채점한 것도 포함."""
    out = []
    for d in sorted(runs_dir.iterdir()):
        if not d.is_dir() or not (d / "report.md").exists() or d.name < since:
            continue
        parts = d.name.split("_", 2)
        if mode and (len(parts) < 2 or parts[1] != mode):
            continue
        if (d / "judge.json").exists() and not force:
            continue
        out.append(d)
    return out
