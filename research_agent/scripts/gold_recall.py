"""정답 서베이 참고문헌 회수율 (gold reference recall) — ReportBench 방식의 결정적 지표 (plan.md §6.2, ADR-10).

실행:
  uv run python scripts/gold_recall.py [--model claude-sonnet-5-5] [--md] [--refresh]

eval/gold.yaml 의 주제별 정답 서베이 참고문헌(DOI) 을 정답 집합으로 두고, ablation 실행(runs/*/ablation.json) 마다
세 단계에서 그중 몇 편을 건졌는지 센다:
  retrieved = papers.json (검색이 가져온 전체 후보)  →  evaluated = brief.evidence (평가 노드가 선별해 읽은 문헌)
  →  cited = §4 종합 claim + §5 Gap 이 실제로 인용한 문헌
세 숫자의 차이가 "검색이 못 찾은 것" 과 "찾았지만 선별·인용에서 떨어진 것" 을 가른다.

정답 참고문헌은 OpenAlex `referenced_works` 로 한 번 받아 eval/gold_refs.json 에 캐시한다 (주제당 호출 1 + 50편당 1).
캐시가 있으면 네트워크를 쓰지 않는다 — 평가자는 캐시만으로 재계산할 수 있다. `--refresh` 는 다시 받는다.
LLM 비용 0. 결과는 표로만 출력하고 실행 폴더는 건드리지 않는다.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

import yaml

from research_agent.config import ROOT, RUNS_DIR, load_settings

GOLD_F = ROOT / "eval" / "gold.yaml"
CACHE_F = ROOT / "eval" / "gold_refs.json"
OPENALEX = "https://api.openalex.org/works"


def canon(pid: str) -> str:
    """비교용 정규화. Paper.id 는 소문자 DOI 또는 'arxiv:<id>' 인데, OpenAlex 가 색인한 arXiv 프리프린트는
    DOI 10.48550/arxiv.<id> 로 온다 — 둘을 같은 문헌으로 본다. 버전 접미(v2)도 뗀다."""
    p = pid.strip().lower().replace("https://doi.org/", "")
    m = re.match(r"^(?:10\.48550/arxiv\.|arxiv:)(.+)$", p)
    if m:
        return "arxiv:" + re.sub(r"v\d+$", "", m.group(1))
    return p


# ---- 정답 집합 ----------------------------------------------------------------

def load_gold() -> dict[str, list[dict]]:
    return yaml.safe_load(GOLD_F.read_text(encoding="utf-8"))["gold"]


def load_cache() -> dict[str, dict]:
    return json.loads(CACHE_F.read_text(encoding="utf-8")) if CACHE_F.exists() else {}


def fetch_refs(doi: str, mailto: str | None) -> dict:
    """OpenAlex 에서 서베이 1편의 참고문헌 DOI 목록을 받는다. referenced_works 는 OpenAlex id(W…) 라 50개씩 DOI 로 바꾼다."""
    import httpx
    c = httpx.Client(timeout=30, headers={"User-Agent": "research-agent gold_recall"})
    params = {"mailto": mailto} if mailto else {}
    r = c.get(f"{OPENALEX}/https://doi.org/{doi}", params={**params, "select": "id,title,referenced_works"})
    r.raise_for_status()
    w = r.json()
    wids = w.get("referenced_works") or []
    dois: list[str] = []
    for i in range(0, len(wids), 50):
        chunk = "|".join(x.rsplit("/", 1)[-1] for x in wids[i:i + 50])
        rr = c.get(OPENALEX, params={**params, "filter": f"openalex_id:{chunk}", "per-page": 50, "select": "id,doi"})
        rr.raise_for_status()
        dois += [canon(x["doi"]) for x in rr.json()["results"] if x.get("doi")]
        remaining = rr.headers.get("x-ratelimit-remaining")
    print(f"  {doi}: referenced_works {len(wids)} → DOI 있는 것 {len(dois)}"
          + (f"  (OpenAlex 잔량 {remaining})" if wids else ""), file=sys.stderr)
    return {"title": w.get("title"), "n_referenced_works": len(wids), "refs": sorted(set(dois)), "fetched": date.today().isoformat()}


def gold_sets(refresh: bool) -> dict[str, set[str]]:
    """주제 id → 정답 DOI 집합 (서베이가 여럿이면 합집합). 캐시에 없는 서베이만 받는다."""
    gold, cache = load_gold(), load_cache()
    mailto = load_settings().contact_email
    changed = False
    for tid, surveys in gold.items():
        for sv in surveys:
            if refresh or sv["doi"] not in cache:
                cache[sv["doi"]] = fetch_refs(sv["doi"], mailto)
                changed = True
    if changed:
        CACHE_F.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    return {tid: set().union(*(set(cache[sv["doi"]]["refs"]) for sv in surveys)) for tid, surveys in gold.items()}


# ---- 실행별 회수 ---------------------------------------------------------------

def run_ids(d: Path) -> dict[str, set[str]] | None:
    """한 실행 폴더에서 retrieved / evaluated / cited 문헌 id 집합. 완주 전 폴더면 None."""
    brief_f, papers_f = d / "brief.json", d / "papers.json"
    if not brief_f.exists() or not papers_f.exists():
        return None
    brief = json.loads(brief_f.read_text(encoding="utf-8"))
    papers = json.loads(papers_f.read_text(encoding="utf-8"))
    evaluated = {canon(e["paper_id"]) for e in brief["evidence"]["items"]}
    syn = brief["synthesis"]
    claims = list(syn["consensus"]) + list(syn["conditional"]) + [s for cf in syn["conflicts"] for s in (cf["side_a"], cf["side_b"])]
    cited = {canon(i) for c in claims for i in c["evidence_ids"]} | {canon(i) for g in brief["gaps"]["gaps"] for i in g["evidence_ids"]}
    return {"retrieved": {canon(p) for p in papers}, "evaluated": evaluated, "cited": cited}


def latest_runs(model: str | None) -> list[tuple[dict, Path]]:
    """(주제, 조건, 모델) 당 가장 최근 완주 ablation 실행 — summarize_runs.py --ablation 과 같은 선택 규칙."""
    want = model.replace("claude-", "") if model else None
    latest: dict[tuple, tuple[dict, Path]] = {}
    for d in sorted(RUNS_DIR.iterdir()):
        f = d / "ablation.json"
        if not f.exists() or not (d / "report.md").exists():
            continue
        meta = json.loads(f.read_text(encoding="utf-8"))
        m = (meta.get("model") or "").replace("claude-", "")
        if want and m != want:
            continue
        latest[(meta["topic_id"], meta["condition"], m)] = (meta, d)
    return sorted(latest.values(), key=lambda x: (x[0]["topic_id"], x[0]["condition"]))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", help="이 모델의 ablation 실행만 (예: claude-sonnet-5-5)")
    ap.add_argument("--md", action="store_true", help="Markdown 표")
    ap.add_argument("--refresh", action="store_true", help="정답 참고문헌 캐시를 OpenAlex 에서 다시 받는다")
    a = ap.parse_args()

    gold = gold_sets(a.refresh)
    rows = []
    for meta, d in latest_runs(a.model):
        tid = meta["topic_id"]
        if tid not in gold:
            continue
        ids = run_ids(d)
        if ids is None:
            continue
        g = gold[tid]
        row = {"topic": tid, "cond": meta["condition"], "run": d.name[4:8] + "-" + d.name[9:13], "gold": len(g)}
        for stage in ("retrieved", "evaluated", "cited"):
            hit = len(ids[stage] & g)
            row[stage] = f"{hit}/{len(g)} ({hit / len(g):.0%})" if g else "-"
            row["_" + stage] = hit / len(g) if g else None
        row["n_retrieved"] = len(ids["retrieved"])
        rows.append(row)
    if not rows:
        sys.exit("ablation 실행이 없습니다 (runs/*/ablation.json)")

    cols = ["topic", "cond", "run", "gold", "n_retrieved", "retrieved", "evaluated", "cited"]
    _print(cols, rows, a.md)
    print()
    agg_cols = ["cond", "n", "retrieved", "evaluated", "cited"]
    agg = []
    for cond in sorted({r["cond"] for r in rows}):
        rs = [r for r in rows if r["cond"] == cond]
        mean = lambda k: f"{sum(r[k] for r in rs if r[k] is not None) / len(rs):.1%}"
        agg.append({"cond": cond, "n": len(rs), "retrieved": mean("_retrieved"), "evaluated": mean("_evaluated"), "cited": mean("_cited")})
    _print(agg_cols, agg, a.md)


def _print(cols: list[str], rows: list[dict], md: bool) -> None:
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


if __name__ == "__main__":
    main()
