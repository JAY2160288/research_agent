"""report.py 렌더러 (2026-10-08 개편 + 같은 날 상품성 개편) — LLM 없이 brief 에서 결정적으로 그려지는지.

- 읽는 순서: 요약 → 먼저 읽을 문헌 → 품질 카드 → §1~§7 → 참고문헌
- 인용은 번호 [n] 이고 끝에 참고문헌 목록. LLM 이 산문에 박아 넣은 DOI·arXiv id 도 [n] 으로 치환된다
- "먼저 읽을 문헌" 은 관련성 → 신뢰도 → 연도 순으로 결정적으로 뽑히고, 여기서 번호 [1]~ 가 매겨진다
- 미배정(관련성 낮은) 문헌은 표에만 남고 참고문헌 번호를 받지 않는다
- Evidence map 은 sub-RQ 별 편수·신뢰도 구간·커버 여부, 표는 sub-RQ 별로 나뉘고 접힌다
- §5 Gap 은 제목 한 문장 + 본문, §6 은 요약표(셀 길이 상한), §7 의 [auto] 노트는 사람 서술과 분리되고 리스트 repr 은 불릿으로 풀린다
- 표 셀의 파이프·개행은 깨지지 않게 이스케이프
- rerender_run 이 끝난 실행 폴더를 다시 그리고 옛 report.md 를 report_v1.md 로 보관
"""

import json

from research_agent.report import _auto_note, _link_ids, _Refs, _split_title, post_checks, render_markdown, rerender_run
from research_agent.schemas import (Claim, Conflict, Evidence, EvidenceTable, Gap, GapList, Paper, ResearchBrief,
                                    ResearchPlan, SubRQ, Synthesis, TopicFrame, Variables)

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


def _brief(limitations=None, coverage_note="cov", gap_desc="g1"):
    ev = EvidenceTable(items=[
        _ev("10.1/p0", reli=4), _ev("10.1/p1", reli=2, finding="has | pipe\nand newline"),
        _ev("10.1/p2", rq=("rq1", "rq2")), _ev("arxiv:0009.00001", rq=("rq2",)),
        _ev("10.1/p3", rel=1, rq=()),                       # 관련성 낮아 어느 sub-RQ 에도 배정 안 됨
    ])
    synthesis = Synthesis(
        consensus=[Claim(statement="c1", evidence_ids=["10.1/p0", "10.1/p1"])],
        conflicts=[Conflict(claim="k", side_a=Claim(statement="a", evidence_ids=["10.1/p2"]),
                            side_b=Claim(statement="b", evidence_ids=["arxiv:0009.00001", "10.1/p0"]), hypothesis_for_conflict="h")],
        conditional=[], coverage_note=coverage_note)
    gaps = GapList(gaps=[Gap(description=gap_desc, evidence_ids=["10.1/p0", "10.1/p2"], proposed_rq="rq?", method="RCT", data="n=100")])
    return ResearchBrief(topic_frame=TF, plan=PLAN, evidence=ev, synthesis=synthesis, gaps=gaps,
                         limitations=limitations or ["human limitation", "[auto] critic: rq3 thin"], executive_summary="요약")


def _papers():
    ps = [_paper(i) for i in range(4)] + [_paper(9, "arxiv", authors=["B1", "B2", "B3", "B4"])]
    return {p.id: p for p in ps}


def test_reading_order_and_top_papers():
    md = render_markdown(_brief(), _papers())
    order = [md.index(h) for h in ("## 요약", "## 먼저 읽을 문헌", "## 품질 한눈에", "## 1. 주제 재정의", "## 7. 한계와 신뢰도", "## 참고문헌")]
    assert order == sorted(order)                                   # 요약·읽을 문헌이 카드보다 앞
    # Top: rel≥3 인 배정 문헌 4편을 관련성 → 신뢰도 → 연도 순으로. p0(4,4) → p2(4,3) → p9(4,3) → p1(4,2)
    top = md.split("## 먼저 읽을 문헌 (4편)")[1].split("## 품질 한눈에")[0]
    assert "| [1] | P0 (2024) | f | rq1 | 4 · 4 |" in top
    assert "| [2] | P2 (2024) | f | rq1, rq2 | 4 · 3 |" in top
    assert "| [4] | P1 (2024) | has \\| pipe and newline | rq1 | 4 · 2 |" in top
    assert "P3" not in top                                          # 미배정 문헌은 Top 에 없음


