"""리포트 렌더링과 사후 결정적 지표 — 베이스라인과 그래프가 같은 함수를 쓴다 (ablation 비교의 공정성, plan.md §6.2).

렌더링 원칙 (2026-10-08 개편, plan.md §8):
- LLM 호출 0. `brief.json`·`papers.json`·`cost.json` 만으로 언제든 같은 report.md 를 다시 그릴 수 있다 (`agent render`).
- 인용은 DOI 문자열이 아니라 **번호 [n]** 으로, 끝에 참고문헌 목록. 번호는 문서에 처음 등장하는 순서.
- 맨 위 "한눈에" 카드는 `post_checks` 의 결정적 지표를 그대로 보여준다 — 독자가 첫 줄에서 인용 검증률·커버리지를 확인.
- Evidence Table 은 sub-RQ 별로 나누고 각 머리에 편수·평균 신뢰도·상위 문헌을 요약, 본표는 접는다(<details>).
- 같은 날 상품성 개편: 요약·"먼저 읽을 문헌" 을 카드보다 앞에, 산문 속 DOI 도 [n] 으로 치환, §6 은 요약표, Gap 은 제목+본문,
  Critic 자동 노트는 항목별 불릿, 미배정 문헌은 참고문헌 번호를 받지 않는다. 독자는 "뭘 읽고 뭐가 비었나" 를 먼저 본다.
"""

from __future__ import annotations

import ast
import re
from typing import Any

from .schemas import Evidence, Paper, ResearchBrief

FINDING_MAX = 160          # 표 안 finding 길이 상한 (전체는 brief.json)
TOP_PER_SUBRQ = 3          # sub-RQ 머리에 보여줄 상위 문헌 수
TOP_READ = 10              # "먼저 읽을 문헌" 편수
RQ_MAX, METHOD_MAX, DATA_MAX = 140, 100, 80   # §6 요약표 셀 상한 (전문은 §5)
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


_DOI_RE = re.compile(r"10\.\d+/\S+")      # 접두어 자릿수는 느슨하게 — 어차피 레지스트리에 있는 id 만 치환한다
_ARXIV_RE = re.compile(r"arxiv(?::|\.org/abs/)\s?(\d{4}\.\d{4,5})(?:v\d+)?", re.I)
_TRAIL = ".,;:)]'\""


def _link_ids(text: str, refs: _Refs, papers: dict[str, Paper]) -> str:
    """LLM 이 산문 안에 그대로 쓴 DOI·arXiv id 를 번호 인용 [n] 으로 바꾼다 (레지스트리에 있는 문헌만).

    구조화 필드(evidence_ids)는 애초에 [n] 으로 그려지지만, coverage_note·gap.description·limitations 같은 자유 문장에는
    LLM 이 '10.1007/...' 를 박아 넣는다. 인용 체계를 하나로 맞추려면 여기서 결정적으로 치환해야 한다."""
    if not papers or not text:
        return text

    def doi_sub(m: re.Match[str]) -> str:
        tok, tail = m.group(0), ""
        # 문장부호나 한국어 조사("…-6)는")가 붙어 온 경우 떼어 본다 — DOI 는 ASCII 라 비 ASCII 는 전부 꼬리
        while tok and tok.lower() not in papers and (tok[-1] in _TRAIL or not tok[-1].isascii()):
            tail, tok = tok[-1] + tail, tok[:-1]
        if tok.lower() in papers:
            return f"[{refs.n(tok.lower())}]{tail}"
        return m.group(0)

    def ax_sub(m: re.Match[str]) -> str:
        pid = f"arxiv:{m.group(1)}"
        return f"[{refs.n(pid)}]" if pid in papers else m.group(0)

    out = _ARXIV_RE.sub(ax_sub, _DOI_RE.sub(doi_sub, text))
    return re.sub(r"\(\[(\d+)\]\)", r"[\1]", out)      # "(10.1/x)" → "([3])" → "[3]"


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


