"""report.py 렌더러 (2026-10-08 개편) — LLM 없이 brief 에서 결정적으로 그려지는지.

- 인용은 번호 [n] 이고 끝에 참고문헌 목록이 있으며, 본문·표에 등장한 문헌이 전부 번호를 받는다
- 맨 위 "한눈에" 카드가 post_checks 수치를 그대로 보여준다
- Evidence map 은 sub-RQ 별 편수·신뢰도 구간·커버 여부, 표는 sub-RQ 별로 나뉘고 접힌다
- §4 claim 옆 근거 태그, §6 은 표, §7 의 [auto] 노트는 사람 서술과 분리
- 표 셀의 파이프·개행은 깨지지 않게 이스케이프
- rerender_run 이 끝난 실행 폴더를 다시 그리고 옛 report.md 를 report_v1.md 로 보관
"""

import json

from research_agent.report import post_checks, render_markdown, rerender_run
from research_agent.schemas import (Claim, Conflict, Evidence, EvidenceTable, Gap, GapList, Paper, ResearchBrief,
                                    ResearchPlan, SubRQ, TopicFrame, Variables)

TF = TopicFrame(original_topic="주제", topic_en="t", domain="education", concepts=["a", "b", "c"],
                variables=Variables(independent=["x"], dependent=["y"], population="p"),
                synonyms_en=["s1", "s2", "s3"], research_question="Does x affect y?")
PLAN = ResearchPlan(sub_rqs=[
    SubRQ(id="rq1", question="q1", rationale="r", queries=["a1", "b1"], source_pref="openalex"),
    SubRQ(id="rq2", question="q2", rationale="r", queries=["a2"], source_pref="arxiv"),
    SubRQ(id="rq3", question="q3", rationale="r", queries=["a3"], source_pref="both"),
], search_strategy="s")


def _paper(i, src="openalex", year=2024, authors=None):
    pid = f"arxiv:{i:04d}.00001" if src == "arxiv" else f"10.1/p{i}"
    return Paper(id=pid, title=f"P{i}", year=year, doi=None if src == "arxiv" else pid, arxiv_id=f"{i:04d}.00001" if src == "arxiv" else None,
                 authors=authors or [f"A{i}"], venue="V", source=src, verified=True)


def _ev(pid, rel=4, reli=3, rq=("rq1",), finding="f"):
    return Evidence(paper_id=pid, relevance=rel, reliability=reli, method="survey", finding=finding, sub_rq_ids=list(rq))


def _brief(limitations=None):
    ev = EvidenceTable(items=[
        _ev("10.1/p0", reli=4), _ev("10.1/p1", reli=2, finding="has | pipe\nand newline"),
        _ev("10.1/p2", rq=("rq1", "rq2")), _ev("arxiv:0009.00001", rq=("rq2",)),
        _ev("10.1/p3", rel=1, rq=()),                       # 관련성 낮아 어느 sub-RQ 에도 배정 안 됨
    ])
    from research_agent.schemas import Synthesis
    synthesis = Synthesis(
        consensus=[Claim(statement="c1", evidence_ids=["10.1/p0", "10.1/p1"])],
        conflicts=[Conflict(claim="k", side_a=Claim(statement="a", evidence_ids=["10.1/p2"]),
                            side_b=Claim(statement="b", evidence_ids=["arxiv:0009.00001", "10.1/p0"]), hypothesis_for_conflict="h")],
        conditional=[], coverage_note="cov")
    gaps = GapList(gaps=[Gap(description="g1", evidence_ids=["10.1/p0", "10.1/p2"], proposed_rq="rq?", method="RCT", data="n=100")])
    return ResearchBrief(topic_frame=TF, plan=PLAN, evidence=ev, synthesis=synthesis, gaps=gaps,
                         limitations=limitations or ["human limitation", "[auto] critic: rq3 thin"], executive_summary="요약")


def _papers():
    ps = [_paper(i) for i in range(4)] + [_paper(9, "arxiv", authors=["B1", "B2", "B3", "B4"])]
    return {p.id: p for p in ps}