def test_numbered_citations_and_reference_list():
    md = render_markdown(_brief(), _papers())
    body = md.split("## 참고문헌")[0]
    assert "[10.1/p0" not in body                                    # 본문 인용은 DOI 가 아니라 번호
    assert "- c1 [1, 4] (근거 2편 · 신뢰도 평균 3.0)" in md
    # 참고문헌: 번호를 받은 4편만 (미배정 p3 제외), 번호순, DOI 링크·arXiv 링크·et al.
    refs = md.split("## 참고문헌 (4편)")[1]
    assert "1. A0 (2024). P0. *V*. https://doi.org/10.1/p0" in refs
    assert "3. B1, B2, B3 et al. (2024). P9. *V*. https://arxiv.org/abs/0009.00001" in refs
    assert "P3" not in refs
    # 미배정 표는 번호 대신 id 를 보여준다
    assert "| 10.1/p3 | P3 (2024) | 1 | 3 |" in md and "참고문헌 번호를 받지 않으며" in md


def test_prose_doi_replaced_with_citation_number():
    b = _brief(coverage_note="Only 10.1/p2 and (10.1/p0) address rq1; see arXiv:0009.00001 and arxiv.org/abs/0009.00001v2. Unknown 10.9/zzz stays.",
               gap_desc="Nothing measures X (10.1/p2, 10.1/p0). Only one survey exists. Third sentence.",
               limitations=["RQ1 relies on 10.1/p0.", "[auto] critic: rq3 thin"])
    md = render_markdown(b, _papers())
    cov = md.split("### 커버리지 메모")[1].split("## 5.")[0]
    assert "Only [2] and [1] address rq1; see [3] and [3]. Unknown 10.9/zzz stays." in cov   # 괄호 DOI → [n], 모르는 DOI 는 그대로
    gap = md.split("## 5. Research Gap")[1].split("## 6.")[0]
    assert "### G1. Nothing measures X ([2], [1])." in gap          # 제목 = 첫 문장
    assert "\nOnly one survey exists. Third sentence.\n" in gap     # 나머지는 본문
    assert "- RQ1 relies on [1]." in md.split("## 7. 한계와 신뢰도")[1]


def test_link_ids_unit():
    refs, ps = _Refs(), _papers()
    assert _link_ids("x 10.1/P0, y 10.1/p1.", refs, ps) == "x [1], y [2]."     # 대소문자 무시, 뒤 문장부호 보존
    assert _link_ids("no ids here", refs, ps) == "no ids here"
    assert _link_ids("유일한 증거(10.1/p0)는 설문이다.", refs, ps) == "유일한 증거[1]는 설문이다."   # 한국어 조사가 붙은 DOI
    assert _link_ids("10.1/p0", refs, {}) == "10.1/p0"                          # papers 없으면 그대로


def test_split_title_and_auto_note():
    assert _split_title("First. Second one.") == ("First.", "Second one.")
    assert _split_title("생산성(단어 수)의 직접 측정은 비교된 적이 없다. 유일한 증거는 설문이다.") == ("생산성(단어 수)의 직접 측정은 비교된 적이 없다.", "유일한 증거는 설문이다.")
    assert _split_title("Ref 10.1007/x. Then more.") == ("Ref 10.1007/x.", "Then more.")   # DOI 의 점은 문장 끝이 아님
    long = "A" * 200 + ". B."
    t, rest = _split_title(long)
    assert t == "A" * 110 + "…" and rest == long                                  # 단어 경계도 괄호도 없으면 110자에서 자르고 전문을 본문에
    assert _split_title("Direct measurement of research output (word count, pages) has never been compared between users and non-users in randomized or longitudinal designs over a full semester or academic year anywhere.") == (
        "Direct measurement of research output", "Direct measurement of research output (word count, pages) has never been compared between users and non-users in randomized or longitudinal designs over a full semester or academic year anywhere.")
    head, items = _auto_note("critic: unresolved after 2 replan(s): ['RQ1 thin', 'RQ2 thin']")
    assert head == "Critic 미해결 — unresolved after 2 replan(s)" and items == ["RQ1 thin", "RQ2 thin"]
    assert _auto_note("search: rq3 0 hits") == ("검색 부족 — rq3 0 hits", [])
    assert _auto_note("critic: plain note: [not a list") == ("Critic 미해결 — plain note: [not a list", [])


