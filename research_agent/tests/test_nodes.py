"""understand / plan 노드와 공통 checked_call 테스트 — LLM 은 messages.parse 를 흉내 내는 가짜 클라이언트."""

from types import SimpleNamespace

from research_agent.config import Settings, LLMConfig, Price, Limits, ToolsConfig
from research_agent.llm import LLM
from research_agent.nodes import NodeContext, plan, understand
from research_agent.runlog import RunLogger
from research_agent.schemas import RunState
from research_agent.tools import Tools

FRAME = {
    "original_topic": "t", "topic_en": "t", "domain": "education",
    "concepts": ["a", "b", "c"],
    "variables": {"independent": ["x"], "dependent": ["y"], "population": "grad students"},
    "synonyms_en": ["s1", "s2", "s3"],
    "research_question": "Does x affect y?",
}
PLAN_OK = {
    "sub_rqs": [{"id": f"rq{i}", "question": f"q{i}", "rationale": "r", "queries": [f"a{i}", f"b{i}"]} for i in (1, 2, 3)],
    "search_strategy": "s",
}
PLAN_DUP = {  # 쿼리 전부 동일 → overlap 검사 실패
    "sub_rqs": [{"id": f"rq{i}", "question": f"q{i}", "rationale": "r", "queries": ["same", "same2"]} for i in (1, 2, 3)],
    "search_strategy": "s",
}


class FakeMessages:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = []

    def parse(self, **kw):
        self.calls.append(kw)
        out = self.outputs.pop(0)
        return SimpleNamespace(content=[SimpleNamespace(type="text", text="{}", parsed_output=out)],
                               usage=SimpleNamespace(input_tokens=100, output_tokens=50), stop_reason="end_turn")


def _ctx(tmp_path, outputs):
    s = Settings(llm=LLMConfig(model="m", judge_model="j"), pricing={"default": Price(input=1, output=1)},
                 limits=Limits(), tools=ToolsConfig(cache_dir=str(tmp_path / "c")))
    log = RunLogger("t", "test", runs_dir=tmp_path)
    fake = SimpleNamespace(messages=FakeMessages(outputs))
    return NodeContext(settings=s, llm=LLM(s, log, client=fake), tools=Tools(s, log, use_cache=False), log=log), fake


def test_understand_fills_topic_frame(tmp_path):
    ctx, fake = _ctx(tmp_path, [FRAME])
    state = RunState(topic="t")
    understand.run(state, ctx)
    assert state.topic_frame is not None and state.topic_frame.domain == "education"
    assert state.notes == [] and (ctx.log.dir / "topic_frame.json").exists()
    assert len(fake.messages.calls) == 1
    assert fake.messages.calls[0]["max_tokens"] == ctx.settings.llm.node_max_tokens   # 노드 호출은 node_max_tokens (폭주 출력 차단)


def test_understand_retries_on_check_failure(tmp_path):
    bad = dict(FRAME, synonyms_en=["only-one"])  # 스키마는 통과하지만 check() 실패
    ctx, fake = _ctx(tmp_path, [bad, FRAME])
    state = RunState(topic="t")
    understand.run(state, ctx)
    assert state.topic_frame.synonyms_en == ["s1", "s2", "s3"]
    assert len(fake.messages.calls) == 2
    # 2번째 호출의 user 메시지에 이슈가 되먹여졌는지
    second_user = fake.messages.calls[1]["messages"][0]["content"]
    assert "synonyms_en < 3" in second_user


def test_understand_keeps_result_and_notes_when_still_failing(tmp_path):
    bad = dict(FRAME, synonyms_en=["only-one"])
    ctx, _ = _ctx(tmp_path, [bad, bad])
    state = RunState(topic="t")
    understand.run(state, ctx)
    assert state.topic_frame is not None  # 죽지 않고 결과 유지
    assert any("understand" in n and "synonyms_en" in n for n in state.notes)


def test_plan_retries_on_overlap(tmp_path):
    ctx, fake = _ctx(tmp_path, [FRAME, PLAN_DUP, PLAN_OK])
    state = RunState(topic="t")
    understand.run(state, ctx)
    plan.run(state, ctx)
    assert [s.id for s in state.plan.sub_rqs] == ["rq1", "rq2", "rq3"]
    assert state.notes == []
    assert len(fake.messages.calls) == 3
    assert "overlap" in fake.messages.calls[2]["messages"][0]["content"]
    assert (ctx.log.dir / "plan.json").exists()


def test_graph_runner_until_plan(tmp_path, monkeypatch):
    """러너가 understand → plan 을 순서대로 돌리고 state.json 과 cost.json 을 남기는지."""
    import json
    from research_agent import graph
    s = Settings(llm=LLMConfig(model="m", judge_model="j"), pricing={"default": Price(input=1, output=1)},
                 limits=Limits(), tools=ToolsConfig(cache_dir=str(tmp_path / "c")))
    fake = SimpleNamespace(messages=FakeMessages([FRAME, PLAN_OK]))
    monkeypatch.setattr(graph, "RunLogger", lambda topic, mode: RunLogger(topic, mode, runs_dir=tmp_path))
    monkeypatch.setattr(graph, "LLM", lambda settings, log: LLM(settings, log, client=fake))
    state, log = graph.run_graph("t", s, until="plan")
    assert state.plan is not None and state.brief is None
    cost = json.loads((log.dir / "cost.json").read_text())
    assert cost["status"] == "partial:plan" and cost["llm_calls"] == 2
    kinds = [json.loads(l)["kind"] for l in (log.dir / "events.jsonl").read_text().splitlines()]
    assert kinds.count("node_start") == 2 and kinds.count("node_end") == 2
