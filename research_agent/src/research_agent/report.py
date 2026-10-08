"""리포트 렌더링과 사후 결정적 지표 — 베이스라인과 그래프가 같은 함수를 쓴다 (ablation 비교의 공정성, plan.md §6.2).

렌더링 원칙 (2026-10-08 개편, plan.md §8):
- LLM 호출 0. `brief.json`·`papers.json`·`cost.json` 만으로 언제든 같은 report.md 를 다시 그릴 수 있다 (`agent render`).
- 인용은 DOI 문자열이 아니라 **번호 [n]** 으로, 끝에 참고문헌 목록. 번호는 문서에 처음 등장하는 순서.
- 맨 위 "한눈에" 카드는 `post_checks` 의 결정적 지표를 그대로 보여준다 — 독자가 첫 줄에서 인용 검증률·커버리지를 확인.
- Evidence Table 은 sub-RQ 별로 나누고 각 머리에 편수·평균 신뢰도·상위 문헌을 요약, 본표는 접는다(<details>).
"""

from __future__ import annotations

from typing import Any

from .schemas import Evidence, Paper, ResearchBrief

FINDING_MAX = 160          # 표 안 finding 길이 상한 (전체는 brief.json)
TOP_PER_SUBRQ = 3          # sub-RQ 머리에 보여줄 상위 문헌 수
AUTO_PREFIX = "[auto] "    # write 노드가 파이프라인 노트에 붙이는 접두어


def post_checks(brief: ResearchBrief, papers: dict[str, Paper], min_evidence_per_subrq: int = 3,
                min_relevance: int = 3) -> dict[str, Any]:
    """plan.md §6.2 의 결정적 지표. LLM 없이 계산. 커버리지는 Critic 과 같은 기준(relevance ≥ min_relevance)."""
    known = {pid for pid, p in papers.items() if p.verified}
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
                               if sum(1 for e in brief.evidence.items
                                      if s.id in e.sub_rq_ids and e.relevance >= min_relevance) >= min_evidence_per_subrq),
        "gaps": len(brief.gaps.gaps),
        "gaps_with_2_evidence": sum(1 for g in brief.gaps.gaps if len(set(g.evidence_ids) & known) >= 2),
        "conflicts": len(brief.synthesis.conflicts),
        "conflicts_with_hypothesis": sum(1 for c in brief.synthesis.conflicts if c.hypothesis_for_conflict.strip()),
        "unknown_ids": sorted(cited - set(papers)),
    }


# ---------------------------------------------------------------- 보조

def _cell(s: str | None, limit: int | None = None) -> str:
    """마크다운 표 셀용: 파이프·개행 제거, 길이 상한."""
    t = (s or "").replace("|", "\\|").replace("\n", " ").strip()
    if limit and len(t) > limit:
        t = t[: limit - 1].rstrip() + "…"
    return t


def _ref_line(pid: str, p: Paper | None) -> str:
    """참고문헌 한 줄: 저자 (연도). 제목. 출처. 링크."""
    if p is None:
        return f"{pid} (메타데이터 없음)"
    authors = ", ".join(p.authors[:3]) + (" et al." if len(p.authors) > 3 else "") if p.authors else "저자 미상"
    year = f" ({p.year})" if p.year else ""
    venue = f" *{p.venue}*." if p.venue else ""
    if p.doi:
        link = f"https://doi.org/{p.doi}"
    elif p.arxiv_id:
        link = f"https://arxiv.org/abs/{p.arxiv_id}"
    else:
        link = p.url or ""
    return f"{authors}{year}. {p.title}.{venue} {link}".strip()


class _Refs:
    """문헌 id → 번호. 문서에 처음 등장하는 순서로 매긴다."""

    def __init__(self) -> None:
        self.order: list[str] = []
        self.num: dict[str, int] = {}

    def n(self, pid: str) -> int:
        if pid not in self.num:
            self.order.append(pid)
            self.num[pid] = len(self.order)
        return self.num[pid]

    def cite(self, ids: list[str]) -> str:
        """[1, 4, 7] — 번호 오름차순, 중복 제거."""
        nums = sorted({self.n(i) for i in ids})
        return "[" + ", ".join(str(x) for x in nums) + "]" if nums else "[근거 없음]"


def _evidence_tag(ids: list[str], ev_by_id: dict[str, Evidence]) -> str:
    """claim 옆 근거 태그: (근거 3편 · 신뢰도 평균 3.3)."""
    found = [ev_by_id[i] for i in ids if i in ev_by_id]
    if not found:
        return f"(근거 {len(ids)}편)"
    mean_rel = sum(e.reliability for e in found) / len(found)
    return f"(근거 {len(ids)}편 · 신뢰도 평균 {mean_rel:.1f})"


