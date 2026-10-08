"""제출 전 품질 개선 묶음 (2026-10-08, docs/quality.md §4, ADR-12) — 파이프라인 지표는 그대로, 실행 경험·속도·견고성만.

- evaluate 병렬화: 배치가 병렬로 돌아도 결과는 배치 순서로 합쳐지고 전부 평가된다
- 캐시 키 정규화: 대소문자·공백만 다른 쿼리는 같은 키
- --exclude / --include: 제외 문헌은 레지스트리에 못 들어오고, 고정 문헌은 후보 상한과 무관하게 평가된다
- --resume: 중단된 실행을 같은 폴더에서 이어가며 끝난 노드(검색·평가)를 다시 돌리지 않는다
- export: BibTeX·RIS 번호가 report.md 참고문헌 순서와 같다
- progress: 이벤트 → 사람이 읽는 진행 줄
"""

import json
from types import SimpleNamespace

from research_agent import graph
from research_agent.config import GraphConfig
from research_agent.export import bib_keys, export_run, reference_order, to_bibtex, to_ris
from research_agent.llm import LLM
from research_agent.nodes import evaluate, search
from research_agent.progress import Progress
from research_agent.runlog import RunLogger
from research_agent.schemas import Evidence, EvidenceTable, RunState
from research_agent.tools import Tools, arxiv, normalize_id, openalex
from research_agent.tools.cache import ToolCache

from .test_graph import BRIEF_TEXT, PLAN, TF, FakeParse, _ctx, _ev, _paper, _settings, _state_with_papers
from .test_report import _brief, _papers

CLEAN = {"issues": []}
SYN = {"consensus": [{"statement": "c", "evidence_ids": ["10.1/p3", "10.1/p2"]}], "conflicts": [], "conditional": [], "coverage_note": "n"}
GAPS = {"gaps": [{"description": "g", "evidence_ids": ["10.1/p3", "10.1/p2"], "proposed_rq": "q", "method": "m", "data": "d"}]}


def _eval_from_prompt(kw):
    text = kw["messages"][0]["content"]
    ids = [l.split("id: ")[1] for l in text.splitlines() if l.startswith("--- id: ")]
    return EvidenceTable(items=[Evidence(**_ev(i, rq=("rq1", "rq2", "rq3"))) for i in ids])


# ---- D1 evaluate 병렬화 ---------------------------------------------------------

