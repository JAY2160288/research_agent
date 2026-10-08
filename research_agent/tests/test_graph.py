"""search → evaluate → synthesize → gap → critic → write 와 전체 그래프 — HTTP·LLM 모두 가짜.

검증하는 것
- search: source_pref 분기, sub-RQ 태깅, 후보 부족 노트
- evaluate: sub-RQ 당 후보 상한·배치 분할·배치 밖 id 거절 후 재호출
- critic: 결정적 검사 5종이 각각 걸리는지
- write: 구조 섹션은 상태에서 조립, notes 가 limitations 로 자동 편입
- graph: end-to-end 로 brief/report/cost.json 생성, 노드 이벤트 8개
"""

import json
from types import SimpleNamespace

from research_agent import graph
from research_agent.config import Settings, LLMConfig, Price, Limits, ToolsConfig
from research_agent.llm import LLM
from research_agent.nodes import NodeContext, critic, evaluate, search, write
from research_agent.runlog import RunLogger
from research_agent.schemas import (Claim, Conflict, Evidence, EvidenceTable, Gap, GapList, Paper, ResearchPlan,
                                    RunState, SubRQ, Synthesis, TopicFrame, Variables)
from research_agent.tools import arxiv, openalex

# ---- 고정 데이터 ------------------------------------------------------------

TF = TopicFrame(original_topic="t", topic_en="t", domain="education", concepts=["a", "b", "c"],
                variables=Variables(independent=["x"], dependent=["y"], population="p"),
                synonyms_en=["s1", "s2", "s3"], research_question="Does x affect y?")
PLAN = ResearchPlan(sub_rqs=[
    SubRQ(id="rq1", question="q1", rationale="r", queries=["a1", "b1"], source_pref="openalex"),
    SubRQ(id="rq2", question="q2", rationale="r", queries=["a2", "b2"], source_pref="arxiv"),
    SubRQ(id="rq3", question="q3", rationale="r", queries=["a3", "b3"], source_pref="both"),
], search_strategy="s")


def _paper(i: int, src="openalex", abstract="abs", cites=0, year=2024):
    pid = f"arxiv:{i:04d}.00001" if src == "arxiv" else f"10.1/p{i}"
    return Paper(id=pid, title=f"P{i}", year=year, abstract=abstract, doi=None if src == "arxiv" else pid,
                 source=src, verified=True, cited_by_count=cites)


def _settings(tmp_path, **tools):
    base = dict(cache_dir=str(tmp_path / "c"), search_workers=2, search_min_per_subrq=3,
                evaluate_per_subrq=2, evaluate_batch=2, evaluate_workers=1,   # FakeParse 는 호출 순서대로 답하므로 순차
                min_relevance=3, min_evidence_per_subrq=1)
    base.update(tools)
    return Settings(llm=LLMConfig(model="m", judge_model="j"), pricing={"default": Price(input=1, output=1)},
                    limits=Limits(), tools=ToolsConfig(**base))


class FakeParse:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = []

    def parse(self, **kw):
        self.calls.append(kw)
        out = self.outputs.pop(0)
        if callable(out):
            out = out(kw)
        return SimpleNamespace(content=[SimpleNamespace(type="text", text="{}", parsed_output=out)],
                               usage=SimpleNamespace(input_tokens=10, output_tokens=5), stop_reason="end_turn")


def _ctx(tmp_path, outputs, **tools):
    s = _settings(tmp_path, **tools)
    log = RunLogger("t", "test", runs_dir=tmp_path)
    fake = SimpleNamespace(messages=FakeParse(outputs))
    from research_agent.tools import Tools
    return NodeContext(settings=s, llm=LLM(s, log, client=fake), tools=Tools(s, log, use_cache=False), log=log), fake


# ---- search -------------------------------------------------------------------

def test_search_routes_by_source_pref_and_tags(tmp_path, monkeypatch):
    oa_calls, ax_calls = [], []
    monkeypatch.setattr(openalex, "search", lambda q, **kw: oa_calls.append(q) or [_paper(len(oa_calls)), _paper(100)])
    monkeypatch.setattr(arxiv, "search", lambda q, **kw: ax_calls.append(q) or [_paper(200 + len(ax_calls), "arxiv")])
    monkeypatch.setattr(search.time, "sleep", lambda s: None)
    ctx, _ = _ctx(tmp_path, [])
    state = RunState(topic="t", topic_frame=TF, plan=PLAN)
    search.run(state, ctx)
    assert sorted(oa_calls) == ["a1", "a2", "a3", "b1", "b2", "b3"]   # OpenAlex 는 모든 sub-RQ 의 주력
    assert sorted(ax_calls) == ["a2", "a3", "b2", "b3"]               # arXiv 는 arxiv/both 보강
    assert "rq1" in state.papers["10.1/p100"].sub_rq_ids and "rq3" in state.papers["10.1/p100"].sub_rq_ids
    assert state.papers["arxiv:0201.00001"].sub_rq_ids == ["rq2"]
    assert not any("shortfall" in n for n in state.notes)            # 모든 sub-RQ ≥ 3 (OpenAlex 2×2 + 중복 p100)


