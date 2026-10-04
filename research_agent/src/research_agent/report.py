"""리포트 렌더링과 사후 결정적 지표 — 베이스라인과 그래프가 같은 함수를 쓴다 (ablation 비교의 공정성, plan.md §6.2)."""

from __future__ import annotations

from typing import Any

from .schemas import Paper, ResearchBrief


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


def render_markdown(b: ResearchBrief, papers: dict[str, Paper] | None = None) -> str:
    """goals.md §5 의 7개 섹션. papers 를 주면 Evidence Table 에 제목·연도를 붙인다."""
    papers = papers or {}
    tf, lines = b.topic_frame, []
    lines += [f"# Research Brief: {tf.original_topic}", "", "## 요약", b.executive_summary, ""]
    lines += ["## 1. 주제 재정의", f"- RQ: {tf.research_question}", f"- 독립변수: {', '.join(tf.variables.independent)}",
              f"- 종속변수: {', '.join(tf.variables.dependent)}", f"- 대상: {tf.variables.population}",
              f"- 핵심 개념: {', '.join(tf.concepts)}", ""]
    lines += ["## 2. 조사 계획", f"전략: {b.plan.search_strategy}", ""]
    for s in b.plan.sub_rqs:
        lines.append(f"- **{s.id}** {s.question}  \n  쿼리: {'; '.join(s.queries)}")
    lines += ["", "## 3. Evidence Table", "", "| id | 제목 (연도) | rel | reli | method | sample | finding | sub-RQ |",
              "|---|---|---|---|---|---|---|---|"]
    for e in sorted(b.evidence.items, key=lambda x: (-x.relevance, -x.reliability)):
        p = papers.get(e.paper_id)
        title = f"{p.title[:70]} ({p.year})" if p else ""
        lines.append(f"| {e.paper_id} | {title} | {e.relevance} | {e.reliability} | {e.method} | {e.sample} | "
                     f"{e.finding} | {','.join(e.sub_rq_ids)} |")
    lines += ["", "## 4. 종합", "### 합의"]
    lines += [f"- {c.statement} [{', '.join(c.evidence_ids)}]" for c in b.synthesis.consensus] or ["- (없음)"]
    lines += ["### 상충"]
    for c in b.synthesis.conflicts:
        lines += [f"- **{c.claim}**", f"  - A: {c.side_a.statement} [{', '.join(c.side_a.evidence_ids)}]",
                  f"  - B: {c.side_b.statement} [{', '.join(c.side_b.evidence_ids)}]", f"  - 가설: {c.hypothesis_for_conflict}"]
    if not b.synthesis.conflicts:
        lines.append("- (없음)")
    lines += ["### 조건부"]
    lines += [f"- {c.statement} [{', '.join(c.evidence_ids)}]" for c in b.synthesis.conditional] or ["- (없음)"]
    lines += ["", f"커버리지: {b.synthesis.coverage_note}", "", "## 5. Research Gap"]
    for g in b.gaps.gaps:
        lines += [f"- **{g.description}** [{', '.join(g.evidence_ids)}]", f"  - 제안 RQ: {g.proposed_rq}",
                  f"  - 방법: {g.method}", f"  - 데이터: {g.data}"]
    lines += ["", "## 6. 향후 연구 방향"]
    lines += [f"{i}. {g.proposed_rq} — {g.method}; 데이터: {g.data}" for i, g in enumerate(b.gaps.gaps, 1)]
    lines += ["", "## 7. 한계와 신뢰도"]
    lines += [f"- {x}" for x in b.limitations]
    return "\n".join(lines) + "\n"
