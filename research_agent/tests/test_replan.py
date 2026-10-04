"""W3 — Critic LLM 비판 + Replan 루프. HTTP·LLM 모두 가짜.

검증하는 것
- critic: 결정적 통과 → LLM 비판 호출, major 이슈면 미통과. critic=deterministic 이면 LLM 호출 없음
- replan: 모르는 sub-RQ·기존과 같은 쿼리는 되먹여 재호출, 새 쿼리가 계획에 덧붙음, replan_count 증가
- evaluate: 증분 — 이미 평가한 문헌은 건너뛰고 only_sub_rqs 의 새 후보만 평가해 기존 표에 합침
- graph: Critic 미달 → replan → 해당 sub-RQ 만 재검색·재평가 → Critic 통과 (Replan 이 결과를 바꿈)
- graph: 상한 도달 시 미달 항목이 notes 에 남고 write 까지 간다
"""

import json
from types import SimpleNamespace

from research_agent import graph
from research_agent.config import GraphConfig
from research_agent.llm import LLM
from research_agent.nodes import critic, evaluate, replan, search
from research_agent.runlog import RunLogger
from research_agent.schemas import Evidence, EvidenceTable, GapList, RunState, Synthesis
from research_agent.tools import arxiv, openalex

from .test_graph import BRIEF_TEXT, PLAN, TF, FakeParse, _ctx, _ev, _full_state, _paper, _settings, _state_with_papers

MAJOR = {"issues": [{"severity": "major", "where": "evidence", "sub_rq_id": "rq1",
                     "problem": "rq1 rests on commentaries only", "action": "search rq1: empirical studies"}]}
MINOR = {"issues": [{"severity": "minor", "where": "synthesis", "sub_rq_id": None, "problem": "p", "action": "synthesize: x"}]}
CLEAN = {"issues": []}


# ---- critic -------------------------------------------------------------------

def test_critic_runs_llm_after_deterministic_pass_and_fails_on_major(tmp_path):
    st = _full_state()
    ctx, fake = _ctx(tmp_path, [MAJOR])
    critic.run(st, ctx)
    cr = st.critiques[-1]
    assert cr.llm_ran and not cr.passed and cr.deterministic_issues == []
    assert cr.uncovered_sub_rqs == ["rq1"] and cr.actions == ["search rq1: empirical studies"]
    assert "Evidence table" in fake.messages.calls[0]["messages"][0]["content"]


def test_critic_persisting_major_after_research_becomes_limitation(tmp_path):
    """같은 sub-RQ 를 이미 재검색했는데 같은 'search' major 가 남으면 → 통과 + 한계 기록 (무한 Replan 방지)."""
    from research_agent.schemas import ReplanItem, ReplanPlan
    st = _full_state()
    st.replans.append(ReplanPlan(items=[ReplanItem(sub_rq_id="rq1", reason="r", queries=["q"])], rationale="x"))
    ctx, _ = _ctx(tmp_path, [MAJOR])                    # MAJOR: search rq1 — 이미 재검색한 sub-RQ
    critic.run(st, ctx)
    cr = st.critiques[-1]
    assert cr.passed and cr.llm_ran and cr.uncovered_sub_rqs == [] and cr.actions == []
    assert any(n.startswith("critic: major issue(s) persist after re-search") and "rq1" in n for n in st.notes)

    st = _full_state()                                   # 재검색한 적 없는 sub-RQ 면 여전히 미통과
    st.replans.append(ReplanPlan(items=[ReplanItem(sub_rq_id="rq2", reason="r", queries=["q"])], rationale="x"))
    ctx, _ = _ctx(tmp_path, [MAJOR])
    critic.run(st, ctx)
    assert not st.critiques[-1].passed and st.notes == []


def test_critic_minor_only_passes(tmp_path):
    st = _full_state()
    ctx, _ = _ctx(tmp_path, [MINOR])
    critic.run(st, ctx)
    assert st.critiques[-1].passed and len(st.critiques[-1].llm_issues) == 1


