"""W4 — LLM-judge (judge.py) 와 ablation 공정성용 계획 재사용(graph `plan_from`). LLM 은 가짜.

검증하는 것
- JudgeResult.check: 항목 누락·중복·점수 범위·빈 인용을 잡는다
- judge_run: 결정적 검증 실패 → 1회 되먹여 재호출, judge.json·judge_events.jsonl 이 실행 폴더에 남고 원 cost.json 은 그대로
- consistency_flags: 결정적 지표 미달인데 4점 이상이면 표시 (점수는 안 바꿈)
- judgeable_runs: report.md 있고 judge.json 없는 것만, --force 면 전부
- run_graph(plan_from=...): understand·plan LLM 호출 없이 이전 실행의 계획을 쓰고, 주제가 다르면 거부
"""

import json
from types import SimpleNamespace

import pytest

from research_agent import graph, judge
from research_agent.llm import LLM
from research_agent.runlog import RunLogger
from research_agent.schemas import Claim, Evidence, EvidenceTable, Gap, GapList, JudgeItem, JudgeResult, Synthesis
from research_agent.tools import arxiv, openalex
from research_agent.nodes import search

from .test_graph import BRIEF_TEXT, PLAN, TF, FakeParse, _ev, _paper, _settings


def _items(scores=None, **over):
    scores = scores or {f"J{i}": 4 for i in range(1, 8)}
    return [JudgeItem(id=k, score=v, quote=over.get("quote", "q"), reason="r") for k, v in scores.items()]


GOOD = {"items": [i.model_dump() for i in _items()], "overall_comment": "ok"}


# ---- schema ----------------------------------------------------------------------

def test_judge_result_check_catches_missing_dup_range_and_empty_quote():
    assert JudgeResult(items=_items(), overall_comment="c").check() == []
    r = JudgeResult(items=_items({"J1": 6, "J2": 0, "J3": 3}), overall_comment="c")
    issues = r.check()
    assert any("missing items ['J4', 'J5', 'J6', 'J7']" in i for i in issues)
    assert any("J1: score 6" in i for i in issues) and any("J2: score 0" in i for i in issues)
    r = JudgeResult(items=_items() + _items({"J1": 2}), overall_comment="c")
    assert any("duplicated items ['J1']" in i for i in r.check())
    r = JudgeResult(items=_items(quote="  "), overall_comment="c")
    assert sum("quote is empty" in i for i in r.check()) == 7
    assert JudgeResult(items=_items({"J1": 5, "J2": 2}), overall_comment="c").mean == 3.5


# ---- judge_run ---------------------------------------------------------------------

def _run_dir(tmp_path, checks=None, name="20261004T000000Z_graph_t"):
    d = tmp_path / name
    d.mkdir()
    (d / "report.md").write_text("# Research Brief: t\n\n## 요약\n본문\n", encoding="utf-8")
    (d / "cost.json").write_text(json.dumps({"status": "ok", "llm_calls": 3, "cost_usd": 0.1,
                                             "checks": checks or {"citation_verified_rate": 1.0, "sub_rqs": 4, "sub_rqs_covered": 4,
                                                                  "gaps": 3, "gaps_with_2_evidence": 3}}), encoding="utf-8")
    return d


def _client(tmp_path, outputs):
    return _settings(tmp_path), SimpleNamespace(messages=FakeParse(outputs))