def _split_title(desc: str, limit: int = 160, short: int = 110) -> tuple[str, str]:
    """Gap 설명(긴 문단)을 '제목 + 본문' 으로 나눈다. 굵은 글씨 문단은 읽히지 않는다.

    1) 첫 문장이 limit 이하면 그대로 제목, 나머지가 본문.
    2) 첫 문장이 길면(LLM 이 한 문장에 근거까지 욱여넣는 경우가 흔하다) 첫 괄호·대시·콜론·세미콜론 앞에서 끊어
       '주어구' 만 제목으로 쓰고 전문을 본문에 둔다. 예: "Direct measurement of X (word count, …) has never …" → "Direct measurement of X".
    3) 그것도 없으면 short 자 안쪽 단어 경계에서 자르고 … 를 붙인다."""
    desc = desc.strip()
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\[(가-힣])", desc, maxsplit=1)   # 다음 문장이 대문자·괄호·한글로 시작할 때만 (e.g. 방지)
    first, rest = parts[0], (parts[1] if len(parts) > 1 else "")
    if len(first) <= limit:
        return first, rest
    m = re.search(r"\s[(\u2014:;]|\u2014| — |: ", first)
    if m and 25 <= m.start() <= short:
        return first[: m.start()].rstrip(" ,"), desc
    cut = first.rfind(" ", 0, short)
    return first[: cut if cut > 25 else short].rstrip(" ,") + "…", desc


def _auto_note(body: str) -> tuple[str, list[str]]:
    """'critic: unresolved after 2 replan(s): ['a', 'b']' → ('Critic 미해결 — unresolved after …', ['a', 'b']).
    graph 가 노트에 파이썬 리스트를 str() 로 붙이므로 여기서 다시 항목으로 푼다."""
    if body.startswith("critic:"):
        body = "Critic 미해결 — " + body[len("critic:"):].strip()
    elif body.startswith("search:"):
        body = "검색 부족 — " + body[len("search:"):].strip()
    m = re.match(r"^(.*?):\s*(\[.*\])\s*$", body, re.S)
    if m:
        try:
            lst = ast.literal_eval(m.group(2))
        except (ValueError, SyntaxError):
            lst = None
        if isinstance(lst, list) and lst:
            return m.group(1).strip(), [str(x) for x in lst]
    return body, []


# ---------------------------------------------------------------- 렌더링

def _assigned(b: ResearchBrief) -> list[Evidence]:
    """어느 sub-RQ 에든 배정된 평가 문헌 (관련성 낮아 버려진 것 제외)."""
    ids = {s.id for s in b.plan.sub_rqs}
    return [e for e in b.evidence.items if any(sid in ids for sid in e.sub_rq_ids)]


def top_read(b: ResearchBrief, papers: dict[str, Paper] | None = None, n: int = TOP_READ) -> list[Evidence]:
    """"먼저 읽을 문헌": 배정된 문헌 중 rel ≥ 3 을 관련성 → 신뢰도 → 연도 순으로. 렌더러와 translate 가 같은 선정을 써야 해서 분리."""
    papers = papers or {}

    def year(e: Evidence) -> int:
        p = papers.get(e.paper_id)
        return (p.year or 0) if p else 0
    return sorted((e for e in _assigned(b) if e.relevance >= 3), key=lambda e: (-e.relevance, -e.reliability, -year(e)))[:n]