def test_critic_skips_llm_when_deterministic_fails_or_mode_deterministic(tmp_path):
    st = _full_state()
    ctx, fake = _ctx(tmp_path, [MAJOR])
    ctx.settings.tools.min_evidence_per_subrq = 5          # 결정적 검사 실패 → LLM 안 부름
    critic.run(st, ctx)
    assert not st.critiques[-1].passed and not st.critiques[-1].llm_ran and fake.messages.calls == []

    st = _full_state()
    ctx, fake = _ctx(tmp_path, [MAJOR])
    ctx.settings.graph = GraphConfig(critic="deterministic")
    critic.run(st, ctx)
    assert st.critiques[-1].passed and not st.critiques[-1].llm_ran and fake.messages.calls == []


# ---- replan -------------------------------------------------------------------

def test_replan_rejects_bad_items_then_extends_plan(tmp_path):
    st = _full_state()
    ctx, fake = _ctx(tmp_path, [MAJOR])
    ctx.settings.tools.min_evidence_per_subrq = 5
    critic.run(st, ctx)                                     # rq1·rq2·rq3 모두 under-covered
    bad = {"items": [{"sub_rq_id": "rq9", "reason": "r", "queries": ["x"]},
                     {"sub_rq_id": "rq1", "reason": "r", "queries": ["A1"]}], "rationale": "bad"}   # 모르는 id + 기존 쿼리 재사용
    good = {"items": [{"sub_rq_id": "rq1", "reason": "r", "queries": ["new q1"]},
                      {"sub_rq_id": "rq2", "reason": "r", "queries": ["longitudinal q2 study", "q2 survey"]},
                      {"sub_rq_id": "rq3", "reason": "r", "queries": ["new q3"]}], "rationale": "ok"}
    ctx, fake = _ctx(tmp_path, [bad, good])
    replan.run(st, ctx)
    assert len(fake.messages.calls) == 2
    feedback = fake.messages.calls[1]["messages"][0]["content"]
    assert "unknown sub_rq_id rq9" in feedback and "already used" in feedback
    assert "missing the sub-RQs the critic asked to re-search: ['rq2', 'rq3']" in feedback   # bad 에는 rq2·rq3 가 없었다
    rq2 = next(s for s in st.plan.sub_rqs if s.id == "rq2")
    assert rq2.queries == ["a2", "b2", "longitudinal q2 study", "q2 survey"]
    assert st.replan_count == 1
    assert st.replans[-1].as_extra_queries() == {"rq1": ["new q1"], "rq2": ["longitudinal q2 study", "q2 survey"], "rq3": ["new q3"]}
    assert st.notes == [] and (ctx.log.dir / "replan_1.json").exists()
    assert "flagged" in fake.messages.calls[0]["messages"][0]["content"]


def test_replan_empty_items_for_flagged_subrqs_is_rejected_then_falls_back(tmp_path):
    """Haiku 가 rationale 에만 쿼리를 적고 items 를 비워 보낸 사례(2026-10-04 T1 실행) — 되먹이고, 끝까지 비면 결정적 fallback."""
    st = _full_state()
    ctx, _ = _ctx(tmp_path, [MAJOR])            # LLM major: search rq1 → uncovered ['rq1']
    critic.run(st, ctx)
    assert st.critiques[-1].uncovered_sub_rqs == ["rq1"]
    empty = {"items": [], "rationale": "rq1 needs longitudinal queries"}
    ctx, fake = _ctx(tmp_path, [empty, empty])
    replan.run(st, ctx)
    assert len(fake.messages.calls) == 2
    assert "missing the sub-RQs the critic asked to re-search: ['rq1']" in fake.messages.calls[1]["messages"][0]["content"]
    assert [it.sub_rq_id for it in st.replans[-1].items] == ["rq1"]
    assert st.replans[-1].items[0].queries == [replan.fallback_query("q1")]
    assert any(n.startswith("replan: LLM output incomplete") for n in st.notes)


def test_replan_truncates_queries_to_three(tmp_path):
    st = _full_state()
    ctx, _ = _ctx(tmp_path, [MAJOR])
    critic.run(st, ctx)
    six = {"items": [{"sub_rq_id": "rq1", "reason": "r", "queries": [f"new q1 {i}" for i in range(6)]}], "rationale": "ok"}
    ctx, _ = _ctx(tmp_path, [six])
    replan.run(st, ctx)                                  # 스키마 상한이 아니라 코드에서 자른다 — SDK parse 단계에서 죽지 않게
    assert st.replans[-1].items[0].queries == ["new q1 0", "new q1 1", "new q1 2"]
    assert next(s for s in st.plan.sub_rqs if s.id == "rq1").queries == ["a1", "b1", "new q1 0", "new q1 1", "new q1 2"]