def _paper_label(pid: str, papers: dict[str, Paper], limit: int = 70) -> str:
    p = papers.get(pid)
    if not p:
        return pid
    return _cell(p.title, limit) + (f" ({p.year})" if p.year else "")


# ---------------------------------------------------------------- 렌더링

def render_markdown(b: ResearchBrief, papers: dict[str, Paper] | None = None,
                    checks: dict[str, Any] | None = None, stats: dict[str, Any] | None = None) -> str:
    """goals.md §5 의 7개 섹션 + 참고문헌. papers 가 있으면 제목·연도·링크를 붙인다.

    checks: `post_checks` 결과 → 맨 위 "한눈에" 카드. 없으면 여기서 계산한다 (기본 기준값).
    stats: {"candidates": 검색 후보 수, "critic_rounds": n, "replans": n, "cost_usd": x, "elapsed_min": x} — 있는 것만 표시.
    """
    papers = papers or {}
    stats = stats or {}
    if checks is None:
        checks = post_checks(b, papers)
    refs = _Refs()
    ev_by_id = {e.paper_id: e for e in b.evidence.items}
    tf, lines = b.topic_frame, []

    # ---- 제목 + 한눈에 카드 (결정적 지표)
    lines += [f"# Research Brief: {tf.original_topic}", ""]
    cite_tot, cite_ok = checks.get("citations_total", 0), checks.get("citations_verified", 0)
    rate = f"{cite_ok}/{cite_tot}" + (f" ({cite_ok / cite_tot:.0%})" if cite_tot else "")
    auto_notes = [x for x in b.limitations if x.startswith(AUTO_PREFIX)]
    card = [
        ("검색 후보", str(stats["candidates"]) if "candidates" in stats else str(len(papers)) if papers else "-"),
        ("평가 문헌", str(len(b.evidence.items))),
        ("인용 문헌 (실존 검증)", rate),
        ("sub-RQ 커버리지 (근거 ≥ 3편)", f"{checks.get('sub_rqs_covered', 0)}/{checks.get('sub_rqs', 0)}"),
        ("출처 있는 claim", f"{checks.get('claims_with_source', 0)}/{checks.get('claims_total', 0)}"),
        ("근거 ≥ 2편인 Gap", f"{checks.get('gaps_with_2_evidence', 0)}/{checks.get('gaps', 0)}"),
    ]
    if "critic_rounds" in stats:
        card.append(("Critic 판정 / Replan", f"{stats['critic_rounds']}회 / {stats.get('replans', 0)}회"))
    card.append(("품질 게이트 미해결", f"{len(auto_notes)}건" + (" → §7" if auto_notes else "")))
    if "cost_usd" in stats and stats["cost_usd"] is not None:
        t = f"${stats['cost_usd']:.2f}" + (f" · {stats['elapsed_min']:.1f}분" if stats.get("elapsed_min") else "")
        card.append(("비용 · 시간", t))
    lines += ["| " + " | ".join(k for k, _ in card) + " |", "|" + "---|" * len(card),
              "| " + " | ".join(v for _, v in card) + " |", "",
              "위 수치는 LLM 없이 코드가 계산한 결정적 지표다 (`cost.json` `checks`). 인용 번호 [n] 은 문서 끝 참고문헌을 가리킨다.", ""]

    # ---- 요약, §1, §2
    lines += ["## 요약", b.executive_summary, ""]
    lines += ["## 1. 주제 재정의", f"- RQ: {tf.research_question}", f"- 독립변수: {', '.join(tf.variables.independent)}",
              f"- 종속변수: {', '.join(tf.variables.dependent)}", f"- 대상: {tf.variables.population}",
              f"- 핵심 개념: {', '.join(tf.concepts)}", ""]
    lines += ["## 2. 조사 계획", f"전략: {b.plan.search_strategy}", ""]
    for s in b.plan.sub_rqs:
        lines.append(f"- **{s.id}** {s.question}  \n  쿼리 ({len(s.queries)}개): {'; '.join(s.queries)}")
    lines.append("")

    # ---- §3 Evidence map + sub-RQ 별 표
    lines += ["## 3. Evidence Table", "", "### 3.1 Evidence map — sub-RQ × 신뢰도", "",
              "| sub-RQ | 편수 (rel ≥ 3) | 신뢰도 4~5 | 신뢰도 3 | 신뢰도 ≤ 2 | 평균 신뢰도 | 커버 |",
              "|---|---|---|---|---|---|---|"]
    groups: dict[str, list[Evidence]] = {s.id: [] for s in b.plan.sub_rqs}
    other: list[Evidence] = []
    for e in b.evidence.items:
        hit = False
        for sid in e.sub_rq_ids:
            if sid in groups:
                groups[sid].append(e)
                hit = True
        if not hit:
            other.append(e)
    for s in b.plan.sub_rqs:
        g = [e for e in groups[s.id] if e.relevance >= 3]
        hi, mid, lo = (sum(1 for e in g if e.reliability >= 4), sum(1 for e in g if e.reliability == 3),
                       sum(1 for e in g if e.reliability <= 2))
        mean = f"{sum(e.reliability for e in g) / len(g):.1f}" if g else "-"
        lines.append(f"| {s.id} | {len(g)} | {hi} | {mid} | {lo} | {mean} | {'✅' if len(g) >= 3 else '⚠️ 부족'} |")
    lines += ["", "커버 기준은 Critic 결정적 검사와 같다 (relevance ≥ 3 인 문헌 3편 이상). 신뢰도는 Evaluator 가 설계·표본·출처로 매긴 0~5 점.", "",
              "### 3.2 sub-RQ 별 문헌", ""]

    def table(items: list[Evidence]) -> list[str]:
        out = ["| # | 문헌 | rel | reli | method | sample | finding |", "|---|---|---|---|---|---|---|"]
        for e in items:
            out.append(f"| [{refs.n(e.paper_id)}] | {_paper_label(e.paper_id, papers)} | {e.relevance} | {e.reliability} | "
                       f"{_cell(e.method, 80)} | {_cell(e.sample, 60)} | {_cell(e.finding, FINDING_MAX)} |")
        return out

    for s in b.plan.sub_rqs:
        items = sorted(groups[s.id], key=lambda x: (-x.relevance, -x.reliability))
        lines.append(f"#### {s.id} — {s.question}")
        if not items:
            lines += ["", "(평가된 문헌 없음)", ""]
            continue
        mean = sum(e.reliability for e in items) / len(items)
        top = "; ".join(f"[{refs.n(e.paper_id)}] {_paper_label(e.paper_id, papers, 60)} (reli {e.reliability})"
                        for e in items[:TOP_PER_SUBRQ])
        lines += ["", f"{len(items)}편 · 신뢰도 평균 {mean:.1f} · 상위: {top}", "",
                  f"<details><summary>전체 표 ({len(items)}편)</summary>", ""] + table(items) + ["", "</details>", ""]
    if other:
        items = sorted(other, key=lambda x: (-x.relevance, -x.reliability))
        lines += [f"#### 평가했으나 어느 sub-RQ 에도 배정되지 않은 문헌 ({len(items)}편, 대부분 관련성 ≤ 1)", "",
                  "Evaluator 가 읽고 관련성이 낮다고 판정한 문헌. 종합·Gap 에는 쓰이지 않았지만 평가 기록으로 남긴다.", "",
                  f"<details><summary>전체 표 ({len(items)}편)</summary>", ""] + table(items) + ["", "</details>", ""]

    # ---- §4 종합
    lines += ["## 4. 종합", "", "### 합의"]
    lines += [f"- {c.statement} {refs.cite(c.evidence_ids)} {_evidence_tag(c.evidence_ids, ev_by_id)}"
              for c in b.synthesis.consensus] or ["- (없음)"]
    lines += ["", "### 상충"]
    for c in b.synthesis.conflicts:
        lines += [f"- **{c.claim}** (A {len(c.side_a.evidence_ids)}편 vs B {len(c.side_b.evidence_ids)}편)",
                  f"  - A: {c.side_a.statement} {refs.cite(c.side_a.evidence_ids)}",
                  f"  - B: {c.side_b.statement} {refs.cite(c.side_b.evidence_ids)}",
                  f"  - 원인 가설: {c.hypothesis_for_conflict}"]
    if not b.synthesis.conflicts:
        lines.append("- (없음)")
    lines += ["", "### 조건부"]
    lines += [f"- {c.statement} {refs.cite(c.evidence_ids)} {_evidence_tag(c.evidence_ids, ev_by_id)}"
              for c in b.synthesis.conditional] or ["- (없음)"]
    lines += ["", f"**커버리지 메모**: {b.synthesis.coverage_note}", ""]

    # ---- §5 Gap, §6 제안 표
    lines += ["## 5. Research Gap", ""]
    for i, g in enumerate(b.gaps.gaps, 1):
        lines += [f"**G{i}. {g.description}** {refs.cite(g.evidence_ids)} {_evidence_tag(g.evidence_ids, ev_by_id)}",
                  f"- 제안 RQ: {g.proposed_rq}", f"- 방법: {g.method}", f"- 데이터: {g.data}", ""]
    lines += ["## 6. 향후 연구 방향", "", "§5 의 제안을 한 표로 모았다. 각 행의 근거는 해당 Gap 의 인용을 따른다.", "",
              "| # | 제안 RQ | 연구 설계 | 데이터 | 근거 Gap |", "|---|---|---|---|---|"]
    lines += [f"| {i} | {_cell(g.proposed_rq)} | {_cell(g.method)} | {_cell(g.data)} | G{i} {refs.cite(g.evidence_ids)} |"
              for i, g in enumerate(b.gaps.gaps, 1)]
    if not b.gaps.gaps:
        lines.append("| - | (없음) | | | |")

    # ---- §7 한계: LLM 서술 → 파이프라인 자동 기재
    lines += ["", "## 7. 한계와 신뢰도", ""]
    human = [x for x in b.limitations if not x.startswith(AUTO_PREFIX)]
    lines += [f"- {x}" for x in human] or ["- (없음)"]
    if auto_notes:
        lines += ["", "**품질 게이트가 자동으로 기록한 미해결 항목** (사람이 쓴 것이 아니라 파이프라인 검사 결과다):", ""]
        for x in auto_notes:
            body = x[len(AUTO_PREFIX):]
            if body.startswith("critic:"):
                body = "Critic 미해결 — " + body[len("critic:"):].strip()
            elif body.startswith("search:"):
                body = "검색 부족 — " + body[len("search:"):].strip()
            lines.append(f"- {body}")

    # ---- 참고문헌: 본문·표에 등장한 모든 문헌, 번호순
    lines += ["", f"## 참고문헌 ({len(refs.order)}편)", "",
              "모든 문헌은 검색 도구(OpenAlex·arXiv·Crossref)가 반환한 메타데이터 그대로이며 DOI/arXiv id 로 실존이 확인됐다.", ""]
    lines += [f"{refs.num[pid]}. {_ref_line(pid, papers.get(pid))}" for pid in refs.order]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- 재렌더링 (agent render)

