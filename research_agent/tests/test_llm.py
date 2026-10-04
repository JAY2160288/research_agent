"""llm.py 단위 테스트 — 실제 API 없이 클라이언트를 모킹.

검증하는 것: (1) 정상 파싱, (2) 검증 실패 → 오류 되먹임 재시도 → 성공, (3) 비용 집계와 상한.
"""

from types import SimpleNamespace

import pytest

from research_agent.config import Settings, LLMConfig, Price, Limits
from research_agent.llm import LLM, CostLimitExceeded, LLMError
from research_agent.runlog import RunLogger
from research_agent.schemas import TopicFrame


def _settings(**over):
    base = dict(
        llm=LLMConfig(model="m", judge_model="j", max_retries=2),
        pricing={"default": Price(input=3.0, output=15.0)},
        limits=Limits(max_cost_usd=1.0, max_minutes=10),
    )
    base.update(over)
    return Settings(**base)


GOOD = {
    "original_topic": "t", "topic_en": "t", "domain": "education",
    "concepts": ["a", "b", "c"],
    "variables": {"independent": ["x"], "dependent": ["y"], "population": "grad students"},
    "synonyms_en": ["s1", "s2", "s3"],
    "research_question": "Does x affect y?",
}


class FakeMessages:
    """messages.parse 를 흉내. 응답 큐에서 차례로 꺼낸다."""

    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = []

    def parse(self, **kw):
        self.calls.append(kw)
        out = self.outputs.pop(0)
        block = SimpleNamespace(type="text", text="{...}", parsed_output=out)
        return SimpleNamespace(content=[block], usage=SimpleNamespace(input_tokens=1000, output_tokens=500),
                               stop_reason="end_turn")


def _client(outputs):
    return SimpleNamespace(messages=FakeMessages(outputs))


def test_parse_ok(tmp_path):
    log = RunLogger("t", "test", runs_dir=tmp_path)
    llm = LLM(_settings(), log, client=_client([GOOD]))
    tf = llm.call(role="understand", system="s", user="u", schema=TopicFrame)
    assert isinstance(tf, TopicFrame) and tf.domain == "education"
    assert log.llm_calls == 1
    assert log.cost_usd == pytest.approx((1000 * 3 + 500 * 15) / 1e6)


def test_retry_then_ok(tmp_path):
    bad = dict(GOOD, concepts="not-a-list")  # 검증 실패 유도
    log = RunLogger("t", "test", runs_dir=tmp_path)
    client = _client([bad, GOOD])
    llm = LLM(_settings(), log, client=client)
    tf = llm.call(role="understand", system="s", user="u", schema=TopicFrame)
    assert tf.concepts == ["a", "b", "c"]
    assert len(client.messages.calls) == 2
    # 두 번째 호출에 오류 되먹임이 포함됐는지
    msgs = client.messages.calls[1]["messages"]
    assert any("rejected" in m["content"] for m in msgs if m["role"] == "user")
    assert log.llm_calls == 2


def test_gives_up_after_retries(tmp_path):
    bad = dict(GOOD, concepts="x")
    llm = LLM(_settings(), RunLogger("t", "test", runs_dir=tmp_path), client=_client([bad, bad, bad]))
    with pytest.raises(LLMError):
        llm.call(role="understand", system="s", user="u", schema=TopicFrame)


def test_cost_limit(tmp_path):
    s = _settings(limits=Limits(max_cost_usd=0.001, max_minutes=10))
    log = RunLogger("t", "test", runs_dir=tmp_path)
    llm = LLM(s, log, client=_client([GOOD, GOOD]))
    llm.call(role="a", system="s", user="u", schema=TopicFrame)  # 첫 호출로 상한 초과
    with pytest.raises(CostLimitExceeded):
        llm.call(role="b", system="s", user="u", schema=TopicFrame)