def test_card_and_evidence_map():
    b, ps = _brief(), _papers()
    checks = post_checks(b, ps)
    md = render_markdown(b, ps, checks=checks, stats={"candidates": 42, "critic_rounds": 2, "replans": 1, "cost_usd": 0.5, "elapsed_min": 3.2})
    card = md.split("## 품질 한눈에")[1].split("## 1. 주제 재정의")[0]
    assert "| 42 | 5 | 5/5 (100%) | 1/3 | 3/3 | 1/1 | 2회 / 1회 | 1건 → §7 | $0.50 · 3.2분 |" in card
    # Evidence map: rq1 는 rel≥3 세 편(p0 reli4, p1 reli2, p2 reli3) → 커버, rq2 는 2편·rq3 는 0편 → 부족
    assert "| rq1 | 3 | 1 | 1 | 1 | 3.0 | ✅ |" in md
    assert "| rq2 | 2 | 0 | 2 | 0 | 3.0 | ⚠️ 부족 |" in md and "| rq3 | 0 | 0 | 0 | 0 | - | ⚠️ 부족 |" in md
    assert "#### rq3 — q3" in md and "(평가된 문헌 없음)" in md
    # 미배정 문헌은 별도 그룹에, 지표 분모에는 남음
    assert "어느 sub-RQ 에도 배정되지 않은 문헌 (1편" in md


def test_subrq_header_shows_rel_split_when_differs():
    b = _brief()
    b.evidence.items.append(_ev("10.1/p3", rel=2, rq=("rq1",)))     # rq1 에 rel 2 짜리 추가 → 4편 중 rel≥3 은 3편
    md = render_markdown(b, _papers())
    assert "4편 (rel ≥ 3: 3편) · 신뢰도 평균" in md
    assert "2편 · 신뢰도 평균 3.0 · 상위:" in md                     # rq2 는 전부 rel≥3 → 괄호 없음


def test_table_cells_escaped_and_sections_present():
    md = render_markdown(_brief(), _papers())
    assert "has \\| pipe and newline" in md                      # 파이프 이스케이프, 개행 제거
    for h in ("## 요약", "## 1. 주제 재정의", "## 2. 조사 계획", "## 3. Evidence Table", "### 3.1 Evidence map",
              "## 4. 종합", "## 5. Research Gap", "## 6. 향후 연구 방향", "## 7. 한계와 신뢰도", "## 참고문헌"):
        assert h in md
    assert "<details><summary>검색 쿼리 전체 (4개" in md            # §2 쿼리는 접힘
    assert "<details><summary>전체 표 (3편)</summary>" in md      # rq1 표 접힘
    assert "- **k** (A 1편 vs B 2편)" in md                         # 상충 양측 편수
    assert "| 1 | rq? | RCT | n=100 | G1 [1, 2] |" in md             # §6 표
    # §7: 사람 서술과 자동 기재 분리, [auto] 접두어는 사람 말로
    tail = md.split("## 7. 한계와 신뢰도")[1]
    assert "- human limitation" in tail and "[auto]" not in tail and "- Critic 미해결 — rq3 thin" in tail


def test_section6_truncates_and_auto_note_list_becomes_bullets():
    b = _brief(limitations=["h", "[auto] critic: unresolved after 2 replan(s): ['RQ1 thin', 'RQ2 (10.1/p0) thin']"])
    b.gaps.gaps[0].proposed_rq = "Q" * 300
    md = render_markdown(b, _papers())
    row = [ln for ln in md.splitlines() if ln.startswith("| 1 | QQQ")][0]
    assert "Q" * 139 + "…" in row and "Q" * 141 not in row            # §6 셀은 140자에서 잘림
    assert "### G1. g1" in md and "- 제안 RQ: " + "Q" * 300 in md     # §5 에는 전문
    tail = md.split("## 7. 한계와 신뢰도")[1]
    assert "- Critic 미해결 — unresolved after 2 replan(s)\n  - RQ1 thin\n  - RQ2 [1] thin" in tail
    assert "['RQ1" not in tail                                       # 리스트 repr 이 그대로 찍히지 않음


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
    assert r["refs"] == 4 and (d / "report_v1.md").read_text(encoding="utf-8") == "OLD"
    md = (d / "report.md").read_text(encoding="utf-8")
    assert "| 3회 / 2회 |" in md and "$0.81 · 7.3분" in md
    rerender_run(d)                                                 # 두 번째는 v1 을 덮어쓰지 않음
    assert (d / "report_v1.md").read_text(encoding="utf-8") == "OLD"
