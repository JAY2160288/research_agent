"""translate.py — brief 산문의 한국어 번역 (ADR-11). LLM 은 가짜.

검증하는 것
- source_items: 리포트 순서대로 id 를 매기고, [auto] 노트와 빈 문자열은 빼며, Top 문헌의 finding 만 포함
- KoreanBrief.check / item_issues: id 누락·중복, 한글 없음, 숫자·DOI 누락, 길이 비율
- apply_translation: 사전에 있는 것만 덧씌우고 원본 brief 는 불변
- translate_run: 검사 실패 → 되먹여 재호출, 끝까지 안 풀린 항목은 영어 유지 + notes, brief.ko.json·translate_events.jsonl 생성,
  report.md 는 한국어본·report.en.md 는 영어 원문, brief.json·cost.json 은 그대로
- rerender_run: brief.ko.json 이 있으면 한국어본을 다시 그린다
"""

import json
from types import SimpleNamespace

import pytest

from research_agent import translate
from research_agent.report import post_checks, rerender_run
from research_agent.schemas import KoreanBrief, KoText

from .test_graph import FakeParse, _settings
from .test_report import _brief, _papers

KO = {
    "rq": "x 는 y 에 영향을 미치는가?",
    # Top 문헌 순서 = 관련성 → 신뢰도 → 연도: p0(4,4) → p2(4,3) → p9(4,3) → p1(4,2)
    "finding:10.1/p0": "결과 f", "finding:10.1/p2": "결과 f", "finding:arxiv:0009.00001": "결과 f",
    "finding:10.1/p1": "파이프 | 와 개행이 있는 결과", "strategy": "전략 s",
    "subrq:rq1": "질문 1", "subrq:rq2": "질문 2", "subrq:rq3": "질문 3",
    "consensus:0": "합의 c1", "conflict:0:claim": "쟁점 k", "conflict:0:a": "A 측 a", "conflict:0:b": "B 측 b", "conflict:0:hyp": "가설 h",
    "coverage": "커버리지 cov", "gap:0:desc": "공백 g1", "gap:0:rq": "제안 rq?", "gap:0:method": "RCT 설계", "gap:0:data": "n=100 자료",
    "limit:0": "사람이 쓴 한계",
}


def _items(ko: dict[str, str]) -> dict:
    return {"items": [KoText(id=k, ko=v).model_dump() for k, v in ko.items()]}


def _run_dir(tmp_path):
    d = tmp_path / "20260101T000000Z_graph_x"
    d.mkdir()
    b, ps = _brief(), _papers()
    (d / "brief.json").write_text(b.model_dump_json(), encoding="utf-8")
    (d / "papers.json").write_text(json.dumps({k: v.model_dump() for k, v in ps.items()}), encoding="utf-8")
    (d / "cost.json").write_text(json.dumps({"checks": post_checks(b, ps), "cost_usd": 0.5}), encoding="utf-8")
    (d / "report.md").write_text("OLD", encoding="utf-8")
    return d


# ---- source_items / apply ----------------------------------------------------------------

def test_source_items_ids_in_report_order_and_exclusions():
    src = translate.source_items(_brief(), _papers())
    assert list(src) == list(KO)                                  # 리포트 순서, [auto] 한계·미배정 문헌(p3) 제외
    assert src["limit:0"] == "human limitation" and "limit:1" not in src
    assert src["finding:10.1/p1"] == "has | pipe\nand newline"


def test_apply_translation_overlays_and_keeps_original():
    b = _brief()
    out = translate.apply_translation(b, {"rq": "질문", "gap:0:rq": "제안", "limit:0": "한계"})
    assert out.topic_frame.research_question == "질문" and out.gaps.gaps[0].proposed_rq == "제안"
    assert out.limitations == ["한계", "[auto] critic: rq3 thin"]        # [auto] 는 그대로
    assert out.gaps.gaps[0].method == "RCT"                                   # 사전에 없으면 영어 유지
    assert b.topic_frame.research_question == "Does x affect y?"             # 원본 불변


# ---- checks ----------------------------------------------------------------------------

def test_korean_brief_checks():
    src = {"a": "Only one survey (n=32, 10.1007/x-1) over 10 weeks reports 17–33% rates.", "b": "short",
           "c": "Another sentence here that is long enough to trigger the ratio check."}
    good = KoreanBrief(items=[KoText(id="a", ko="단 하나의 설문(n=32, 10.1007/x-1)만이 10주에 걸쳐 17~33% 비율을 보고한다."),
                              KoText(id="b", ko="짧음"), KoText(id="c", ko="길이 비율 검사를 건드릴 만큼 긴 또 다른 문장이다.")])
    assert good.check(src) == [] and set(good.accepted(src)) == {"a", "b", "c"}
    bad = KoreanBrief(items=[KoText(id="a", ko="한 설문만 보고한다."),                 # 숫자·DOI 누락 + 너무 짧음
                             KoText(id="b", ko="no hangul"), KoText(id="b", ko="중복"),   # 한글 없음, 중복
                             KoText(id="z", ko="모르는 id")])                           # c 누락, z 는 unknown
    issues = bad.check(src)
    assert any(i.startswith("missing ids ['c']") for i in issues) and any("unknown ids ['z']" in i for i in issues)
    assert any("duplicated ids ['b']" in i for i in issues)
    assert any(i.startswith("a: numbers missing") and "10.1007" in i and "too short" in i for i in issues)
    assert any(i.startswith("b: no Korean") for i in issues)
    assert bad.accepted(src) == {}
    long = KoreanBrief(items=[KoText(id="c", ko="길이 비율 검사를 건드릴 만큼 긴 또 다른 문장이다. " * 6)])
    assert any("too long" in i for i in long.check({"c": src["c"]}))


