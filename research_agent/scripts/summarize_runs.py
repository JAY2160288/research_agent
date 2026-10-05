"""runs/ 아래 모든 실행의 cost.json 을 표로 모은다 (plan.md §6.2 결정적 지표).

실행:  uv run python scripts/summarize_runs.py [--mode baseline|graph] [--md]
       uv run python scripts/summarize_runs.py --ablation [--all-runs] [--md]
  --md       : 마크다운 표로 출력 (design.md 에 붙여넣기용)
  --ablation : 주제 × 조건(A~D) 매트릭스 + 조건별 평균 (plan.md §6.3). judge.json 이 있으면 J 평균도 붙인다.
               조건은 ablation.json 에서 읽고, 없으면 cost.json 의 mode/critic_mode 로 추정(A=baseline, B=none, C=deterministic, D=full),
               주제는 폴더 slug 를 eval/topics.yaml 과 대조해 찾는다. 기본은 (주제, 조건, 모델) 당 가장 최근 완주 실행 1개.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_agent.config import RUNS_DIR

COLS = ["run", "mode", "status", "cost", "min", "calls", "cites", "cite_ok", "claims", "claim_src", "subrq", "gaps",
        "critic", "replans"]


def load(mode: str | None) -> list[dict]:
    rows = []
    for d in sorted(RUNS_DIR.iterdir()):
        f = d / "cost.json"
        if not f.exists():
            continue
        c = json.loads(f.read_text(encoding="utf-8"))
        ts, m, slug = d.name.split("_", 2)
        if mode and m != mode:
            continue
        ck = c.get("checks") or {}
        rows.append({
            "run": f"{ts[4:8]}-{ts[9:13]} {slug[:28]}",
            "mode": m,
            "status": c.get("status"),
            "cost": f"${c.get('cost_usd', 0):.3f}",
            "min": f"{c.get('elapsed_sec', 0) / 60:.1f}",
            "calls": c.get("llm_calls"),
            "cites": ck.get("citations_total", "-"),
            "cite_ok": _rate(ck.get("citation_verified_rate")),
            "claims": ck.get("claims_total", "-"),
            "claim_src": _frac(ck.get("claims_with_source"), ck.get("claims_total")),
            "subrq": _frac(ck.get("sub_rqs_covered"), ck.get("sub_rqs")),
            "gaps": ck.get("gaps", "-"),
            # 그래프 전용: Critic 라운드 수와 최종 통과 여부, Replan 횟수 (베이스라인은 '-')
            "critic": (f"{c['critic_rounds']}{'✓' if c.get('final_critic_passed') else '✗'}"
                       if c.get("critic_rounds") else "-"),
            "replans": c.get("replans", "-") if m == "graph" else "-",
        })
    return rows


def _rate(x) -> str:
    return "-" if x is None else f"{x * 100:.0f}%"


def _frac(a, b) -> str:
    return "-" if a is None or b is None else f"{a}/{b}"


# ---- ablation 매트릭스 -----------------------------------------------------------

ABL_COLS = ["topic", "cond", "model", "run", "status", "cost", "min", "calls", "cite_ok", "claim_src", "subrq", "gaps_ok",
            "replans", "judge", "flags"]
CRITIC_TO_COND = {"none": "B", "deterministic": "C", "full": "D"}


def _topic_slugs() -> dict[str, str]:
    """slug → topic id (ko/en 둘 다). runlog._slug 와 같은 규칙으로 만든다."""
    import yaml
    from research_agent.config import ROOT
    from research_agent.runlog import _slug
    raw = yaml.safe_load((ROOT / "eval" / "topics.yaml").read_text(encoding="utf-8"))
    return {_slug(t[k]): t["id"] for t in raw["topics"] for k in ("ko", "en") if t.get(k)}


def load_ablation(all_runs: bool) -> list[dict]:
    slugs = _topic_slugs()
    rows = []
    for d in sorted(RUNS_DIR.iterdir()):
        f = d / "cost.json"
        if not f.exists():
            continue
        c = json.loads(f.read_text(encoding="utf-8"))
        ts, m, slug = d.name.split("_", 2)
        meta_f = d / "ablation.json"
        meta = json.loads(meta_f.read_text(encoding="utf-8")) if meta_f.exists() else {}
        cond = meta.get("condition") or ("A" if m == "baseline" else CRITIC_TO_COND.get(c.get("critic_mode", "full"), "?"))
        topic = meta.get("topic_id") or slugs.get(slug, "?")
        if topic == "?" or m not in ("baseline", "graph"):
            continue
        ck = c.get("checks") or {}
        model = meta.get("model") or c.get("model") or _model_from_events(d) or "?"
        j_f = d / "judge.json"
        j = json.loads(j_f.read_text(encoding="utf-8")) if j_f.exists() else None
        rows.append({
            "topic": topic, "cond": cond, "model": model.replace("claude-", ""),
            "run": f"{ts[4:8]}-{ts[9:13]}", "status": c.get("status"),
            "_cost": c.get("cost_usd", 0.0), "cost": f"${c.get('cost_usd', 0):.3f}",
            "_min": c.get("elapsed_sec", 0) / 60, "min": f"{c.get('elapsed_sec', 0) / 60:.1f}",
            "calls": c.get("llm_calls"),
            "_cite": ck.get("citation_verified_rate"), "cite_ok": _rate(ck.get("citation_verified_rate")),
            "_claim": _ratio(ck.get("claims_with_source"), ck.get("claims_total")),
            "claim_src": _frac(ck.get("claims_with_source"), ck.get("claims_total")),
            "_subrq": _ratio(ck.get("sub_rqs_covered"), ck.get("sub_rqs")),
            "subrq": _frac(ck.get("sub_rqs_covered"), ck.get("sub_rqs")),
            "_gaps": _ratio(ck.get("gaps_with_2_evidence"), ck.get("gaps")),
            "gaps_ok": _frac(ck.get("gaps_with_2_evidence"), ck.get("gaps")),
            "replans": c.get("replans", "-") if m == "graph" else "-",
            "_judge": j["mean"] if j else None, "judge": f"{j['mean']:.2f}" if j else "-",
            "flags": len(j["flags"]) if j else "-",
            # 완주 = 브리프까지 썼음. (옛 `--until` 부분 실행은 status 가 ok 였으므로 report.md 로 다시 확인)
            "_done": c.get("status") in ("ok", "ok_after_limit") and (d / "report.md").exists(),
        })
    if not all_runs:   # (주제, 조건, 모델) 당 가장 최근 완주 실행 1개
        latest: dict[tuple, dict] = {}
        for r in rows:
            if r["_done"]:
                latest[(r["topic"], r["cond"], r["model"])] = r
        rows = list(latest.values())
    return sorted(rows, key=lambda r: (r["topic"], r["cond"], r["model"]))


def _model_from_events(d: Path) -> str | None:
    """cost.json 에 model 이 없는 옛 실행: events.jsonl 의 첫 llm_call 에서 읽는다."""
    f = d / "events.jsonl"
    if not f.exists():
        return None
    with f.open(encoding="utf-8") as fh:
        for line in fh:
            if '"llm_call"' in line:
                return json.loads(line).get("model")
    return None


def _ratio(a, b) -> float | None:
    return None if a is None or not b else a / b


def _mean(xs: list) -> str:
    xs = [x for x in xs if x is not None]
    return "-" if not xs else f"{sum(xs) / len(xs):.2f}"


def print_table(cols: list[str], rows: list[dict], md: bool) -> None:
    if md:
        print("| " + " | ".join(cols) + " |")
        print("|" + "---|" * len(cols))
        for r in rows:
            print("| " + " | ".join(str(r[c]) for c in cols) + " |")
    else:
        w = {c: max(len(c), *(len(str(r[c])) for r in rows)) for c in cols}
        print("  ".join(c.ljust(w[c]) for c in cols))
        for r in rows:
            print("  ".join(str(r[c]).ljust(w[c]) for c in cols))


def ablation(md: bool, all_runs: bool) -> None:
    rows = load_ablation(all_runs)
    if not rows:
        print("no runs")
        return
    print_table(ABL_COLS, rows, md)
    # 조건별 평균 — 불변 지표는 비율 평균, 비용·시간·judge 는 산술 평균
    print()
    agg_cols = ["cond", "n", "done", "cost", "min", "cite_ok", "claim_src", "subrq", "gaps_ok", "judge"]
    agg = []
    for cond in sorted({r["cond"] for r in rows}):
        rs = [r for r in rows if r["cond"] == cond]
        agg.append({
            "cond": cond, "n": len(rs), "done": f"{sum(1 for r in rs if r['_done'])}/{len(rs)}",
            "cost": f"${sum(r['_cost'] for r in rs) / len(rs):.3f}", "min": f"{sum(r['_min'] for r in rs) / len(rs):.1f}",
            "cite_ok": _mean([r["_cite"] for r in rs]), "claim_src": _mean([r["_claim"] for r in rs]),
            "subrq": _mean([r["_subrq"] for r in rs]), "gaps_ok": _mean([r["_gaps"] for r in rs]),
            "judge": _mean([r["_judge"] for r in rs]),
        })
    print_table(agg_cols, agg, md)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--ablation", action="store_true", help="주제 × 조건 매트릭스 (ablation.json / judge.json 반영)")
    ap.add_argument("--all-runs", action="store_true", help="--ablation 에서 (주제, 조건, 모델) 당 최근 1개가 아니라 전부")
    a = ap.parse_args()
    if a.ablation:
        ablation(a.md, a.all_runs)
        return
    rows = load(a.mode)
    if not rows:
        print("no runs")
        return
    if a.md:
        print("| " + " | ".join(COLS) + " |")
        print("|" + "---|" * len(COLS))
        for r in rows:
            print("| " + " | ".join(str(r[c]) for c in COLS) + " |")
    else:
        w = {c: max(len(c), *(len(str(r[c])) for r in rows)) for c in COLS}
        print("  ".join(c.ljust(w[c]) for c in COLS))
        for r in rows:
            print("  ".join(str(r[c]).ljust(w[c]) for c in COLS))
    total = sum(float(r["cost"][1:]) for r in rows)
    print(f"\n{len(rows)} runs, total ${total:.3f}")


if __name__ == "__main__":
    main()
