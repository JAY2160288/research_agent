"""Crossref — DOI 실존 검증 + OpenAlex 폴백 검색. 키 불필요. https://api.crossref.org

- `verify_doi`: LLM 이 인용한 DOI 가 실제로 존재하는지(환각 차단, goals.md O2) 확인한다.
  OpenAlex/arXiv 에서 온 문헌은 이미 verified 지만, 베이스라인 ReAct 가 자유롭게 적은 DOI 는 이 함수를 통과해야 한다.
- `search`: works 검색 (`query.bibliographic`). OpenAlex 가 429(일일 크레딧 소진) 등으로 막혔을 때 search 노드가 쓰는 폴백
  (plan.md ADR-8). Crossref 는 DOI 등록기관이므로 결과는 그 자체로 실존 검증됨(verified=True). 초록은 일부 문헌에만 있고
  JATS XML 로 오므로 태그를 벗긴다. polite pool 은 User-Agent 의 mailto 로 들어간다.
"""

from __future__ import annotations

import re

import httpx

from ..schemas import Paper

BASE = "https://api.crossref.org/works"
_TYPES = "type:journal-article,type:proceedings-article,type:posted-content,type:book-chapter"


def _ua(user_agent: str, mailto: str | None) -> str:
    return f"{user_agent} (mailto:{mailto})" if mailto else user_agent


def verify_doi(doi: str, *, mailto: str | None = None, user_agent: str = "research-agent",
               client: httpx.Client | None = None) -> dict | None:
    """존재하면 {'doi','title','year'} 반환, 없으면 None."""
    doi = doi.lower().strip().replace("https://doi.org/", "")
    c = client or httpx.Client(timeout=30, headers={"User-Agent": _ua(user_agent, mailto)})
    r = c.get(f"{BASE}/{doi}")
    if r.status_code == 404:
        return None
    r.raise_for_status()
    m = r.json().get("message", {})
    date = (m.get("published-print") or m.get("published-online") or m.get("created") or {}).get("date-parts", [[None]])
    return {"doi": doi, "title": (m.get("title") or [""])[0], "year": date[0][0] if date and date[0] else None}


def _strip_jats(text: str | None) -> str | None:
    if not text:
        return None
    out = re.sub(r"<[^>]+>", " ", text)
    out = re.sub(r"\s+", " ", out).strip()
    return out or None


def _year(m: dict) -> int | None:
    for k in ("published", "published-print", "published-online", "issued", "created"):
        parts = (m.get(k) or {}).get("date-parts") or []
        if parts and parts[0] and parts[0][0]:
            return int(parts[0][0])
    return None


def _to_paper(m: dict, sub_rq_id: str | None) -> Paper | None:
    doi = (m.get("DOI") or "").lower().strip()
    title = " ".join((m.get("title") or [""])[0].split())
    if not doi or not title:
        return None
    authors = []
    for a in (m.get("author") or [])[:8]:
        name = " ".join(x for x in (a.get("given"), a.get("family")) if x) or a.get("name") or ""
        if name:
            authors.append(name)
    return Paper(
        id=doi, title=title, year=_year(m), authors=authors,
        venue=(m.get("container-title") or [None])[0],
        abstract=_strip_jats(m.get("abstract")),
        doi=doi, url=f"https://doi.org/{doi}",
        cited_by_count=m.get("is-referenced-by-count"),
        source="crossref", sub_rq_ids=[sub_rq_id] if sub_rq_id else [], verified=True,
    )


def search(query: str, *, rows: int = 15, mailto: str | None = None, user_agent: str = "research-agent",
           from_year: int | None = None, sub_rq_id: str | None = None, client: httpx.Client | None = None) -> list[Paper]:
    params = {
        "query.bibliographic": query,
        "rows": rows,
        "select": "DOI,title,abstract,published,author,container-title,is-referenced-by-count,type",
        "filter": _TYPES + (f",from-pub-date:{from_year}-01-01" if from_year else ""),
    }
    if mailto:
        params["mailto"] = mailto
    c = client or httpx.Client(timeout=30, headers={"User-Agent": _ua(user_agent, mailto)})
    r = c.get(BASE, params=params)
    r.raise_for_status()
    out = []
    for m in (r.json().get("message") or {}).get("items", []):
        p = _to_paper(m, sub_rq_id)
        if p:
            out.append(p)
    return out
