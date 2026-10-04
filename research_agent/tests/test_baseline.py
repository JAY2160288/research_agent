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