def test_judge_run_writes_judge_json_and_leaves_cost_json_alone(tmp_path):
    d = _run_dir(tmp_path)
    before = (d / "cost.json").read_text(encoding="utf-8")
    s, client = _client(tmp_path, [GOOD])
    out = judge.judge_run(d, s, client=client)
    assert out["mean"] == 4.0 and out["scores"]["J7"] == 4 and out["flags"] == [] and out["llm_calls"] == 1
    assert out["model"] == "j"                               # settings.llm.judge_model 이 기본
    j = json.loads((d / "judge.json").read_text(encoding="utf-8"))
    assert [it["id"] for it in j["items"]] == [f"J{i}" for i in range(1, 8)] and j["items"][0]["name"] == "주제 이해의 정확성"
    assert (d / "judge_events.jsonl").exists() and not (d / "events.jsonl").exists()   # 원 실행 로그와 분리
    assert (d / "cost.json").read_text(encoding="utf-8") == before
    call = client.messages.calls[0]
    assert call["model"] == "j" and "citation_verified_rate: 100%" in call["messages"][0]["content"]
    assert "Research brief (Markdown)" in call["messages"][0]["content"]


def test_judge_run_feeds_back_check_failure_once(tmp_path):
    d = _run_dir(tmp_path)
    bad = {"items": [i.model_dump() for i in _items({"J1": 4})], "overall_comment": "c"}   # J2~J7 누락
    s, client = _client(tmp_path, [bad, GOOD])
    out = judge.judge_run(d, s, client=client)
    assert out["llm_calls"] == 2 and out["notes"] == []
    second = client.messages.calls[1]["messages"][0]["content"]
    assert "failed these checks" in second and "missing items" in second


def test_judge_run_keeps_unresolved_note_and_truncates_long_report(tmp_path, monkeypatch):
    d = _run_dir(tmp_path)
    (d / "report.md").write_text("x" * 50, encoding="utf-8")
    monkeypatch.setattr(judge, "MAX_REPORT_CHARS", 10)
    bad = {"items": [i.model_dump() for i in _items({"J1": 4})], "overall_comment": "c"}
    s, client = _client(tmp_path, [bad, bad])
    out = judge.judge_run(d, s, client=client)
    assert any("report truncated" in n for n in out["notes"]) and any("unresolved checks" in n for n in out["notes"])
    assert "[... truncated for grading ...]" in client.messages.calls[0]["messages"][0]["content"]


def test_judge_run_refuses_unfinished_run(tmp_path):
    d = tmp_path / "20261004T000000Z_graph_t"
    d.mkdir()
    s = _settings(tmp_path)
    with pytest.raises(ValueError, match="report.md"):
        judge.judge_run(d, s, client=SimpleNamespace())


def test_consistency_flags_mark_contradictions_without_changing_scores():
    r = JudgeResult(items=_items({f"J{i}": 5 for i in range(1, 8)}), overall_comment="c")
    checks = {"citation_verified_rate": 0.9, "sub_rqs": 5, "sub_rqs_covered": 3, "gaps": 4, "gaps_with_2_evidence": 2,
              "conflicts": 2, "conflicts_with_hypothesis": 1}
    flags = judge.consistency_flags(r, checks)
    assert [f[:2] for f in flags] == ["J2", "J5", "J3", "J4"] and r.items[0].score == 5
    assert judge.consistency_flags(JudgeResult(items=_items({f"J{i}": 3 for i in range(1, 8)}), overall_comment="c"), checks) == []
    assert judge.consistency_flags(r, {}) == []            # 지표 없음(옛 실행) → 표시 없음


def test_judgeable_runs_filters(tmp_path):
    a = _run_dir(tmp_path, name="20261004T000001Z_graph_a")
    b = _run_dir(tmp_path, name="20261004T000002Z_baseline_b")
    (b / "judge.json").write_text("{}", encoding="utf-8")
    (tmp_path / "20261004T000003Z_graph_c").mkdir()         # report.md 없음 (미완주)
    assert [d.name for d in judge.judgeable_runs(tmp_path)] == [a.name]
    assert [d.name for d in judge.judgeable_runs(tmp_path, force=True)] == [a.name, b.name]
    assert judge.judgeable_runs(tmp_path, mode="baseline") == []
    assert judge.judgeable_runs(tmp_path, since="20261004T000002Z", force=True) == [b]


# ---- graph plan_from -------------------------------------------------------------------

