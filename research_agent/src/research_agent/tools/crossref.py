"""Crossref — DOI 실존 검증 전용. 키 불필요. https://api.crossref.org

LLM 이 인용한 DOI 가 실제로 존재하는지(환각 차단, goals.md O2) 확인한다.
OpenAlex/arXiv 에서 온 문헌은 이미 verified 지만, 베이스라인 ReAct 가 자유롭게 적은 DOI 나
사용자가 추가한 DOI 는 이 함수를 통과해야 한다.
"""

from __future__ import annotations

import httpx

BASE = "https://api.crossref.org/works"


def verify_doi(doi: str, *, mailto: str | None = None, user_agent: str = "research-agent",
               client: httpx.Client | None = None) -> dict | None:
    """존재하면 {'doi','title','year'} 반환, 없으면 None."""
    doi = doi.lower().strip().replace("https://doi.org/", "")
    ua = f"{user_agent} (mailto:{mailto})" if mailto else user_agent
    c = client or httpx.Client(timeout=30, headers={"User-Agent": ua})
    r = c.get(f"{BASE}/{doi}")
    if r.status_code == 404:
        return None
    r.raise_for_status()
    m = r.json().get("message", {})
    date = (m.get("published-print") or m.get("published-online") or m.get("created") or {}).get("date-parts", [[None]])
    return {"doi": doi, "title": (m.get("title") or [""])[0], "year": date[0][0] if date and date[0] else None}
