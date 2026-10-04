"""arXiv API 검색. 키 불필요. https://info.arxiv.org/help/api/

CS·물리·통계 성격의 주제를 보강한다. arXiv id 자체가 실존 근거 → verified=True.
DOI 가 있으면 id 를 DOI 로 통일해 OpenAlex 결과와 중복 제거가 되게 한다.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import httpx

from ..schemas import Paper

BASE = "https://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def _parse(xml_text: str, sub_rq_id: str | None) -> list[Paper]:
    root = ET.fromstring(xml_text)
    out = []
    for e in root.findall("a:entry", NS):
        raw_id = (e.findtext("a:id", default="", namespaces=NS) or "").strip()
        m = re.search(r"abs/([^v]+)(v\d+)?$", raw_id)
        if not m:
            continue
        aid = m.group(1)
        doi_el = e.find("arxiv:doi", NS)
        doi = doi_el.text.strip().lower() if doi_el is not None and doi_el.text else None
        year_txt = e.findtext("a:published", default="", namespaces=NS)
        year = int(year_txt[:4]) if year_txt[:4].isdigit() else None
        out.append(Paper(
            id=doi or f"arxiv:{aid}",
            title=re.sub(r"\s+", " ", e.findtext("a:title", default="", namespaces=NS)).strip(),
            year=year,
            authors=[a.findtext("a:name", default="", namespaces=NS) for a in e.findall("a:author", NS)][:8],
            venue="arXiv",
            abstract=re.sub(r"\s+", " ", e.findtext("a:summary", default="", namespaces=NS)).strip() or None,
            doi=doi,
            arxiv_id=aid,
            url=f"https://arxiv.org/abs/{aid}",
            source="arxiv",
            sub_rq_ids=[sub_rq_id] if sub_rq_id else [],
            verified=True,
        ))
    return out


def search(query: str, *, max_results: int = 10, user_agent: str = "research-agent",
           sub_rq_id: str | None = None, client: httpx.Client | None = None) -> list[Paper]:
    params = {"search_query": f"all:{query}", "start": 0, "max_results": max_results,
              "sortBy": "relevance", "sortOrder": "descending"}
    c = client or httpx.Client(timeout=30, headers={"User-Agent": user_agent})
    r = c.get(BASE, params=params)
    r.raise_for_status()
    return _parse(r.text, sub_rq_id)