def _fake_graph(tmp_path, monkeypatch, outputs):
    monkeypatch.setattr(openalex, "search", lambda q, **kw: [_paper(i, cites=i) for i in range(4)])
    monkeypatch.setattr(arxiv, "search", lambda q, **kw: [_paper(9, "arxiv")])
    monkeypatch.setattr(search.time, "sleep", lambda s: None)
    fake = SimpleNamespace(messages=FakeParse(outputs))
    s = _settings(tmp_path, evaluate_per_subrq=3, evaluate_batch=3, search_min_per_subrq=1)
    monkeypatch.setattr(graph, "RunLogger", lambda topic, mode: RunLogger(topic, mode, runs_dir=tmp_path))
    monkeypatch.setattr(graph, "LLM", lambda settings, log: LLM(settings, log, client=fake))
    return s, fake


def test_graph_plan_from_skips_understand_and_plan(tmp_path, monkeypatch):
    src = tmp_path / "20261004T000000Z_graph_t"
    src.mkdir()
    (src / "topic_frame.json").write_text(TF.model_dump_json(), encoding="utf-8")
    (src / "plan.json").write_text(PLAN.model_dump_json(), encoding="utf-8")

    def eval_batch(kw):
        text = kw["messages"][0]["content"]
        ids = [l.split("id: ")[1] for l in text.splitlines() if l.startswith("--- id: ")]
        return EvidenceTable(items=[Evidence(**_ev(i, rq=("rq1", "rq2", "rq3"))) for i in ids])
    syn = Synthesis(consensus=[Claim(statement="c", evidence_ids=["10.1/p3", "10.1/p2"])], conflicts=[], conditional=[], coverage_note="n").model_dump()
    gaps = GapList(gaps=[Gap(description="g", evidence_ids=["10.1/p3", "10.1/p2"], proposed_rq="q", method="m", data="d")]).model_dump()
    # frame·plan 출력이 없다 — 재사용되므로 LLM 이 호출되면 FakeParse 가 비어 IndexError 로 실패한다
    s, fake = _fake_graph(tmp_path, monkeypatch, [eval_batch, eval_batch, eval_batch, syn, gaps, {"issues": []}, BRIEF_TEXT])
    state, log = graph.run_graph(TF.original_topic, s, plan_from=src)
    assert state.brief is not None and state.plan == PLAN and state.topic_frame == TF
    assert fake.messages.outputs == []
    kinds = [json.loads(l)["kind"] for l in (log.dir / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    assert kinds.count("node_reused") == 2 and kinds.count("node_start") == 6     # understand·plan 은 node_start 없음
    cost = json.loads((log.dir / "cost.json").read_text(encoding="utf-8"))
    assert cost["plan_from"] == src.name and cost["model"] == "m" and cost["max_replans"] == 2
    assert (log.dir / "plan.json").exists() and (log.dir / "topic_frame.json").exists()   # 복사돼 있어 이 실행도 plan 공급원이 된다


def test_graph_plan_from_rejects_other_topic_or_missing_files(tmp_path, monkeypatch):
    src = tmp_path / "20261004T000000Z_graph_t"
    src.mkdir()
    (src / "topic_frame.json").write_text(TF.model_dump_json(), encoding="utf-8")
    (src / "plan.json").write_text(PLAN.model_dump_json(), encoding="utf-8")
    s, _ = _fake_graph(tmp_path, monkeypatch, [])
    state, log = graph.run_graph("another topic", s, plan_from=src)
    cost = json.loads((log.dir / "cost.json").read_text(encoding="utf-8"))
    assert cost["status"] == "error" and state.brief is None                    # 죽지 않고 error 로 기록 (O1)
    assert "주제가 다르다" in (log.dir / "traceback.txt").read_text(encoding="utf-8")
    state, log = graph.run_graph(TF.original_topic, s, plan_from=tmp_path / "nope")
    assert json.loads((log.dir / "cost.json").read_text(encoding="utf-8"))["status"] == "error"