def test_search_falls_back_to_crossref_when_openalex_fails(tmp_path, monkeypatch):
    """OpenAlex 429(일일 크레딧 소진, 2026-10-04 관찰) → 실패한 쿼리만 Crossref 로 (ADR-8). 결과 구조는 그대로."""
    from research_agent.tools import crossref
    cr_calls = []

    def oa(q, **kw):
        if q.startswith("a"):
            raise RuntimeError("429 Too Many Requests")
        return [_paper(1)]
    monkeypatch.setattr(openalex, "search", oa)
    monkeypatch.setattr(crossref, "search", lambda q, **kw: cr_calls.append(q) or [_paper(300 + len(cr_calls), "crossref")])
    monkeypatch.setattr(arxiv, "search", lambda q, **kw: [])
    monkeypatch.setattr(search.time, "sleep", lambda s: None)
    ctx, _ = _ctx(tmp_path, [], search_min_per_subrq=1)
    state = RunState(topic="t", topic_frame=TF, plan=PLAN)
    search.run(state, ctx)
    assert sorted(cr_calls) == ["a1", "a2", "a3"]                                   # 실패한 쿼리만 폴백
    assert any(p.source == "crossref" and p.verified for p in state.papers.values())
    assert any("OpenAlex failed for 3/6 queries" in n and "Crossref fallback answered 3" in n for n in state.notes)
    assert all(sum(1 for p in state.papers.values() if sq.id in p.sub_rq_ids) >= 1 for sq in PLAN.sub_rqs)


def test_search_circuit_breaker_disables_arxiv(tmp_path, monkeypatch):
    ax_calls = []

    def failing(q, **kw):
        ax_calls.append(q)
        raise RuntimeError("429 Too Many Requests")

    monkeypatch.setattr(openalex, "search", lambda q, **kw: [_paper(1), _paper(2), _paper(3)])
    monkeypatch.setattr(arxiv, "search", failing)
    monkeypatch.setattr(search.time, "sleep", lambda s: None)
    ctx, _ = _ctx(tmp_path, [], arxiv_max_failures=2)
    state = RunState(topic="t", topic_frame=TF, plan=PLAN)
    search.run(state, ctx)
    assert len(ax_calls) == 2                                          # 2회 실패 후 차단
    assert any("arXiv unavailable" in n for n in state.notes)
    assert all(sum(1 for p in state.papers.values() if sq.id in p.sub_rq_ids) >= 3 for sq in PLAN.sub_rqs)


# ---- evaluate -----------------------------------------------------------------

def _state_with_papers(n=6):
    st = RunState(topic="t", topic_frame=TF, plan=PLAN.model_copy(deep=True))  # replan 이 queries 를 덧붙이므로 테스트 간 공유 금지
    for i in range(n):
        p = _paper(i, cites=10 - i)
        p.sub_rq_ids = ["rq1"] if i < 3 else ["rq2"]
        st.papers[p.id] = p
    return st


def _ev(pid, rel=4, rq=("rq1",)):
    return {"paper_id": pid, "relevance": rel, "reliability": 3, "method": "survey", "finding": "f", "sub_rq_ids": list(rq)}


def test_evaluate_caps_per_subrq_batches_and_rejects_foreign_ids(tmp_path):
    st = _state_with_papers(6)
    # per_subrq=2 → rq1 에서 피인용 상위 p0,p1 / rq2 에서 p3,p4 → 4편, batch=2 → 2배치
    bad_then_good = [
        lambda kw: EvidenceTable(items=[Evidence(**_ev("10.1/p0")), Evidence(**_ev("10.1/ghost"))]),  # 배치 밖 id → 재호출
        lambda kw: EvidenceTable(items=[Evidence(**_ev("10.1/p0")), Evidence(**_ev("10.1/p1"))]),
        lambda kw: EvidenceTable(items=[Evidence(**_ev("10.1/p3", rq=("rq2",))), Evidence(**_ev("10.1/p4", rel=1, rq=("rq2",)))]),
    ]
    ctx, fake = _ctx(tmp_path, bad_then_good)
    evaluate.run(st, ctx)
    ids = sorted(e.paper_id for e in st.evidence.items)
    assert ids == ["10.1/p0", "10.1/p1", "10.1/p3", "10.1/p4"]
    assert len(fake.messages.calls) == 3
    assert "not in this batch" in fake.messages.calls[1]["messages"][0]["content"]
    assert (ctx.log.dir / "evidence.json").exists()


# ---- critic ------------------------------------------------------------------

def _full_state():
    st = _state_with_papers(4)
    st.evidence = EvidenceTable(items=[Evidence(**_ev("10.1/p0")), Evidence(**_ev("10.1/p1")),
                                       Evidence(**_ev("10.1/p3", rq=("rq2", "rq3")))])
    st.synthesis = Synthesis(consensus=[Claim(statement="c", evidence_ids=["10.1/p0", "10.1/p1"])],
                             conflicts=[], conditional=[], coverage_note="n")
    st.gaps = GapList(gaps=[Gap(description="g", evidence_ids=["10.1/p0", "10.1/p3"], proposed_rq="q", method="m", data="d")])
    return st