# ---- translate_run ---------------------------------------------------------------------------

def _client(tmp_path, outputs):
    return _settings(tmp_path), SimpleNamespace(messages=FakeParse(outputs))


def test_translate_run_writes_ko_json_and_korean_report(tmp_path):
    d = _run_dir(tmp_path)
    before = {f: (d / f).read_text(encoding="utf-8") for f in ("brief.json", "cost.json")}
    s, client = _client(tmp_path, [_items(KO)])
    out = translate.translate_run(d, s, client=client)
    assert out["llm_calls"] == 1 and out["fallback_en"] == [] and out["notes"] == [] and out["source_items"] == len(KO)
    assert out["model"] == "claude-sonnet-5-5"                                      # settings.llm.translate_model 기본
    ko = json.loads((d / "brief.ko.json").read_text(encoding="utf-8"))
    assert ko["items"]["gap:0:rq"] == "제안 rq?"
    md = (d / "report.md").read_text(encoding="utf-8")
    assert "> RQ — x 는 y 에 영향을 미치는가?" in md and "report.en.md" in md         # 한국어본 + 배너
    assert "- 합의 c1 [1, 4]" in md and "### G1. 공백 g1" in md and "| 1 | 제안 rq? | RCT 설계 | n=100 자료 | G1 [1, 2] |" in md
    assert "| [1] | P0 (2024) | 결과 f |" in md                                        # Top 문헌 finding 도 한국어
    assert "- 사람이 쓴 한계" in md and "- Critic 미해결 — rq3 thin" in md             # [auto] 는 영어 그대로
    en = (d / "report.en.md").read_text(encoding="utf-8")
    assert "> RQ — Does x affect y?" in en and "report.en.md" not in en
    assert (d / "report_v1.md").read_text(encoding="utf-8") == "OLD"
    assert (d / "translate_events.jsonl").exists() and not (d / "events.jsonl").exists()
    for f, txt in before.items():
        assert (d / f).read_text(encoding="utf-8") == txt                            # brief.json·cost.json 불변
    call = client.messages.calls[0]
    assert call["model"] == "claude-sonnet-5-5" and '"id": "gap:0:desc"' in call["messages"][0]["content"]


def test_translate_run_feeds_back_then_falls_back_to_english(tmp_path):
    d = _run_dir(tmp_path)
    bad1 = dict(KO, **{"gap:0:data": "자료"})                       # n=100 의 100 누락 → 검사 실패
    bad1.pop("limit:0")                                              # id 누락
    bad2 = dict(KO, **{"gap:0:data": "자료"})                       # 두 번째도 숫자 누락 (id 는 채움)
    s, client = _client(tmp_path, [_items(bad1), _items(bad2), _items(bad2)])
    out = translate.translate_run(d, s, client=client)
    assert out["llm_calls"] == 3 and out["fallback_en"] == ["gap:0:data"]
    assert out["notes"] == ["1 item(s) kept in English after checks failed: ['gap:0:data']"]
    second = client.messages.calls[1]["messages"][0]["content"]
    assert "failed these checks" in second and "missing ids ['limit:0']" in second and "gap:0:data: numbers missing" in second
    md = (d / "report.md").read_text(encoding="utf-8")
    assert "- 데이터: n=100" in md and "- 데이터: 자료" not in md     # 실패 항목은 영어 원문


def test_translate_run_refuses_unfinished_and_rerender_uses_ko(tmp_path):
    d = tmp_path / "20260101T000000Z_graph_y"
    d.mkdir()
    with pytest.raises(ValueError, match="brief.json"):
        translate.translate_run(d, _settings(tmp_path), client=SimpleNamespace())
    d2 = _run_dir(tmp_path)
    assert rerender_run(d2)["lang"] == "en" and not (d2 / "report.en.md").exists()
    (d2 / "brief.ko.json").write_text(json.dumps({"items": {"rq": "질문"}}), encoding="utf-8")
    r = rerender_run(d2)
    assert r["lang"] == "ko" and "> RQ — 질문" in (d2 / "report.md").read_text(encoding="utf-8")
    assert "> RQ — Does x affect y?" in (d2 / "report.en.md").read_text(encoding="utf-8")
