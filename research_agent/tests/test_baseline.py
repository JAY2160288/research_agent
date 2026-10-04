"""베이스라인 ReAct 루프 제어 흐름 테스트 — 가짜 클라이언트로 '검색 → 제출' 2턴을 재현."""

from types import SimpleNamespace

from research_agent import baseline
from research_agent.config import Settings, LLMConfig, Price, Limits, ToolsConfig
from research_agent.tools import openalex
from research_agent.schemas import Paper

PAPER = Paper(id="10.1000/abc", title="T", year=2024, abstract="We study LLMs", doi="10.1000/abc",
              source="openalex", verified=True)

BRIEF = {
    "topic_frame": {"original_topic": "t", "topic_en": "t", "domain": "education", "concepts": ["a", "b", "c"],
                    "variables": {"independent": ["x"], "dependent": ["y"], "population": "p"},
                    "synonyms_en": ["s1", "s2", "s3"], "research_question": "q"},
    "plan": {"sub_rqs": [{"id": f"rq{i}", "question": "q", "rationale": "r", "queries": ["a", "b"]} for i in (1, 2, 3)],
             "search_strategy": "s"},
    "evidence": {"items": [{"paper_id": "10.1000/abc", "relevance": 4, "reliability": 3, "method": "survey",
                            "finding": "f", "sub_rq_ids": ["rq1"]}]},
    "synthesis": {"consensus": [{"statement": "c", "evidence_ids": ["10.1000/abc"]}],
                  "conflicts": [], "conditional": [], "coverage_note": "n"},
    "gaps": {"gaps": [{"description": "g", "evidence_ids": ["10.1000/abc", "10.1000/ghost"],
                       "proposed_rq": "q", "method": "m", "data": "d"}]},
    "limitations": ["l"], "executive_summary": "요약",
}


class FakeMessages:
    def __init__(self):
        self.turn = 0

    def create(self, **kw):
        self.turn += 1
        if self.turn == 1:
            content = [SimpleNamespace(type="text", text="searching"),
                       SimpleNamespace(type="tool_use", id="tu1", name="search_openalex", input={"query": "x"})]
        else:
            content = [SimpleNamespace(type="tool_use", id="tu2", name="submit_brief", input=BRIEF)]
        return SimpleNamespace(content=content, usage=SimpleNamespace(input_tokens=10, output_tokens=5), stop_reason="tool_use")


def test_baseline_flow(tmp_path, monkeypatch):
    monkeypatch.setattr(openalex, "search", lambda q, **kw: [PAPER.model_copy()])
    monkeypatch.setattr(baseline, "RunLogger", lambda topic, mode: __import__("research_agent.runlog", fromlist=["RunLogger"]).RunLogger(topic, mode, runs_dir=tmp_path))
    s = Settings(llm=LLMConfig(model="m", judge_model="j"), pricing={"default": Price(input=1, output=1)},
                 limits=Limits(max_react_steps=5), tools=ToolsConfig(cache_dir=str(tmp_path / "c")))
    fake = SimpleNamespace(messages=FakeMessages())
    monkeypatch.setattr(baseline, "LLM", lambda settings, log: __import__("research_agent.llm", fromlist=["LLM"]).LLM(settings, log, client=fake))

    brief, log = baseline.run_baseline("topic", s)
    assert brief is not None and log.llm_calls == 2
    assert (log.dir / "report.md").exists() and (log.dir / "cost.json").exists()
    import json
    cost = json.loads((log.dir / "cost.json").read_text())
    ck = cost["checks"]
    assert ck["citations_total"] == 2 and ck["citations_verified"] == 1
    assert ck["unknown_ids"] == ["10.1000/ghost"]  # 환각 인용이 잡히는지
    assert "## 5. Research Gap" in (log.dir / "report.md").read_text()