def test_critic_passes_on_clean_state():
    cr = critic.deterministic_checks(_full_state(), min_relevance=3, min_evidence_per_subrq=1)
    assert cr.passed and cr.actions == []


def test_critic_flags_each_check():
    st = _full_state()
    st.synthesis.consensus.append(Claim(statement="ghost", evidence_ids=["10.1/nope"]))          # 1. 미검증 인용
    st.synthesis.conflicts.append(Conflict(claim="x", side_a=Claim(statement="a", evidence_ids=["10.1/p0"]),
                                           side_b=Claim(statement="b", evidence_ids=["10.1/p1"]),
                                           hypothesis_for_conflict=""))                           # 5. 가설 없음
    st.gaps.gaps.append(Gap(description="thin", evidence_ids=["10.1/p0", "10.1/zzz"], proposed_rq="q", method="m", data="d"))  # 4.
    cr = critic.deterministic_checks(st, min_relevance=3, min_evidence_per_subrq=2)                  # 3. rq2·rq3 커버 부족
    assert not cr.passed
    joined = " ".join(cr.deterministic_issues)
    assert "unverified citations" in joined and "under-covered" in joined and "conflicts without hypothesis" in joined \
        and "gaps with < 2" in joined
    assert "rq2" in cr.uncovered_sub_rqs and "rq3" in cr.uncovered_sub_rqs
    assert any(a.startswith("rq2:") for a in cr.actions)


# ---- write + graph -----------------------------------------------------------

BRIEF_TEXT = {"executive_summary": "이 브리프는 네 편의 문헌을 바탕으로 합의와 상충, 공백을 정리한다. " * 4,
              "limitations": ["only abstracts were read"]}


def test_write_assembles_brief_and_merges_notes(tmp_path):
    st = _full_state()
    st.notes.append("search: candidate shortfall ['rq2: 1 < 3']")
    ctx, _ = _ctx(tmp_path, [BRIEF_TEXT])
    write.run(st, ctx)
    assert st.brief is not None and st.brief.gaps is st.gaps
    assert st.brief.limitations[0] == "only abstracts were read"
    assert any(l.startswith("[auto] search:") for l in st.brief.limitations)
    md = (ctx.log.dir / "report.md").read_text(encoding="utf-8")
    assert "## 7. 한계와 신뢰도" in md and "## 3. Evidence Table" in md and "P0 (2024)" in md


def test_graph_end_to_end_with_fakes(tmp_path, monkeypatch):
    monkeypatch.setattr(openalex, "search", lambda q, **kw: [_paper(i, cites=i) for i in range(4)])
    monkeypatch.setattr(arxiv, "search", lambda q, **kw: [_paper(9, "arxiv")])
    monkeypatch.setattr(search.time, "sleep", lambda s: None)
    frame = TF.model_dump()
    plan = PLAN.model_dump()
    syn = Synthesis(consensus=[Claim(statement="c", evidence_ids=["10.1/p3", "10.1/p2"])], conflicts=[], conditional=[],
                    coverage_note="n").model_dump()
    gaps = GapList(gaps=[Gap(description="g", evidence_ids=["10.1/p3", "10.1/p2"], proposed_rq="q", method="m", data="d")]).model_dump()

    def eval_batch(kw):  # 배치에 들어온 id 를 프롬프트에서 읽어 그대로 평가
        text = kw["messages"][0]["content"]
        ids = [l.split("id: ")[1] for l in text.splitlines() if l.startswith("--- id: ")]
        return EvidenceTable(items=[Evidence(**_ev(i, rq=("rq1", "rq2", "rq3"))) for i in ids])

    outputs = [frame, plan, eval_batch, eval_batch, eval_batch, syn, gaps, {"issues": []}, BRIEF_TEXT]  # critic=full → LLM 비판 1회
    fake = SimpleNamespace(messages=FakeParse(outputs))
    s = _settings(tmp_path, evaluate_per_subrq=3, evaluate_batch=3, search_min_per_subrq=1)
    monkeypatch.setattr(graph, "RunLogger", lambda topic, mode: RunLogger(topic, mode, runs_dir=tmp_path))
    monkeypatch.setattr(graph, "LLM", lambda settings, log: LLM(settings, log, client=fake))

    state, log = graph.run_graph("t", s)
    assert state.brief is not None and state.critiques and state.critiques[0].passed and state.critiques[0].llm_ran
    cost = json.loads((log.dir / "cost.json").read_text(encoding="utf-8"))
    assert cost["status"] == "ok" and cost["checks"]["citation_verified_rate"] == 1.0 and cost["critic_rounds"] == 1
    assert cost["replans"] == 0 and cost["final_critic_passed"] is True
    kinds = [json.loads(l)["kind"] for l in (log.dir / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    assert kinds.count("node_start") == 8 and "critique" in kinds
    for f in ("brief.json", "report.md", "papers.json", "state.json", "critique_1.json"):
        assert (log.dir / f).exists(), f
