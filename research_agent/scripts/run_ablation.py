"""ablation 매트릭스 실행기 — 조건 A~D × 주제 (plan.md §6.3, W4-4.1).

실행:
  uv run python scripts/run_ablation.py --topics T1,T2 --conditions D,B,C,A --dry-run      # 계획·OpenAlex 예산만 출력
  uv run python scripts/run_ablation.py --topics T1,T2 --conditions D,B,C,A [--model claude-sonnet-5-5] [--judge]

조건 (plan.md §6.3):  A = baseline ReAct · B = graph, critic none · C = graph, critic deterministic · D = graph, critic full (최종)

공정성·예산 (ADR-9): 한 주제에서 **D 를 먼저** 돌려 TopicFrame·Plan 을 만들고, B·C 는 그 실행의 계획을 `plan_from` 으로
재사용한다. 첫 라운드 검색 쿼리가 완전히 같으므로 검색 캐시가 그대로 맞고(OpenAlex 호출 0), 조건 간 차이는 품질 게이트
차이만 반영한다. D 를 이번에 안 돌리면 같은 주제·언어의 가장 최근 D 실행 계획을 찾아 쓴다.

OpenAlex 는 IP 당 하루 검색 약 100회. 실행 전 추정치를 더해 `--openalex-budget` 을 넘길 것 같으면 그 실행 앞에서 멈춘다
(429 → Crossref 폴백 상태로 돌면 조건 간 비교가 오염된다). 다음 날 같은 명령을 다시 돌리면 끝난 조합은 건너뛴다.

각 실행 폴더에 ablation.json {topic_id, lang, condition, model, plan_from} 을 남긴다 → summarize_runs.py --ablation 이 읽는다.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from research_agent.config import ROOT, RUNS_DIR, GraphConfig, load_settings

CONDITIONS = {
    "A": {"mode": "baseline", "critic": None},
    "B": {"mode": "graph", "critic": "none"},
    "C": {"mode": "graph", "critic": "deterministic"},
    "D": {"mode": "graph", "critic": "full"},
}
# OpenAlex 검색 횟수 추정 (실행당). 계획: sub-RQ ≤6 × 쿼리 ≤4 = 24, Replan 라운드당 sub-RQ 1~3 × 쿼리 ≤3 ≈ 6
EST_PLAN_SEARCHES = 24
EST_REPLAN_SEARCHES = 6
EST_BASELINE_SEARCHES = 10


def load_topics() -> dict[str, dict]:
    raw = yaml.safe_load((ROOT / "eval" / "topics.yaml").read_text(encoding="utf-8"))
    return {t["id"]: t for t in raw["topics"]}


def existing_runs() -> list[tuple[Path, dict]]:
    out = []
    for d in sorted(RUNS_DIR.iterdir()):
        f = d / "ablation.json"
        if f.exists():
            out.append((d, json.loads(f.read_text(encoding="utf-8"))))
    return out


def find_done(topic_id: str, lang: str, cond: str, model: str) -> Path | None:
    """같은 조합의 완주 실행 (가장 최근). 완주 = cost.json status ok/ok_after_limit + report.md."""
    for d, meta in reversed(existing_runs()):
        if (meta.get("topic_id"), meta.get("lang"), meta.get("condition"), meta.get("model")) != (topic_id, lang, cond, model):
            continue
        cost_f = d / "cost.json"
        if cost_f.exists() and json.loads(cost_f.read_text(encoding="utf-8")).get("status") in ("ok", "ok_after_limit") \
                and (d / "report.md").exists():
            return d
    return None


def find_plan_source(topic_id: str, lang: str) -> Path | None:
    """B/C 가 재사용할 계획: 같은 주제·언어의 가장 최근 D 실행 (모델 무관 — 계획은 공유해도 됨)."""
    for d, meta in reversed(existing_runs()):
        if meta.get("topic_id") == topic_id and meta.get("lang") == lang and meta.get("condition") == "D" \
                and (d / "plan.json").exists() and (d / "topic_frame.json").exists():
            return d
    return None


def openalex_credits() -> tuple[int | None, int | None]:
    """(남은 크레딧, 리셋까지 초). OpenAlex 는 응답 헤더로 일일 잔량을 알려준다 (검색 1회 = 10 크레딧, 하루 1000, 00:00 UTC 리셋).
    429 면 잔량 0 과 retry-after. 실패(네트워크 등)면 (None, None). 성공 응답 1회는 크레딧 10 을 쓴다."""
    import httpx
    try:
        r = httpx.get("https://api.openalex.org/works", params={"search": "budget probe", "per-page": 1}, timeout=15)
    except httpx.HTTPError:
        return None, None
    h = r.headers
    remaining = int(h.get("x-ratelimit-remaining", 0)) if "x-ratelimit-remaining" in h else None
    reset = int(h.get("retry-after") or h.get("x-ratelimit-reset") or 0) or None
    return remaining, reset


def estimate(cond: str, max_replans: int, plan_reused: bool) -> int:
    if cond == "A":
        return EST_BASELINE_SEARCHES
    first = 0 if plan_reused else EST_PLAN_SEARCHES
    replans = 0 if cond == "B" else max_replans * EST_REPLAN_SEARCHES
    return first + replans


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--topics", default="T1,T2,T3,T4,T5", help="eval/topics.yaml 의 id, 쉼표 구분")
    ap.add_argument("--conditions", default="D,B,C,A", help="A~D, 쉼표 구분. D 는 항상 먼저 실행된다")
    ap.add_argument("--lang", default="ko", choices=["ko", "en"], help="주제 언어 (T5 는 ko 만 있음)")
    ap.add_argument("--model", default=None, help="실행 모델 (기본 config llm.model). 품질 측정은 claude-sonnet-5-5")
    ap.add_argument("--max-replans", type=int, default=None, help="C/D 의 Replan 상한 (기본 config graph.max_replans)")
    ap.add_argument("--openalex-budget", type=int, default=100, help="이번 세션에서 쓸 OpenAlex 검색 추정 상한")
    ap.add_argument("--no-cache", action="store_true", help="도구 캐시 끄기 (공정성 통제가 깨지므로 보통 쓰지 않는다)")
    ap.add_argument("--force", action="store_true", help="이미 완주한 조합도 다시 실행")
    ap.add_argument("--judge", action="store_true", help="각 실행이 끝나면 바로 LLM-judge 채점")
    ap.add_argument("--dry-run", action="store_true", help="실행하지 않고 계획·예산만 출력")
    ap.add_argument("--wait", action="store_true", help="OpenAlex 잔량이 추정치보다 적으면 일일 리셋(00:00 UTC)까지 기다렸다 시작")
    a = ap.parse_args()

    topics = load_topics()
    base = load_settings()
    model = a.model or base.llm.model
    max_replans = base.graph.max_replans if a.max_replans is None else a.max_replans
    conds = [c.strip().upper() for c in a.conditions.split(",") if c.strip()]
    bad = [c for c in conds if c not in CONDITIONS]
    if bad:
        sys.exit(f"unknown condition {bad}; choose from {list(CONDITIONS)}")
    conds = sorted(set(conds), key=lambda c: "DBCA".index(c))        # D 먼저 (계획 공급), A 는 독립이라 마지막

    # ---- 계획 ------------------------------------------------------------
    jobs = []   # (topic_id, lang, cond, topic_text, plan_source | None | "from-D-in-this-batch", est)
    used = 0
    for tid in [t.strip().upper() for t in a.topics.split(",") if t.strip()]:
        t = topics.get(tid)
        if t is None:
            sys.exit(f"unknown topic {tid}; choose from {list(topics)}")
        text = t.get(a.lang) or t["ko"]
        lang = a.lang if t.get(a.lang) else "ko"
        d_in_batch = "D" in conds and (a.force or find_done(tid, lang, "D", model) is None)
        for cond in conds:
            done = find_done(tid, lang, cond, model)
            if done and not a.force:
                jobs.append((tid, lang, cond, text, None, 0, f"skip (done: {done.name[:16]})"))
                continue
            src = None
            if cond in ("B", "C"):
                src = "D(this batch)" if d_in_batch else find_plan_source(tid, lang)
            est = estimate(cond, max_replans, plan_reused=src is not None)
            jobs.append((tid, lang, cond, text, src, est, "run"))
            used += est

    print(f"model={model}  max_replans={max_replans}  lang={a.lang}  cache={'off' if a.no_cache else 'on'}")
    print(f"{'topic':6} {'lang':4} {'cond':4} {'openalex~':9} {'plan_from':34} note")
    for tid, lang, cond, text, src, est, note in jobs:
        s = src.name[:34] if isinstance(src, Path) else (src or "-")
        print(f"{tid:6} {lang:4} {cond:4} {est:>9} {s:34} {note}")
    n_run = sum(1 for j in jobs if j[6] == "run")
    print(f"\n실행 {n_run}개 · OpenAlex 검색 추정 {used}회 / 예산 {a.openalex_budget}회"
          + ("  ⚠ 예산 초과 — 예산에 닿는 실행 앞에서 멈춘다. 날짜를 나누거나 --topics 를 줄일 것" if used > a.openalex_budget else ""))
    if a.dry_run:
        return

    # ---- OpenAlex 잔량 사전 점검 (추정이 아니라 실제 헤더) ----------------------
    import time
    remaining, reset = openalex_credits()
    need = used * 10
    if remaining is not None:
        print(f"OpenAlex 잔량 {remaining} 크레딧 (= 검색 {remaining // 10}회), 필요 추정 {need}"
              + (f", 리셋까지 {reset // 60}분" if reset else ""))
        if remaining < need and reset:
            if not a.wait:
                sys.exit("잔량 부족. --wait 로 리셋까지 기다리거나 --topics 를 줄일 것 (429 → Crossref 폴백 상태는 조건 비교를 오염시킨다)")
            print(f"--wait: {reset + 30}초 대기 후 시작")
            time.sleep(reset + 30)
            remaining, _ = openalex_credits()
            print(f"리셋 후 잔량 {remaining}")

    # ---- 실행 ------------------------------------------------------------
    from research_agent.baseline import run_baseline
    from research_agent.graph import run_graph
    from research_agent.judge import judge_run

    spent = 0
    d_dirs: dict[tuple[str, str], Path] = {}
    for tid, lang, cond, text, src, est, note in jobs:
        if note != "run":
            continue
        if spent + est > a.openalex_budget:
            print(f"\n[stop] {tid} {cond}: OpenAlex 추정 누적 {spent}+{est} > {a.openalex_budget}. 내일 같은 명령으로 이어서 실행")
            break
        s = load_settings()                      # 실행마다 새 Settings (조건별 graph 설정이 섞이지 않게)
        s.llm.model = model
        spec = CONDITIONS[cond]
        plan_from = d_dirs.get((tid, lang)) if src == "D(this batch)" else src
        print(f"\n=== {tid} [{lang}] {cond} ({spec['mode']}, critic={spec['critic']}, plan_from={plan_from.name[:16] if plan_from else '-'}) ===")
        if spec["mode"] == "baseline":
            brief, log = run_baseline(text, s, use_cache=not a.no_cache)
            ok = brief is not None
        else:
            s.graph = GraphConfig(critic=spec["critic"], max_replans=max_replans,  # type: ignore[arg-type]
                                  replan_budget_fraction=s.graph.replan_budget_fraction)
            state, log = run_graph(text, s, use_cache=not a.no_cache, plan_from=plan_from)
            ok = state.brief is not None
            if cond == "D":
                d_dirs[(tid, lang)] = log.dir
        meta = {"topic_id": tid, "lang": lang, "condition": cond, "model": model, "max_replans": max_replans,
                "plan_from": plan_from.name if plan_from else None, "topic": text}
        (log.dir / "ablation.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        spent += est
        print(f"→ {log.dir.name}  {'완주' if ok else '미완주'}  ${log.cost_usd:.3f} · {log.llm_calls}회 · {log.elapsed_min:.1f}분")
        if a.judge and ok:
            r = judge_run(log.dir, s)
            print(f"   judge mean {r['mean']:.2f} {r['scores']}  ${r['cost_usd']:.3f}" + (f"  ⚠ {r['flags']}" if r["flags"] else ""))
    print(f"\n완료. OpenAlex 추정 사용 {spent}회. 표: uv run python scripts/summarize_runs.py --ablation --md")


if __name__ == "__main__":
    main()
