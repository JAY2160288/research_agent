"""OpenAlex 검색. 키 불필요. https://docs.openalex.org/

- `mailto` 에 연락 이메일을 넣으면 polite pool (더 높은 rate limit). 키가 아니라 연락처다.
- 초록은 inverted index 로 오므로 복원한다.
- DOI 가 있는 문헌은 OpenAlex 자체가 실존 근거이므로 verified=True. (Crossref 로 2차 확인은 crossref.py)
"""

from __future__ import annotations

import httpx

from ..schemas import Paper

BASE = "https://api.openalex.org/works"


def _reconstruct_abstract(inv: dict[str, list[int]] | None) -> str | None:
    if not inv:
        return None
    pos: dict[int, str] = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos)) or None


def _to_paper(w: dict, sub_rq_id: str | None) -> Paper | None:
    doi = (w.get("doi") or "").lower().replace("https://doi.org/", "") or None
    if not doi:
        return None  # DOI 없는 문헌은 검증 불가 → 제외 (goals.md O2)
    loc = w.get("primary_location") or {}
    src = loc.get("source") or {}
    return Paper(
        id=doi,
        title=w.get("display_name") or w.get("title") or "",
        year=w.get("publication_year"),
        authors=[a.get("author", {}).get("display_name", "") for a in (w.get("authorships") or [])[:8]],
        venue=src.get("display_name"),
        abstract=_reconstruct_abstract(w.get("abstract_inverted_index")),
        doi=doi,
        url=w.get("doi") or loc.get("landing_page_url"),
        cited_by_count=w.get("cited_by_count"),
        source="openalex",
        sub_rq_ids=[sub_rq_id] if sub_rq_id else [],
        verified=True,
    )


def search(query: str, *, per_page: int = 15, mailto: str | None = None, user_agent: str = "research-agent",
           from_year: int | None = None, sub_rq_id: str | None = None, client: httpx.Client | None = None) -> list[Paper]:
    params = {
        "search": query,
        "per-page": per_page,
        "select": "id,doi,display_name,publication_year,authorships,primary_location,"
                  "abstract_inverted_index,cited_by_count,type",
        "filter": "type:article|review|preprint|book-chapter" + (f",from_publication_date:{from_year}-01-01" if from_year else ""),
        "sort": "relevance_score:desc",
    }
    if mailto:
        params["mailto"] = mailto
    c = client or httpx.Client(timeout=30, headers={"User-Agent": user_agent})
    r = c.get(BASE, params=params)
    r.raise_for_status()
    out = []
    for w in r.json().get("results", []):
        p = _to_paper(w, sub_rq_id)
        if p:
            out.append(p)
    return out


def get_by_doi(doi: str, *, mailto: str | None = None, client: httpx.Client | None = None) -> Paper | None:
    c = client or httpx.Client(timeout=30)
    params = {"mailto": mailto} if mailto else {}
    r = c.get(f"{BASE}/https://doi.org/{doi}", params=params)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return _to_paper(r.json(), None)