def test_fallback_query_strips_stopwords():
    q = replan.fallback_query("How does generative AI use affect the research productivity of graduate students?")
    assert q == "generative ai use research productivity graduate empirical study"


# ---- evaluate (증분) ------------------------------------------------------------

def test_evaluate_incremental_skips_evaluated_and_restricts_to_targets(tmp_path):
    st = _state_with_papers(6)                              # p0..p2 → rq1, p3..p5 → rq2
    st.evidence = EvidenceTable(items=[Evidence(**_ev("10.1/p0")), Evidence(**_ev("10.1/p3", rq=("rq2",)))])
    out = [lambda kw: EvidenceTable(items=[Evidence(**_ev("10.1/p4", rq=("rq2",))), Evidence(**_ev("10.1/p5", rq=("rq2",)))])]
    ctx, fake = _ctx(tmp_path, out, evaluate_per_subrq=2, evaluate_batch=10)
    evaluate.run(st, ctx, only_sub_rqs={"rq2"})
    assert len(fake.messages.calls) == 1
    prompt = fake.messages.calls[0]["messages"][0]["content"]
    assert "10.1/p4" in prompt and "10.1/p5" in prompt and "10.1/p3" not in prompt and "10.1/p1" not in prompt
    assert sorted(e.paper_id for e in st.evidence.items) == ["10.1/p0", "10.1/p3", "10.1/p4", "10.1/p5"]


# ---- graph 루프 -----------------------------------------------------------------

def _run(tmp_path, monkeypatch, outputs, oa_calls, **tools):
    monkeypatch.setattr(openalex, "search", lambda q, **kw: oa_calls.append(q) or (
        [_paper(50)] if q.startswith("new") else [_paper(i, cites=i) for i in range(4)]))
    monkeypatch.setattr(arxiv, "search", lambda q, **kw: [])
    monkeypatch.setattr(search.time, "sleep", lambda s: None)
    fake = SimpleNamespace(messages=FakeParse(outputs))
    max_replans = tools.pop("max_replans", 2)
    base = dict(evaluate_per_subrq=3, evaluate_batch=10, search_min_per_subrq=1)
    base.update(tools)
    s = _settings(tmp_path, **base)
    s.graph = GraphConfig(critic="full", max_replans=max_replans)
    monkeypatch.setattr(graph, "RunLogger", lambda topic, mode: RunLogger(topic, mode, runs_dir=tmp_path))
    monkeypatch.setattr(graph, "LLM", lambda settings, log: LLM(settings, log, client=fake))
    return graph.run_graph("t", s)


def _eval_from_prompt(rq):
    def f(kw):
        text = kw["messages"][0]["content"]
        ids = [l.split("id: ")[1] for l in text.splitlines() if l.startswith("--- id: ")]
        return EvidenceTable(items=[Evidence(**_ev(i, rq=rq)) for i in ids])
    return f


SYN = Synthesis(consensus=[{"statement": "c", "evidence_ids": ["10.1/p3", "10.1/p2"]}], conflicts=[], conditional=[],
                coverage_note="n").model_dump()
GAPS = GapList(gaps=[{"description": "g", "evidence_ids": ["10.1/p3", "10.1/p2"], "proposed_rq": "q", "method": "m", "data": "d"}]).model_dump()
REPLAN_RQ2 = {"items": [{"sub_rq_id": "rq2", "reason": "0 relevant", "queries": ["new memory query"]}], "rationale": "rq2 thin"}


