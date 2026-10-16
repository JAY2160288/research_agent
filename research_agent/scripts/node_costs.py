"""실행 폴더의 events.jsonl 을 노드별 소요·호출·토큰·비용으로 집계한다 (design.md §1.5 비용·지연 모델).

실행:  uv run python scripts/node_costs.py runs/<실행 폴더> [runs/<다른 폴더> ...] [--md]
       uv run python scripts/node_costs.py --latest [--md]      # runs/ 의 가장 최근 graph 실행
  --md : 마크다운 표 (design.md 에 붙여넣기용)

읽는 법 (AGT06 비용·지연 모델):
  - 지연 ≈ 임계 경로. 노드 소요의 합이 전체 경과와 같으면 노드 간 병렬이 없다는 뜻 (병렬은 노드 안에만).
  - 비용 ≈ Σ 호출 × (입력 × 단가_in + 출력 × 단가_out). 라운드별 합계로 "재검색 라운드가 얼마나 드는가" 를 본다.
  - cache_read/cache_write 가 0 이면 프롬프트 캐시를 쓰지 않은 것.
LLM 없음, 네트워크 없음 — events.jsonl 과 cost.json 만 읽는다.
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

from research_agent.config import RUNS_DIR

ORDER = ["understand", "plan", "search", "evaluate", "synthesize", "gap", "critic", "replan", "write", "react"]


def aggregate(run_dir: Path) -> dict:
    ev = [json.loads(l) for l in (run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    start: dict[tuple[str, int], float] = {}
    dur: dict[str, float] = collections.defaultdict(float)
    runs: dict[str, int] = collections.defaultdict(int)
    tok: dict[str, list] = collections.defaultdict(lambda: [0, 0, 0, 0, 0.0])   # calls, in, out, cache_read, usd
    by_round: dict[str, dict] = collections.defaultdict(lambda: {"usd": 0.0, "sec": 0.0})
    cur_round = 0
    for e in ev:
        k = e.get("kind")
        if k == "node_start":
            cur_round = e.get("round", 0)
            start[(e["node"], cur_round)] = e["t"]
        elif k == "node_end":
            key = (e["node"], e.get("round", 0))
            sec = e["t"] - start.get(key, e["t"])
            dur[e["node"]] += sec
            runs[e["node"]] += 1
            by_round["write" if e["node"] == "write" else f"round{e.get('round', 0)}"]["sec"] += sec
        elif k == "llm_call":
            r = tok[e.get("role", "?")]
            cr, cw = e.get("cache_read") or 0, e.get("cache_write") or 0
            r[0] += 1
            r[1] += (e.get("input_tokens") or 0) + cr + cw
            r[2] += e.get("output_tokens") or 0
            r[3] += cr
            r[4] += e.get("cost_usd") or 0.0
            by_round["write" if e.get("role") == "write" else f"round{cur_round}"]["usd"] += e.get("cost_usd") or 0.0
    elapsed = ev[-1]["t"] if ev else 0.0
    cost_f = run_dir / "cost.json"
    cost = json.loads(cost_f.read_text(encoding="utf-8")) if cost_f.exists() else {}
    nodes = [n for n in ORDER if n in dur or n in tok] + sorted((set(dur) | set(tok)) - set(ORDER))
    rows = [{"node": n, "runs": runs.get(n, 0), "sec": dur.get(n, 0.0), "calls": tok[n][0], "in": tok[n][1],
             "out": tok[n][2], "cache_read": tok[n][3], "usd": tok[n][4]} for n in nodes]
    return {"dir": run_dir.name, "rows": rows, "elapsed": elapsed, "node_sec_sum": sum(dur.values()),
            "by_round": dict(by_round), "stop_reason": cost.get("stop_reason"), "status": cost.get("status"),
            "cost_usd": cost.get("cost_usd")}


def print_report(a: dict, md: bool) -> None:
    print(f"\n{a['dir']}  status={a['status']}  stop_reason={a['stop_reason']}  cost=${a['cost_usd']}")
    cols = ["node", "runs", "sec", "calls", "in", "out", "cache_read", "usd"]
    fmt = {"sec": lambda v: f"{v:.0f}", "in": lambda v: f"{v:,}", "out": lambda v: f"{v:,}", "cache_read": lambda v: f"{v:,}",
           "usd": lambda v: f"${v:.3f}"}
    rows = [{c: fmt.get(c, str)(r[c]) for c in cols} for r in a["rows"]]
    tot = {"node": "합계", "runs": "", "sec": f"{a['node_sec_sum']:.0f}", "calls": str(sum(r["calls"] for r in a["rows"])),
           "in": f"{sum(r['in'] for r in a['rows']):,}", "out": f"{sum(r['out'] for r in a['rows']):,}",
           "cache_read": f"{sum(r['cache_read'] for r in a['rows']):,}", "usd": f"${sum(r['usd'] for r in a['rows']):.3f}"}
    rows.append(tot)
    if md:
        print("| " + " | ".join(cols) + " |")
        print("|" + "---|" * len(cols))
        for r in rows:
            print("| " + " | ".join(r[c] for c in cols) + " |")
    else:
        w = {c: max(len(c), *(len(r[c]) for r in rows)) for c in cols}
        print("  ".join(c.ljust(w[c]) for c in cols))
        for r in rows:
            print("  ".join(r[c].ljust(w[c]) for c in cols))
    print(f"전체 경과 {a['elapsed']:.0f}초 vs 노드 소요 합 {a['node_sec_sum']:.0f}초"
          + ("  → 노드 간 병렬 없음 (임계 경로 = 전체)" if abs(a["elapsed"] - a["node_sec_sum"]) < 5 else ""))
    parts = ", ".join(f"{k} ${v['usd']:.3f}·{v['sec']:.0f}초" for k, v in sorted(a["by_round"].items()))
    print(f"라운드별: {parts}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="*", help="실행 폴더 (runs/...)")
    ap.add_argument("--latest", action="store_true", help="runs/ 의 가장 최근 graph 실행 하나")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    dirs = [Path(d) for d in a.dirs]
    if a.latest:
        cands = sorted(d for d in RUNS_DIR.iterdir() if d.is_dir() and "_graph_" in d.name and (d / "events.jsonl").exists())
        if not cands:
            raise SystemExit("runs/ 에 graph 실행이 없다")
        dirs.append(cands[-1])
    if not dirs:
        ap.error("실행 폴더를 주거나 --latest")
    for d in dirs:
        print_report(aggregate(d), a.md)


if __name__ == "__main__":
    main()