class TruncatingMessages:
    """1턴: max_tokens 로 잘린 submit_brief (불완전 input) → 2턴: 정상 제출."""

    def __init__(self):
        self.turn = 0
        self.calls = []

    def create(self, **kw):
        self.calls.append(kw)
        self.turn += 1
        if self.turn == 1:
            partial = {"executive_summary": "cut"}  # 뒤쪽 필드가 잘려 나간 상태
            return SimpleNamespace(content=[SimpleNamespace(type="tool_use", id="tu1", name="submit_brief", input=partial)],
                                   usage=SimpleNamespace(input_tokens=10, output_tokens=8192), stop_reason="max_tokens")
        return SimpleNamespace(content=[SimpleNamespace(type="tool_use", id="tu2", name="submit_brief", input=BRIEF)],
                               usage=SimpleNamespace(input_tokens=10, output_tokens=5), stop_reason="tool_use")


def test_truncated_output_gets_compress_feedback(tmp_path, monkeypatch):
    monkeypatch.setattr(baseline, "RunLogger", lambda topic, mode: __import__("research_agent.runlog", fromlist=["RunLogger"]).RunLogger(topic, mode, runs_dir=tmp_path))
    s = Settings(llm=LLMConfig(model="m", judge_model="j"), pricing={"default": Price(input=1, output=1)},
                 limits=Limits(max_react_steps=5), tools=ToolsConfig(cache_dir=str(tmp_path / "c")))
    fake = SimpleNamespace(messages=TruncatingMessages())
    monkeypatch.setattr(baseline, "LLM", lambda settings, log: __import__("research_agent.llm", fromlist=["LLM"]).LLM(settings, log, client=fake))

    brief, log = baseline.run_baseline("topic", s)
    assert brief is not None and log.llm_calls == 2
    # 2번째 요청의 직전 user 메시지에 '잘림' 피드백이 is_error 로 들어갔는지 (schema error 가 아니라)
    # (fake 는 messages 리스트 참조를 저장하므로 최종 상태를 본다) 잘린 tu1 에 대한 tool_result 를 찾는다
    msgs = fake.messages.calls[1]["messages"]
    users = [m for m in msgs if m["role"] == "user"]
    fb = next(b for m in users if isinstance(m["content"], list) for b in m["content"]
              if isinstance(b, dict) and b.get("tool_use_id") == "tu1")
    assert fb["is_error"] and "cut off" in fb["content"]
    # 프롬프트 캐시 마커: system 블록에 cache_control, user 메시지 중 마지막으로 전송된 것 하나에만 cache_control
    assert fake.messages.calls[1]["system"][0]["cache_control"] == {"type": "ephemeral"}
    marked = [b for m in users if isinstance(m["content"], list) for b in m["content"]
              if isinstance(b, dict) and "cache_control" in b]
    assert len(marked) == 1 and marked[0] is fb  # 2번째 요청 시점의 마지막 user 블록 = 잘림 피드백


def test_limit_exceeded_finishes_gracefully(tmp_path, monkeypatch):
    monkeypatch.setattr(baseline, "RunLogger", lambda topic, mode: __import__("research_agent.runlog", fromlist=["RunLogger"]).RunLogger(topic, mode, runs_dir=tmp_path))
    s = Settings(llm=LLMConfig(model="m", judge_model="j"), pricing={"default": Price(input=1e6, output=1e6)},  # 1토큰 = $1
                 limits=Limits(max_react_steps=5, max_cost_usd=0.5), tools=ToolsConfig(cache_dir=str(tmp_path / "c")))
    fake = SimpleNamespace(messages=FakeMessages())
    monkeypatch.setattr(baseline, "LLM", lambda settings, log: __import__("research_agent.llm", fromlist=["LLM"]).LLM(settings, log, client=fake))
    monkeypatch.setattr(openalex, "search", lambda q, **kw: [PAPER.model_copy()])

    brief, log = baseline.run_baseline("topic", s)  # 1턴 후 비용 상한 초과 → 예외 없이 종료
    import json
    cost = json.loads((log.dir / "cost.json").read_text())
    assert brief is None and cost["status"] == "limit_exceeded"


def test_submit_unwraps_brief_wrapper():
    """Haiku 가 {'brief': {...}} 로 감싸서 제출한 경우 래퍼를 벗겨 검증한다 (T2 실행에서 2회 거절 관찰)."""
    assert baseline._unwrap_submit({"brief": BRIEF}) == BRIEF
    assert baseline._unwrap_submit(BRIEF) == BRIEF
    assert baseline._unwrap_submit({"brief": "not a dict"}) == {"brief": "not a dict"}