def test_graph_replan_changes_result(tmp_path, monkeypatch):
    oa_calls = []
    outputs = [TF.model_dump(), PLAN.model_dump(),
               _eval_from_prompt(("rq1", "rq3")),        # r0: rq2 에 관련 문헌 0 → 결정적 미달 (LLM 비판 생략)
               SYN, GAPS, REPLAN_RQ2,
               _eval_from_prompt(("rq2",)),              # r1: 새 후보 p50 만 평가
               SYN, GAPS, CLEAN,                         # r1: 결정적 통과 → LLM 비판 → 이슈 없음
               BRIEF_TEXT]
    state, log = _run(tmp_path, monkeypatch, outputs, oa_calls)

    assert state.brief is not None and state.replan_count == 1 and len(state.critiques) == 2
    assert not state.critiques[0].passed and not state.critiques[0].llm_ran
    assert state.critiques[1].passed and state.critiques[1].llm_ran
    assert oa_calls.count("new memory query") == 1 and oa_calls[-1] == "new memory query"   # 재검색은 rq2 새 쿼리만
    assert "new memory query" in next(s for s in state.plan.sub_rqs if s.id == "rq2").queries
    assert any(e.paper_id == "10.1/p50" and "rq2" in e.sub_rq_ids for e in state.evidence.items)
    assert len(state.evidence.items) == 5   # r0: 피인용 상위 3편(p1~p3) + r1: rq2 의 미평가 후보 p0·p50 — 기존 3편은 재평가하지 않음(증분)
    assert not any(n.startswith("critic:") for n in state.notes)                      # 최종 통과 → 미달 노트 없음
    cost = json.loads((log.dir / "cost.json").read_text(encoding="utf-8"))
    assert cost["replans"] == 1 and cost["critic_rounds"] == 2 and cost["final_critic_passed"] is True
    ev = [json.loads(l) for l in (log.dir / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    kinds = [e["kind"] for e in ev]
    assert kinds.count("node_start") == 14 and kinds.count("replan") == 1 and kinds.count("critique") == 2
    assert [e["node"] for e in ev if e["kind"] == "node_start" and e.get("round") == 1] == \
        ["search", "evaluate", "synthesize", "gap", "critic", "write"]
    assert (log.dir / "replan_1.json").exists() and (log.dir / "critique_2.json").exists()


def test_graph_replan_limit_records_unresolved(tmp_path, monkeypatch):
    oa_calls = []
    empty_replan = {"items": [], "rationale": "nothing to search"}
    outputs = [TF.model_dump(), PLAN.model_dump(),
               _eval_from_prompt(("rq1", "rq3")), SYN, GAPS,   # r0: rq2 미달
               empty_replan, empty_replan,                     # replan 1: 두 번 다 비어 옴 → rq2 fallback 쿼리
               SYN, GAPS,                                      # r1: fallback 검색은 이미 평가한 문헌만 → evaluate 호출 없음, 여전히 미달, 상한 1 → 종료
               BRIEF_TEXT]
    state, log = _run(tmp_path, monkeypatch, outputs, oa_calls, max_replans=1, evaluate_per_subrq=4)  # r0 에서 4편 전부 평가
    assert state.brief is not None and state.replan_count == 1 and len(state.critiques) == 2
    assert all(not c.passed for c in state.critiques)
    assert oa_calls[-1] == "q2 empirical study" and oa_calls.count("q2 empirical study") == 1    # fallback 재검색 1회
    assert any("critic: unresolved after 1 replan(s)" in n and "rq2" in n for n in state.notes)
    assert any(n.startswith("replan: LLM output incomplete") for n in state.notes)
    assert any("[auto] critic: unresolved" in l for l in state.brief.limitations)
    cost = json.loads((log.dir / "cost.json").read_text(encoding="utf-8"))
    assert cost["status"] == "ok" and cost["final_critic_passed"] is False
    kinds = [json.loads(l)["kind"] for l in (log.dir / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    assert "replan_limit" in kinds


def test_graph_skips_replan_when_budget_is_low(tmp_path, monkeypatch):
    """경과 시간이 상한의 60% 를 넘으면 Replan 없이 write 로 (완주 우선). 2026-10-04: Replan 2회 뒤 write 직전 10.1분 초과."""
    import time
    oa_calls = []
    outputs = [TF.model_dump(), PLAN.model_dump(), _eval_from_prompt(("rq1", "rq3")), SYN, GAPS, BRIEF_TEXT]  # rq2 미달이지만 replan 없음
    monkeypatch.setattr(openalex, "search", lambda q, **kw: [_paper(i, cites=i) for i in range(4)])
    monkeypatch.setattr(arxiv, "search", lambda q, **kw: [])
    monkeypatch.setattr(search.time, "sleep", lambda s: None)
    fake = SimpleNamespace(messages=FakeParse(outputs))
    s = _settings(tmp_path, evaluate_per_subrq=3, evaluate_batch=10, search_min_per_subrq=1)
    s.graph = GraphConfig(critic="full", max_replans=2)

    def old_logger(topic, mode):
        log = RunLogger(topic, mode, runs_dir=tmp_path)
        log._t0 = time.monotonic() - 7 * 60          # 이미 7분 경과 (상한 10분의 70%)
        return log
    monkeypatch.setattr(graph, "RunLogger", old_logger)
    monkeypatch.setattr(graph, "LLM", lambda settings, log: LLM(settings, log, client=fake))
    state, log = graph.run_graph("t", s)
    assert state.brief is not None and state.replan_count == 0 and len(state.critiques) == 1
    assert any("replan skipped for budget" in n for n in state.notes)
    cost = json.loads((log.dir / "cost.json").read_text(encoding="utf-8"))
    assert cost["status"] == "ok" and cost["final_critic_passed"] is False


def test_grace_write_after_limit(tmp_path):
    """상한에 걸려도 종합·Gap 이 있으면 write 를 1회 허용해 브리프를 남긴다."""
    from research_agent.config import Limits
    from research_agent.llm import CostLimitExceeded
    st = _full_state()
    ctx, _ = _ctx(tmp_path, [BRIEF_TEXT])
    ctx.settings.limits = Limits(max_cost_usd=0.0)       # 어떤 호출도 상한 초과
    ctx.log.cost_usd = 0.5
    import pytest
    with pytest.raises(CostLimitExceeded):
        ctx.llm.call(role="x", system="s", user="u", schema=Synthesis)
    assert graph.grace_write(st, ctx) is True
    assert st.brief is not None and any("hit the budget limit" in l for l in st.brief.limitations)
    assert ctx.llm.grace_calls == 0
    assert graph.grace_write(st, ctx) is False           # 이미 브리프 있음 → 아무것도 안 함


def test_graph_unexpected_error_is_recorded_not_raised(tmp_path, monkeypatch):
    """노드 안의 예상 밖 예외(2026-10-04: SDK parse ValidationError)에도 상태·비용·traceback 을 남기고 정상 종료 (goals.md O1)."""
    oa_calls = []
    outputs = [TF.model_dump(), PLAN.model_dump(), lambda kw: (_ for _ in ()).throw(RuntimeError("boom"))]
    state, log = _run(tmp_path, monkeypatch, outputs, oa_calls)
    assert state.brief is None and state.plan is not None
    cost = json.loads((log.dir / "cost.json").read_text(encoding="utf-8"))
    assert cost["status"] == "error" and cost["checks"] == {"submitted": False}
    assert "RuntimeError: boom" in (log.dir / "traceback.txt").read_text(encoding="utf-8")
    assert (log.dir / "state.json").exists()


def test_graph_critic_none_skips_gate(tmp_path, monkeypatch):
    oa_calls = []
    outputs = [TF.model_dump(), PLAN.model_dump(), _eval_from_prompt(("rq1", "rq3")), SYN, GAPS, BRIEF_TEXT]
    monkeypatch.setattr(openalex, "search", lambda q, **kw: [_paper(i, cites=i) for i in range(4)])
    monkeypatch.setattr(arxiv, "search", lambda q, **kw: [])
    monkeypatch.setattr(search.time, "sleep", lambda s: None)
    fake = SimpleNamespace(messages=FakeParse(outputs))
    s = _settings(tmp_path, evaluate_per_subrq=3, evaluate_batch=10, search_min_per_subrq=1)
    s.graph = GraphConfig(critic="none")
    monkeypatch.setattr(graph, "RunLogger", lambda topic, mode: RunLogger(topic, mode, runs_dir=tmp_path))
    monkeypatch.setattr(graph, "LLM", lambda settings, log: LLM(settings, log, client=fake))
    state, log = graph.run_graph("t", s)
    assert state.brief is not None and state.critiques == [] and state.replan_count == 0
    cost = json.loads((log.dir / "cost.json").read_text(encoding="utf-8"))
    assert cost["critic_mode"] == "none" and cost["final_critic_passed"] is None
