"""같은 주제를 여러 번 돌린 실행들의 편차를 잰다 (goals.md O7-L3, plan.md W3-3.2).

실행:  uv run python scripts/compare_repeats.py "<topic-slug 일부>" [--mode graph] [--since 20261004T113000Z] [--md]

달라지면 안 되는 것(결정적 지표: 인용 검증률, claim 출처율, sub-RQ 커버리지, 스키마 통과)이 모든 실행에서 같은지,
달라져도 되는 것(선택 문헌, Gap 내용, 비용·시간)이 얼마나 흔들리는지를 한 표로 보여준다.
Gap 겹침은 Gap 의 근거 문헌 id 집합으로 잰다 (실행 간 Jaccard) — 문장은 달라도 같은 문헌 조합을 가리키면 같은 Gap 으로 본다.
"""

from __future__ import annotations

import argparse
import json
import statistics
from itertools import combinations
from pathlib import Path

from research_agent.config import RUNS_DIR


def load(slug_part: str, mode: str, since: str = "") -> list[dict]:
    rows = []
    for d in sorted(RUNS_DIR.iterdir()):
        if not d.is_dir() or f"_{mode}_" not in d.name or slug_part not in d.name or d.name < since:
            continue
        cost_f, brief_f = d / "cost.json", d / "brief.json"
        if not cost_f.exists() or not brief_f.exists():
            continue
        c = json.loads(cost_f.read_text(encoding="utf-8"))
        b = json.loads(brief_f.read_text(encoding="utf-8"))
        ck = c.get("checks") or {}
        rows.append({
            "run": d.name.split("_", 1)[0],
            "status": c.get("status"),
            "cost": c.get("cost_usd", 0.0),
            "min": c.get("elapsed_sec", 0) / 60,
            "calls": c.get("llm_calls"),
            "cite_ok": ck.get("citation_verified_rate"),
            "claim_src": (ck.get("claims_with_source"), ck.get("claims_total")),
            "subrq": (ck.get("sub_rqs_covered"), ck.get("sub_rqs")),
            "gaps": ck.get("gaps"),
            "gaps_ok": ck.get("gaps_with_2_evidence"),
            "critic": c.get("critic_rounds"),
            "replans": c.get("replans"),
            "final_pass": c.get("final_critic_passed"),
            "cited_ids": {i for cl in _claims(b) for i in cl["evidence_ids"]} | {e["paper_id"] for e in b["evidence"]["items"]},
            "gap_sets": [frozenset(g["evidence_ids"]) for g in b["gaps"]["gaps"]],
            "gap_rqs": [g["proposed_rq"] for g in b["gaps"]["gaps"]],
        })
    return rows


def _claims(b: dict) -> list[dict]:
    s = b["synthesis"]
    out = list(s["consensus"]) + list(s["conditional"])
    for c in s["conflicts"]:
        out += [c["side_a"], c["side_b"]]
    return out


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if (a | b) else 1.0


def gap_overlap(x: list[frozenset], y: list[frozenset]) -> float:
    """실행 x 의 Gap 중 실행 y 에 근거 집합이 절반 이상 겹치는 Gap 이 있는 비율 (양방향 평균)."""
    def one(p, q):
        return sum(1 for g in p if any(jaccard(set(g), set(h)) >= 0.5 for h in q)) / len(p) if p else 0.0
    return (one(x, y) + one(y, x)) / 2


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--mode", default="graph")
    ap.add_argument("--since", default="", help="이 타임스탬프(폴더명 접두) 이후 실행만. 예: 20261004T113000Z")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    rows = load(a.slug, a.mode, a.since)
    if len(rows) < 2:
        print(f"need >= 2 runs, found {len(rows)}")
        return

    cols = ["run", "status", "cost", "min", "calls", "cite_ok", "claim_src", "subrq", "gaps", "gaps_ok", "critic", "replans", "final_pass"]
    fmt = {"cost": lambda v: f"${v:.3f}", "min": lambda v: f"{v:.1f}", "cite_ok": lambda v: "-" if v is None else f"{v*100:.0f}%",
           "claim_src": lambda v: f"{v[0]}/{v[1]}", "subrq": lambda v: f"{v[0]}/{v[1]}"}
    table = [[fmt.get(c, str)(r[c]) if c in fmt else str(r[c]) for c in cols] for r in rows]
    if a.md:
        print("| " + " | ".join(cols) + " |")
        print("|" + "---|" * len(cols))
        for t in table:
            print("| " + " | ".join(t) + " |")
    else:
        w = [max(len(c), *(len(t[i]) for t in table)) for i, c in enumerate(cols)]
        print("  ".join(c.ljust(w[i]) for i, c in enumerate(cols)))
        for t in table:
            print("  ".join(v.ljust(w[i]) for i, v in enumerate(t)))

    # 불변 지표: 모든 실행에서 같아야 함
    invariant = {
        "citation_verified_rate == 1.0": all(r["cite_ok"] == 1.0 for r in rows),
        "claims_with_source == claims_total": all(r["claim_src"][0] == r["claim_src"][1] for r in rows),
        "sub_rqs_covered == sub_rqs": all(r["subrq"][0] == r["subrq"][1] for r in rows),
        "gaps_with_2_evidence == gaps": all(r["gaps_ok"] == r["gaps"] for r in rows),
        "completed (status ok | ok_after_limit)": all(r["status"] in ("ok", "ok_after_limit") for r in rows),
    }
    print("\n불변 지표 (달라지면 안 되는 것):")
    for k, v in invariant.items():
        print(f"  {'PASS' if v else 'FAIL'}  {k}")

    # 편차: 달라져도 되는 것
    costs = [r["cost"] for r in rows]
    mins = [r["min"] for r in rows]
    pairs = list(combinations(range(len(rows)), 2))
    cite_j = [jaccard(rows[i]["cited_ids"], rows[j]["cited_ids"]) for i, j in pairs]
    gap_o = [gap_overlap(rows[i]["gap_sets"], rows[j]["gap_sets"]) for i, j in pairs]
    print("\n편차 (달라져도 되는 것):")
    print(f"  비용   mean ${statistics.mean(costs):.3f}  sd ${statistics.pstdev(costs):.3f}  range ${min(costs):.3f}–${max(costs):.3f}")
    print(f"  시간   mean {statistics.mean(mins):.1f}분  range {min(mins):.1f}–{max(mins):.1f}")
    print(f"  Gap 수 {[r['gaps'] for r in rows]}  · Replan {[r['replans'] for r in rows]}")
    print(f"  인용 문헌 집합 Jaccard (쌍 평균) {statistics.mean(cite_j):.2f}")
    print(f"  Gap 근거집합 겹침 (쌍 평균)        {statistics.mean(gap_o):.2f}")
    print("\nGap 제안 RQ (실행별):")
    for r in rows:
        print(f"  [{r['run']}]")
        for q in r["gap_rqs"]:
            print(f"    - {q[:110]}")


if __name__ == "__main__":
    main()
