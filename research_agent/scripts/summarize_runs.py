"""runs/ 아래 모든 실행의 cost.json 을 표로 모은다 (plan.md §6.2 결정적 지표).

실행:  uv run python scripts/summarize_runs.py [--mode baseline|graph] [--md]
  --md  : 마크다운 표로 출력 (design.md 에 붙여넣기용)
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
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
