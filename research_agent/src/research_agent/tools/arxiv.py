"""arXiv API 검색. 키 불필요. https://info.arxiv.org/help/api/

CS·물리·통계 성격의 주제를 보강한다. arXiv id 자체가 실존 근거 → verified=True.
DOI 가 있으면 id 를 DOI 로 통일해 OpenAlex 결과와 중복 제거가 되게 한다.
"""

from __future__ import annotations

import re
import time
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


def _retry_after(r: httpx.Response, default: float, cap: float = 30.0) -> float:
    """429·503 의 Retry-After(초) 를 존중하되 cap 초를 넘기지 않는다. 없거나 날짜 형식이면 default."""
    v = r.headers.get("retry-after")
    try:
        return min(float(v), cap) if v is not None else default
    except ValueError:
        return default


def search(query: str, *, max_results: int = 10, user_agent: str = "research-agent",
           sub_rq_id: str | None = None, client: httpx.Client | None = None,
           timeout: float = 30.0, retry_wait: float = 5.0, max_attempts: int = 3,
           deadline: float | None = None) -> list[Paper]:
    """arXiv 는 공식적으로 3초에 1요청이고, export.arxiv.org 는 부하 시 수십 초씩 늦거나 429·503 을 돌려준다
    (2026-10-04 T1 16회 전부 실패, 2026-10-30 세 라운드 모두 타임아웃→429 로 차단. ADR-15).
    - 타임아웃·연결 오류·429·5xx 는 max_attempts 회까지 재시도. 대기는 Retry-After(최대 30초) 또는 retry_wait × 시도 횟수.
    - deadline(time.monotonic 기준) 을 주면 남은 시간 안에서만 요청·대기한다 — search 노드의 라운드당 arXiv 시간 예산.
      예산이 끝나면 TimeoutError 를 던지고, 호출자(search 노드)가 circuit breaker 로 처리한다.
    """
    params = {"search_query": f"all:{query}", "start": 0, "max_results": max_results,
              "sortBy": "relevance", "sortOrder": "descending"}
    c = client or httpx.Client(timeout=timeout, headers={"User-Agent": user_agent})
    for attempt in range(1, max_attempts + 1):
        remaining = None if deadline is None else deadline - time.monotonic()
        if remaining is not None and remaining <= 1.0:
            raise TimeoutError(f"arXiv time budget exhausted before attempt {attempt}")
        per_call = timeout if remaining is None else min(timeout, remaining)   # 남은 예산보다 길게 기다리지 않는다
        last = attempt == max_attempts
        try:
            r = c.get(BASE, params=params, timeout=per_call)
            if r.status_code == 429 or r.status_code >= 500:   # 속도 제한·서버 과부하 → 재시도 대상
                if last:
                    r.raise_for_status()
                wait = _retry_after(r, retry_wait * attempt)
            else:
                r.raise_for_status()                           # 4xx(쿼리 오류 등)는 재시도해도 같으므로 바로 실패
                return _parse(r.text, sub_rq_id)
        except (httpx.TimeoutException, httpx.TransportError):
            if last:
                raise
            wait = retry_wait * attempt
        if deadline is not None and time.monotonic() + wait >= deadline - 1.0:
            raise TimeoutError(f"arXiv time budget exhausted after {attempt} attempt(s)")
        time.sleep(wait)
    return []  # unreachable
