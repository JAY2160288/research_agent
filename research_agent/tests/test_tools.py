"""학술 도구 단위 테스트 — HTTP 를 모킹한 녹화 응답으로 파싱·정규화·캐시·중복 제거를 검증.
실제 네트워크 확인은 scripts/smoke_tools.py (맥에서 실행).
"""

import httpx
import pytest

from research_agent.config import Settings, LLMConfig, Price, ToolsConfig
from research_agent.tools import Tools, arxiv, crossref, openalex

OPENALEX_JSON = {
    "results": [
        {
            "id": "https://openalex.org/W1", "doi": "https://doi.org/10.1000/ABC",
            "display_name": "Generative AI and graduate research productivity", "publication_year": 2024,
            "authorships": [{"author": {"display_name": "A. Kim"}}],
            "primary_location": {"source": {"display_name": "Computers & Education"}, "landing_page_url": "x"},
            "abstract_inverted_index": {"We": [0], "study": [1], "LLMs": [2]},
            "cited_by_count": 12, "type": "article",
        },
        {"id": "https://openalex.org/W2", "doi": None, "display_name": "No DOI paper", "publication_year": 2020},
    ]
}

ARXIV_XML = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2401.00001v2</id>
    <title>Memory  for LLM
     Agents</title>
    <summary>We propose a memory module.</summary>
    <published>2024-01-01T00:00:00Z</published>
    <author><name>B. Lee</name></author>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2305.12345v1</id>
    <title>Paper with DOI</title>
    <summary>s</summary>
    <published>2023-05-01T00:00:00Z</published>
    <arxiv:doi>10.1000/ABC</arxiv:doi>
  </entry>
</feed>"""


def test_openalex_parse_and_abstract():
    c = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200, json=OPENALEX_JSON)))
    ps = openalex.search("x", client=c)
    assert len(ps) == 1  # DOI 없는 문헌 제외
    assert ps[0].id == "10.1000/abc" and ps[0].abstract == "We study LLMs" and ps[0].verified


def test_arxiv_parse_and_doi_unification():
    c = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200, text=ARXIV_XML)))
    ps = arxiv.search("x", client=c)
    assert ps[0].id == "arxiv:2401.00001" and ps[0].title == "Memory for LLM Agents" and ps[0].year == 2024
    assert ps[1].id == "10.1000/abc"  # DOI 가 있으면 id 를 DOI 로


def test_crossref_verify():
    def handler(r):
        if r.url.path.endswith("10.1000/abc"):
            return httpx.Response(200, json={"message": {"title": ["T"], "published-print": {"date-parts": [[2024, 1]]}}})
        return httpx.Response(404)
    c = httpx.Client(transport=httpx.MockTransport(handler))
    assert crossref.verify_doi("https://doi.org/10.1000/ABC", client=c) == {"doi": "10.1000/abc", "title": "T", "year": 2024}
    assert crossref.verify_doi("10.9999/nope", client=c) is None


def _settings(tmp_path):
    return Settings(llm=LLMConfig(model="m", judge_model="j"), pricing={"default": Price(input=1, output=1)},
                    tools=ToolsConfig(cache_dir=str(tmp_path / "cache")))


def test_registry_dedup_and_cache(tmp_path, monkeypatch):
    calls = {"n": 0}
    real_search = openalex.search

    def fake_search(query, **kw):
        calls["n"] += 1
        c = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200, json=OPENALEX_JSON)))
        return real_search(query, client=c)

    monkeypatch.setattr(openalex, "search", fake_search)
    t = Tools(_settings(tmp_path), use_cache=True)
    a = t.search_openalex("q", sub_rq_id="rq1")
    b = t.search_openalex("q", sub_rq_id="rq2")  # 캐시 적중, 같은 문헌에 sub_rq 누적
    assert calls["n"] == 1
    assert a[0] is b[0] and t.papers["10.1000/abc"].sub_rq_ids == ["rq1", "rq2"]


def test_dispatch_format(tmp_path, monkeypatch):
    monkeypatch.setattr(crossref, "verify_doi", lambda doi, **kw: None)
    t = Tools(_settings(tmp_path), use_cache=False)
    assert "NOT FOUND" in t.dispatch("verify_doi", {"doi": "10.1/x"})