def test_evaluate_parallel_batches_merge_in_order(tmp_path):
    st = _state_with_papers(6)
    for p in st.papers.values():
        p.sub_rq_ids = ["rq1", "rq2"]
    ctx, fake = _ctx(tmp_path, [_eval_from_prompt] * 3, evaluate_per_subrq=6, evaluate_batch=2, evaluate_workers=3)
    evaluate.run(st, ctx)
    ids = [e.paper_id for e in st.evidence.items]
    assert sorted(ids) == sorted(p.id for p in st.papers.values()) and len(fake.messages.calls) == 3
    assert ids == [p.id for p in evaluate.select_candidates(st, 6)]     # 병렬이어도 합치는 순서 = 후보 순서
    ev = [json.loads(l) for l in (ctx.log.dir / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    b = next(e for e in ev if e["kind"] == "evaluate_batches")
    assert b["batches"] == 3 and b["workers"] == 3
    assert ctx.log.llm_calls == 3   # 락 아래 합산


# ---- A2 캐시 키 정규화 ----------------------------------------------------------

def test_cache_key_ignores_case_and_whitespace():
    a = ToolCache.key("openalex", {"query": "LLM  graduate productivity ", "per_page": 15, "from_year": None})
    b = ToolCache.key("openalex", {"query": "llm graduate productivity", "per_page": 15, "from_year": None})
    c = ToolCache.key("openalex", {"query": "productivity graduate llm", "per_page": 15, "from_year": None})
    assert a == b and a != c     # 단어 순서는 다른 쿼리


# ---- C4 --exclude / --include ---------------------------------------------------

def test_normalize_id():
    assert normalize_id("https://doi.org/10.1/ABC") == "10.1/abc"
    assert normalize_id("DOI:10.1/x") == "10.1/x"
    assert normalize_id("https://arxiv.org/abs/2401.00001") == "arxiv:2401.00001"


def test_exclude_keeps_paper_out_of_registry(tmp_path, monkeypatch):
    monkeypatch.setattr(openalex, "search", lambda q, **kw: [_paper(1), _paper(2)])
    t = Tools(_settings(tmp_path), use_cache=False, exclude=["https://doi.org/10.1/P1"])
    got = t.search_openalex("q", sub_rq_id="rq1")
    assert [p.id for p in got] == ["10.1/p2"] and "10.1/p1" not in t.papers


def test_include_pins_paper_into_every_subrq_and_evaluate(tmp_path, monkeypatch):
    monkeypatch.setattr(openalex, "search", lambda q, **kw: [_paper(i, cites=10 - i) for i in range(5)])
    monkeypatch.setattr(arxiv, "search", lambda q, **kw: [])
    monkeypatch.setattr(search.time, "sleep", lambda s: None)
    monkeypatch.setattr(openalex, "get_by_doi", lambda doi, **kw: _paper(77, cites=0, year=1999) if doi == "10.1/p77" else None)
    ctx, fake = _ctx(tmp_path, [_eval_from_prompt] * 4, evaluate_per_subrq=2, evaluate_batch=10)
    ctx.tools.include_ids = ["10.1/p77", "10.1/missing"]
    st = RunState(topic="t", topic_frame=TF, plan=PLAN.model_copy(deep=True))
    search.run(st, ctx)
    p = st.papers["10.1/p77"]
    assert p.pinned and set(p.sub_rq_ids) == {"rq1", "rq2", "rq3"}
    assert any("--include" in n and "10.1/missing" in n for n in st.notes)
    cand = evaluate.select_candidates(st, 2)
    assert "10.1/p77" in {c.id for c in cand}        # 피인용 0·1999년이라 상한 밖이지만 고정이라 포함
    evaluate.run(st, ctx)
    assert any(e.paper_id == "10.1/p77" for e in st.evidence.items)


# ---- C3 --resume ---------------------------------------------------------------

def test_resume_skips_finished_nodes_and_keeps_cost(tmp_path, monkeypatch):
    oa_calls = []
    monkeypatch.setattr(openalex, "search", lambda q, **kw: oa_calls.append(q) or [_paper(i, cites=i) for i in range(4)])
    monkeypatch.setattr(arxiv, "search", lambda q, **kw: [])
    monkeypatch.setattr(search.time, "sleep", lambda s: None)
    monkeypatch.setattr(graph, "RunLogger", lambda topic, mode, **kw: RunLogger(topic, mode, runs_dir=tmp_path, **kw))
    s = _settings(tmp_path, evaluate_per_subrq=3, evaluate_batch=10, search_min_per_subrq=1)
    s.graph = GraphConfig(critic="full", max_replans=2)

    fake1 = SimpleNamespace(messages=FakeParse([TF.model_dump(), PLAN.model_dump(), _eval_from_prompt]))
    monkeypatch.setattr(graph, "LLM", lambda settings, log: LLM(settings, log, client=fake1))
    state1, log1 = graph.run_graph("t", s, until="evaluate")          # 평가까지 하고 "중단"
    assert state1.brief is None and (log1.dir / "state.json").exists()
    n_search = len(oa_calls)
    cost1 = json.loads((log1.dir / "cost.json").read_text(encoding="utf-8"))
    assert cost1["status"] == "partial:evaluate" and cost1["llm_calls"] == 3

    fake2 = SimpleNamespace(messages=FakeParse([SYN, GAPS, CLEAN, BRIEF_TEXT]))
    monkeypatch.setattr(graph, "LLM", lambda settings, log: LLM(settings, log, client=fake2))
    state2, log2 = graph.run_graph("", s, resume_from=log1.dir)
    assert log2.dir == log1.dir and state2.brief is not None and state2.topic == "t"
    assert len(oa_calls) == n_search                                   # 검색을 다시 하지 않음
    assert len(fake2.messages.calls) == 4                              # 평가도 다시 하지 않음
    assert [e.paper_id for e in state2.evidence.items] == [e.paper_id for e in state1.evidence.items]
    cost2 = json.loads((log1.dir / "cost.json").read_text(encoding="utf-8"))
    assert cost2["status"] == "ok" and cost2["llm_calls"] == 7 and cost2["resumed_from"] == log1.dir.name
    ev = [json.loads(l) for l in (log1.dir / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    kinds = [e["kind"] for e in ev]
    assert "resumed" in kinds and [e["node"] for e in ev if e["kind"] == "node_skipped"] == ["understand", "plan", "search", "evaluate"]
    assert (log1.dir / "report.md").exists()


def test_resume_refuses_finished_or_foreign_run(tmp_path, monkeypatch):
    import pytest
    (tmp_path / "state.json").write_text(RunState(topic="other").model_dump_json(), encoding="utf-8")
    s = _settings(tmp_path)
    with pytest.raises(ValueError, match="주제가 다르다"):
        graph.run_graph("t", s, resume_from=tmp_path)
    with pytest.raises(ValueError, match="state.json"):
        graph.run_graph("t", s, resume_from=tmp_path / "nope")


# ---- C5 export ------------------------------------------------------------------

def test_export_numbering_matches_report(tmp_path):
    b, ps = _brief(), _papers()
    order = reference_order(b, ps)
    assert order[0] == "10.1/p0" and "10.1/p3" not in order      # 관련성 1 로 버려진 p3 는 번호 없음
    bib = to_bibtex(b, ps)
    assert bib.count("@") == len(order) and "[1] in report.md" in bib and "doi = {10.1/p0}" in bib
    assert "eprint = {0009.00001}" in bib and "author = {B1 and B2 and B3 and B4}" in bib
    ris = to_ris(b, ps)
    assert ris.count("ER  - ") == len(order) and "TY  - JOUR" in ris and "DO  - 10.1/p0" in ris
    keys = bib_keys(["10.1/p0", "10.1/p1"], {"10.1/p0": ps["10.1/p0"], "10.1/p1": ps["10.1/p0"]})
    assert keys["10.1/p0"] != keys["10.1/p1"] and keys["10.1/p1"].endswith("a")   # 같은 키 충돌 → 접미

    d = tmp_path / "run"
    d.mkdir()
    (d / "brief.json").write_text(b.model_dump_json(), encoding="utf-8")
    (d / "papers.json").write_text(json.dumps({k: v.model_dump() for k, v in ps.items()}), encoding="utf-8")
    r = export_run(d, "ris")
    assert r["refs"] == len(order) and (d / "references.ris").exists()


# ---- C1 progress ---------------------------------------------------------------

def test_progress_lines_from_events(tmp_path):
    lines = []
    log = RunLogger("주제", "graph", runs_dir=tmp_path)
    log.listeners.append(Progress(lines.append))
    log.event("node_start", node="search", round=0)
    log.llm(role="evaluate", model="m", input_tokens=10, output_tokens=5, cost_usd=0.01, attempt=1, ok=True)
    log.event("node_check", node="search", attempt=1, issues=[], counts={"rq1": 12, "rq2": 9})
    log.event("critique", round=1, passed=False, issues=["sub-RQs under-covered: ['rq2']"], llm_ran=False,
              llm_major=[], llm_minor=[], uncovered=["rq2"], actions=[])
    log.event("replan", round=1, rationale="r", queries={"rq2": ["a", "b"]})
    log.event("node_end", node="search", round=0)
    text = "\n".join(lines)
    assert "[r1] 문헌 탐색" in text and "후보 21편" in text and "Critic r1: 미달" in text and "rq2 +2개" in text
    assert "$0.01" in text and "LLM 1회" in text