def test_numbered_citations_and_reference_list():
    md = render_markdown(_brief(), _papers())
    # 본문 인용은 DOI 가 아니라 번호
    assert "[10.1/p0" not in md.split("## 참고문헌")[0]
    assert "- c1 [1, 3] (근거 2편 · 신뢰도 평균 3.0)" in md
    # 참고문헌: 등장한 문헌 5편 전부, 번호순, DOI 링크·arXiv 링크·et al.
    refs = md.split("## 참고문헌 (5편)")[1]
    assert "1. A0 (2024). P0. *V*. https://doi.org/10.1/p0" in refs
    assert "B1, B2, B3 et al. (2024). P9. *V*. https://arxiv.org/abs/0009.00001" in refs
    # 번호는 처음 등장 순 — Evidence 표가 먼저이므로 rq1 의 최상위 문헌(p0, rel 4·reli 4)이 [1]
    assert "| [1] | P0 (2024) | 4 | 4 |" in md


def test_card_and_evidence_map():
    b, ps = _brief(), _papers()
    checks = post_checks(b, ps)
    md = render_markdown(b, ps, checks=checks, stats={"candidates": 42, "critic_rounds": 2, "replans": 1, "cost_usd": 0.5, "elapsed_min": 3.2})
    head = md.split("## 요약")[0]
    assert "| 42 | 5 | 5/5 (100%) | 1/3 | 3/3 | 1/1 | 2회 / 1회 | 1건 → §7 | $0.50 · 3.2분 |" in head
    # Evidence map: rq1 는 rel≥3 세 편(p0 reli4, p1 reli2, p2 reli3) → 커버, rq2 는 2편·rq3 는 0편 → 부족
    assert "| rq1 | 3 | 1 | 1 | 1 | 3.0 | ✅ |" in md
    assert "| rq2 | 2 | 0 | 2 | 0 | 3.0 | ⚠️ 부족 |" in md and "| rq3 | 0 | 0 | 0 | 0 | - | ⚠️ 부족 |" in md
    assert "#### rq3 — q3" in md and "(평가된 문헌 없음)" in md
    # 미배정 문헌은 별도 그룹에, 지표 분모에는 남음
    assert "어느 sub-RQ 에도 배정되지 않은 문헌 (1편" in md


def test_table_cells_escaped_and_sections_present():
    md = render_markdown(_brief(), _papers())
    assert "has \\| pipe and newline" in md                      # 파이프 이스케이프, 개행 제거
    for h in ("## 요약", "## 1. 주제 재정의", "## 2. 조사 계획", "## 3. Evidence Table", "### 3.1 Evidence map",
              "## 4. 종합", "## 5. Research Gap", "## 6. 향후 연구 방향", "## 7. 한계와 신뢰도", "## 참고문헌"):
        assert h in md
    assert "<details><summary>전체 표 (3편)</summary>" in md      # rq1 표 접힘
    assert "- **k** (A 1편 vs B 2편)" in md                         # 상충 양측 편수
    assert "| 1 | rq? | RCT | n=100 | G1 [1, 2] |" in md             # §6 표
    # §7: 사람 서술과 자동 기재 분리, [auto] 접두어는 사람 말로
    tail = md.split("## 7. 한계와 신뢰도")[1]
    assert "- human limitation" in tail and "[auto]" not in tail and "- Critic 미해결 — rq3 thin" in tail


def test_render_without_checks_computes_them():
    md = render_markdown(_brief(), _papers())
    assert "| 5 | 5 | 5/5 (100%) | 1/3 |" in md      # candidates = papers 수, checks 는 내부 계산


def test_rerender_run_keeps_old_and_uses_cost_json(tmp_path):
    d = tmp_path / "20260101T000000Z_graph_x"
    d.mkdir()
    b, ps = _brief(), _papers()
    (d / "brief.json").write_text(b.model_dump_json(), encoding="utf-8")
    (d / "papers.json").write_text(json.dumps({k: v.model_dump() for k, v in ps.items()}), encoding="utf-8")
    (d / "cost.json").write_text(json.dumps({"checks": post_checks(b, ps), "critic_rounds": 3, "replans": 2,
                                             "cost_usd": 0.81, "elapsed_sec": 438}), encoding="utf-8")
    (d / "report.md").write_text("OLD", encoding="utf-8")
    r = rerender_run(d)
    assert r["refs"] == 5 and (d / "report_v1.md").read_text(encoding="utf-8") == "OLD"
    md = (d / "report.md").read_text(encoding="utf-8")
    assert "| 3회 / 2회 |" in md and "$0.81 · 7.3분" in md
    rerender_run(d)                                                 # 두 번째는 v1 을 덮어쓰지 않음
    assert (d / "report_v1.md").read_text(encoding="utf-8") == "OLD"