def render_markdown(b: ResearchBrief, papers: dict[str, Paper] | None = None,
                    checks: dict[str, Any] | None = None, stats: dict[str, Any] | None = None,
                    banner: str | None = None, refs: "_Refs | None" = None) -> str:
    """goals.md §5 의 7개 섹션 + 참고문헌. papers 가 있으면 제목·연도·링크를 붙인다.
    banner: 제목 아래 한 줄 안내 (한국어본에서 "영어 원문은 report.en.md" 같은 것).

    읽는 순서(2026-10-08 상품성 개편): 요약 → 먼저 읽을 문헌 → 품질 카드 → §1~§7 → 참고문헌.
    독자가 원하는 답(무엇을 읽고, 무엇이 비어 있나)을 앞에, 채점·검증용 표는 접어서 뒤에 둔다.

    checks: `post_checks` 결과 → 품질 카드. 없으면 여기서 계산한다 (기본 기준값).
    stats: {"candidates": 검색 후보 수, "critic_rounds": n, "replans": n, "cost_usd": x, "elapsed_min": x} — 있는 것만 표시.
    refs: 비어 있는 _Refs 를 주면 참고문헌 번호 순서를 돌려받는다 (export 가 BibTeX 번호를 리포트와 맞추는 데 쓴다).
    """
    papers = papers or {}
    stats = stats or {}
    if checks is None:
        checks = post_checks(b, papers)
    refs = refs if refs is not None else _Refs()
    ev_by_id = {e.paper_id: e for e in b.evidence.items}
    tf, lines = b.topic_frame, []

    def L(text: str) -> str:            # 산문 속 DOI → [n]
        return _link_ids(text, refs, papers)

    # ---- sub-RQ 별 그룹 (미배정 문헌은 따로)
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
    other_ids = {id(e) for e in other}
    assigned = [e for e in b.evidence.items if id(e) not in other_ids]

    # ---- 제목, 요약
    lines += [f"# Research Brief: {tf.original_topic}", "", f"> RQ — {tf.research_question}", ""]
    if banner:
        lines += [f"> {banner}", ""]
    lines += ["## 요약", "", L(b.executive_summary), ""]

    # ---- 먼저 읽을 문헌: 평가 점수(관련성 → 신뢰도 → 최신)로 결정적으로 고른다. 번호 [1]~[N] 이 여기서 매겨진다.
    top = top_read(b, papers)
    if top:
        lines += [f"## 먼저 읽을 문헌 ({len(top)}편)", "",
                  "Evaluator 의 관련성(rel)·신뢰도(reli) 점수 순. 전체 평가 표는 §3, 서지 정보는 참고문헌.", "",
                  "| # | 문헌 | 핵심 결과 | sub-RQ | rel · reli |", "|---|---|---|---|---|"]
        for e in top:
            lines.append(f"| [{refs.n(e.paper_id)}] | {_paper_label(e.paper_id, papers, 80)} | {_cell(e.finding, FINDING_MAX)} | "
                         f"{', '.join(e.sub_rq_ids)} | {e.relevance} · {e.reliability} |")
        lines.append("")

    # ---- 품질 카드 (결정적 지표)
    cite_tot, cite_ok = checks.get("citations_total", 0), checks.get("citations_verified", 0)
    rate = f"{cite_ok}/{cite_tot}" + (f" ({cite_ok / cite_tot:.0%})" if cite_tot else "")
    auto_notes = [x for x in b.limitations if x.startswith(AUTO_PREFIX)]
    card = [
        ("검색 후보", str(stats["candidates"]) if "candidates" in stats else str(len(papers)) if papers else "-"),
        ("평가 문헌", str(len(b.evidence.items))),
        ("실존 검증 (DOI/arXiv)", rate),
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
    lines += ["## 품질 한눈에", "",
              "| " + " | ".join(k for k, _ in card) + " |", "|" + "---|" * len(card),
              "| " + " | ".join(v for _, v in card) + " |", "",
              "LLM 없이 코드가 계산한 결정적 지표다 (`cost.json` `checks`). 인용 번호 [n] 은 문서 끝 참고문헌을 가리킨다.", ""]

    # ---- §1, §2
    lines += ["## 1. 주제 재정의", "", f"- RQ: {tf.research_question}", f"- 독립변수: {', '.join(tf.variables.independent)}",
              f"- 종속변수: {', '.join(tf.variables.dependent)}", f"- 대상: {tf.variables.population}",
              f"- 핵심 개념: {', '.join(tf.concepts)}", ""]
    lines += ["## 2. 조사 계획", "", f"전략: {b.plan.search_strategy}", ""]
    lines += [f"- **{s.id}** {s.question}" for s in b.plan.sub_rqs]
    n_q = sum(len(s.queries) for s in b.plan.sub_rqs)
    lines += ["", f"<details><summary>검색 쿼리 전체 ({n_q}개 — Replan 으로 추가된 쿼리 포함)</summary>", ""]
    lines += [f"- **{s.id}** ({len(s.queries)}개): {'; '.join(s.queries)}" for s in b.plan.sub_rqs]
    lines += ["", "</details>", ""]

    # ---- §3 Evidence map + sub-RQ 별 표
    lines += ["## 3. Evidence Table", "", "### 3.1 Evidence map — sub-RQ × 신뢰도", "",
              "| sub-RQ | 편수 (rel ≥ 3) | 신뢰도 4~5 | 신뢰도 3 | 신뢰도 ≤ 2 | 평균 신뢰도 | 커버 |",
              "|---|---|---|---|---|---|---|"]
    for s in b.plan.sub_rqs:
        g = [e for e in groups[s.id] if e.relevance >= 3]
        hi, mid, lo = (sum(1 for e in g if e.reliability >= 4), sum(1 for e in g if e.reliability == 3),
                       sum(1 for e in g if e.reliability <= 2))
        mean = f"{sum(e.reliability for e in g) / len(g):.1f}" if g else "-"
        lines.append(f"| {s.id} | {len(g)} | {hi} | {mid} | {lo} | {mean} | {'✅' if len(g) >= 3 else '⚠️ 부족'} |")
    lines += ["", "커버 기준은 Critic 결정적 검사와 같다 (relevance ≥ 3 인 문헌 3편 이상). 신뢰도는 Evaluator 가 설계·표본·출처로 매긴 0~5 점.", "",
              "### 3.2 sub-RQ 별 문헌", ""]

    def table(items: list[Evidence], numbered: bool = True) -> list[str]:
        head = "#" if numbered else "id"
        out = [f"| {head} | 문헌 | rel | reli | method | sample | finding |", "|---|---|---|---|---|---|---|"]
        for e in items:
            key = f"[{refs.n(e.paper_id)}]" if numbered else _cell(e.paper_id)
            out.append(f"| {key} | {_paper_label(e.paper_id, papers)} | {e.relevance} | {e.reliability} | "
                       f"{_cell(e.method, 80)} | {_cell(e.sample, 60)} | {_cell(e.finding, FINDING_MAX)} |")
        return out

    for s in b.plan.sub_rqs:
        items = sorted(groups[s.id], key=lambda x: (-x.relevance, -x.reliability))
        lines.append(f"#### {s.id} — {s.question}")
        if not items:
            lines += ["", "(평가된 문헌 없음)", ""]
            continue
        strong = sum(1 for e in items if e.relevance >= 3)
        mean = sum(e.reliability for e in items) / len(items)
        cnt = f"{len(items)}편" + (f" (rel ≥ 3: {strong}편)" if strong != len(items) else "")
        top_s = "; ".join(f"[{refs.n(e.paper_id)}] {_paper_label(e.paper_id, papers, 60)} (reli {e.reliability})"
                          for e in items[:TOP_PER_SUBRQ])
        lines += ["", f"{cnt} · 신뢰도 평균 {mean:.1f} · 상위: {top_s}", "",
                  f"<details><summary>전체 표 ({len(items)}편)</summary>", ""] + table(items) + ["", "</details>", ""]
    if other:
        items = sorted(other, key=lambda x: (-x.relevance, -x.reliability))
        lines += [f"#### 평가했으나 어느 sub-RQ 에도 배정되지 않은 문헌 ({len(items)}편, 대부분 관련성 ≤ 1)", "",
                  "Evaluator 가 읽고 관련성이 낮다고 판정한 문헌. 종합·Gap 에 쓰이지 않아 참고문헌 번호를 받지 않으며, 평가 기록으로만 남긴다.", "",
                  f"<details><summary>전체 표 ({len(items)}편)</summary>", ""] + table(items, numbered=False) + ["", "</details>", ""]

    # ---- §4 종합
    lines += ["## 4. 종합", "", "### 합의", ""]
    lines += [f"- {L(c.statement)} {refs.cite(c.evidence_ids)} {_evidence_tag(c.evidence_ids, ev_by_id)}"
              for c in b.synthesis.consensus] or ["- (없음)"]
    lines += ["", "### 상충", ""]
    for c in b.synthesis.conflicts:
        lines += [f"- **{L(c.claim)}** (A {len(c.side_a.evidence_ids)}편 vs B {len(c.side_b.evidence_ids)}편)",
                  f"  - A: {L(c.side_a.statement)} {refs.cite(c.side_a.evidence_ids)}",
                  f"  - B: {L(c.side_b.statement)} {refs.cite(c.side_b.evidence_ids)}",
                  f"  - 원인 가설: {L(c.hypothesis_for_conflict)}"]
    if not b.synthesis.conflicts:
        lines.append("- (없음)")
    lines += ["", "### 조건부", ""]
    lines += [f"- {L(c.statement)} {refs.cite(c.evidence_ids)} {_evidence_tag(c.evidence_ids, ev_by_id)}"
              for c in b.synthesis.conditional] or ["- (없음)"]
    lines += ["", "### 커버리지 메모", "", L(b.synthesis.coverage_note), ""]

    # ---- §5 Gap: 제목 한 문장 + 본문 + 제안
    lines += ["## 5. Research Gap", ""]
    for i, g in enumerate(b.gaps.gaps, 1):
        title, rest = _split_title(g.description)
        lines += [f"### G{i}. {L(title)}", "",
                  f"{refs.cite(g.evidence_ids)} {_evidence_tag(g.evidence_ids, ev_by_id)}", ""]
        if rest:
            lines += [L(rest), ""]
        lines += [f"- 제안 RQ: {L(g.proposed_rq)}", f"- 방법: {L(g.method)}", f"- 데이터: {L(g.data)}", ""]

    # ---- §6 제안 요약표 (전문은 §5)
    lines += ["## 6. 향후 연구 방향", "", "§5 의 제안을 한 표로 요약했다 (전문은 각 Gap). 근거는 해당 Gap 의 인용을 따른다.", "",
              "| # | 제안 RQ | 연구 설계 | 데이터 | 근거 Gap |", "|---|---|---|---|---|"]
    lines += [f"| {i} | {_cell(L(g.proposed_rq), RQ_MAX)} | {_cell(L(g.method), METHOD_MAX)} | {_cell(L(g.data), DATA_MAX)} | "
              f"G{i} {refs.cite(g.evidence_ids)} |" for i, g in enumerate(b.gaps.gaps, 1)]
    if not b.gaps.gaps:
        lines.append("| - | (없음) | | | |")

    # ---- §7 한계: LLM 서술 → 파이프라인 자동 기재
    lines += ["", "## 7. 한계와 신뢰도", ""]
    human = [x for x in b.limitations if not x.startswith(AUTO_PREFIX)]
    lines += [f"- {L(x)}" for x in human] or ["- (없음)"]
    if auto_notes:
        lines += ["", "**품질 게이트가 자동으로 기록한 미해결 항목** (사람이 쓴 것이 아니라 파이프라인 검사 결과다):", ""]
        for x in auto_notes:
            head, items = _auto_note(x[len(AUTO_PREFIX):])
            lines.append(f"- {L(head)}")
            lines += [f"  - {L(it)}" for it in items]

    # ---- 참고문헌: 본문·표에 번호로 등장한 문헌, 번호순
    lines += ["", f"## 참고문헌 ({len(refs.order)}편)", "",
              "본문·표에 번호로 인용된 문헌. 모두 검색 도구(OpenAlex·arXiv·Crossref)가 반환한 메타데이터 그대로이며 DOI/arXiv id 로 실존이 확인됐다.", ""]
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
    ko_f = d / "brief.ko.json"
    lang = "en"
    if ko_f.exists():
        # 한국어 번역(ADR-11)이 있으면 report.md 는 한국어본, 영어 원문은 report.en.md 로. 번역은 brief.json 을 바꾸지 않는다
        from .translate import KO_BANNER, apply_translation
        ko = json.loads(ko_f.read_text(encoding="utf-8"))
        ko_brief = apply_translation(brief, ko.get("items", {}))
        (d / "report.en.md").write_text(md, encoding="utf-8")
        md = render_markdown(ko_brief, papers, checks=checks, stats=stats, banner=KO_BANNER)
        lang = "ko"
    old.write_text(md, encoding="utf-8")
    tail = md[md.rfind("## 참고문헌"):]
    return {"dir": str(d), "refs": len(re.findall(r"^\d+\. ", tail, re.M)), "bytes": len(md.encode("utf-8")), "lang": lang}
