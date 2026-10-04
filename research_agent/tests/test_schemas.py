from research_agent.schemas import (
    Paper, ResearchPlan, SubRQ, Synthesis, Claim, Conflict, GapList, Gap, ResearchBrief,
)


def test_paper_doi_normalized():
    p = Paper(id="x", title="t", source="openalex", doi="https://doi.org/10.1000/ABC")
    assert p.doi == "10.1000/abc"


def test_plan_check_overlap():
    plan = ResearchPlan(
        sub_rqs=[
            SubRQ(id="rq1", question="q1", rationale="r", queries=["same query", "a"]),
            SubRQ(id="rq2", question="q2", rationale="r", queries=["same query", "b"]),
            SubRQ(id="rq3", question="q3", rationale="r", queries=["same query", "c"]),
        ],
        search_strategy="s",
    )
    assert any("overlap" in i for i in plan.check())


def test_synthesis_check_unknown_ids():
    s = Synthesis(
        consensus=[Claim(statement="x", evidence_ids=["known"])],
        conflicts=[Conflict(claim="c", side_a=Claim(statement="a", evidence_ids=["known"]),
                            side_b=Claim(statement="b", evidence_ids=["ghost"]), hypothesis_for_conflict="")],
        conditional=[], coverage_note="n",
    )
    issues = s.check({"known"})
    assert any("ghost" in i for i in issues)
    assert any("without hypothesis" in i for i in issues)


def test_gap_requires_two_evidence():
    import pydantic, pytest
    with pytest.raises(pydantic.ValidationError):
        Gap(description="d", evidence_ids=["one"], proposed_rq="q", method="m", data="d")


def test_brief_schema_exports():
    s = ResearchBrief.model_json_schema()
    assert "topic_frame" in s["properties"] and "gaps" in s["properties"]