def rerender_run(run_dir: Any, keep_old: bool = True) -> dict[str, Any]:
    """끝난 실행 폴더의 brief.json·papers.json·cost.json 으로 report.md 를 다시 그린다. LLM·네트워크 없음.
    keep_old 면 기존 report.md 를 report_v1.md 로 한 번만 보관한다 (judge.json 은 그 형식을 보고 매긴 점수라 출처를 남긴다)."""
    import json
    from pathlib import Path

    d = Path(run_dir)
    brief_f, papers_f, cost_f = d / "brief.json", d / "papers.json", d / "cost.json"
    if not brief_f.exists() or not papers_f.exists():
        raise ValueError(f"{d.name}: brief.json / papers.json 없음 (완주한 실행만 다시 그린다)")
    brief = ResearchBrief.model_validate_json(brief_f.read_text(encoding="utf-8"))
    papers = {k: Paper.model_validate(v) for k, v in json.loads(papers_f.read_text(encoding="utf-8")).items()}
    cost = json.loads(cost_f.read_text(encoding="utf-8")) if cost_f.exists() else {}
    checks = cost.get("checks") or post_checks(brief, papers)
    stats: dict[str, Any] = {"candidates": len(papers)}
    for k in ("critic_rounds", "replans", "cost_usd"):
        if cost.get(k) is not None:
            stats[k] = cost[k]
    if cost.get("elapsed_sec") is not None:
        stats["elapsed_min"] = cost["elapsed_sec"] / 60
    old = d / "report.md"
    if keep_old and old.exists() and not (d / "report_v1.md").exists():
        (d / "report_v1.md").write_text(old.read_text(encoding="utf-8"), encoding="utf-8")
    md = render_markdown(brief, papers, checks=checks, stats=stats)
    old.write_text(md, encoding="utf-8")
    import re
    tail = md[md.rfind("## 참고문헌"):]
    return {"dir": str(d), "refs": len(re.findall(r"^\d+\. ", tail, re.M)), "bytes": len(md.encode("utf-8"))}
