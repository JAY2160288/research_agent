"""도구 레지스트리. 캐시·로깅을 붙인 실행 함수와, LLM 에 넘길 tool 정의를 한 곳에서 관리.

tool use 에 노출되는 도구 3개 (키 불필요):
  search_openalex(query, from_year?) → 문헌 목록
  search_arxiv(query)                → 문헌 목록
  verify_doi(doi)                    → 실존 여부
"""

from __future__ import annotations

import threading
from typing import Any

from ..config import Settings
from ..runlog import RunLogger
from ..schemas import Paper
from . import arxiv, crossref, openalex
from .cache import ToolCache

TOOL_DEFS: list[dict[str, Any]] = [
    {
        "name": "search_openalex",
        "description": "Search peer-reviewed literature across all fields via OpenAlex. Returns up to 15 papers "
                       "with DOI, year, venue, abstract. Use English keyword queries.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "English keyword query"},
                "from_year": {"type": "integer", "description": "Only papers published in or after this year"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "search_arxiv",
        "description": "Search arXiv preprints (computer science, statistics, physics). Returns up to 10 papers with abstract.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "English keyword query"}},
            "required": ["query"],
        },
    },
    {
        "name": "verify_doi",
        "description": "Check that a DOI exists in Crossref. Papers returned by search_openalex / search_arxiv are ALREADY "
                       "verified — do not call this on them (it wastes steps). Use it only for a DOI you did not get from a search tool.",
        "input_schema": {
            "type": "object",
            "properties": {"doi": {"type": "string"}},
            "required": ["doi"],
        },
    },
]


def normalize_id(raw: str) -> str:
    """사용자가 준 문헌 id 를 Paper.id 규칙으로: 소문자 DOI(접두 URL 제거) 또는 arxiv:<id>."""
    s = raw.strip().lower()
    for pre in ("https://doi.org/", "http://doi.org/", "doi:", "https://dx.doi.org/"):
        if s.startswith(pre):
            s = s[len(pre):]
    if s.startswith("https://arxiv.org/abs/"):
        s = "arxiv:" + s[len("https://arxiv.org/abs/"):]
    return s


class Tools:
    def __init__(self, settings: Settings, log: RunLogger | None = None, use_cache: bool = True,
                 exclude: list[str] | None = None, include: list[str] | None = None):
        self.s = settings
        self.log = log
        self.cache = ToolCache(settings.tools.cache_dir, enabled=use_cache)
        self.papers: dict[str, Paper] = {}  # 이번 실행에서 본 모든 문헌 (id → Paper)
        self._lock = threading.Lock()       # search 노드가 쿼리를 병렬로 돌리므로 레지스트리 갱신은 직렬화
        # 사용자 개입 (2026-10-08): 제외 문헌은 레지스트리에 들어오지 않아 인용될 수 없고, 고정 문헌은 search 가 DOI 로 가져와
        # 모든 sub-RQ 후보에 넣는다 (evaluate 가 관련성을 매기되 후보 상한과 무관하게 평가됨)
        self.excluded: set[str] = {normalize_id(x) for x in (exclude or []) if x.strip()}
        self.include_ids: list[str] = [normalize_id(x) for x in (include or []) if x.strip()]

    # ---- 개별 도구 ----------------------------------------------------
    def search_openalex(self, query: str, from_year: int | None = None, sub_rq_id: str | None = None) -> list[Paper]:
        args = {"query": query, "from_year": from_year, "per_page": self.s.tools.openalex_per_query}
        raw, cached = self.cache.get_or_call("openalex", args, lambda: [
            p.model_dump() for p in openalex.search(query, per_page=self.s.tools.openalex_per_query,
                                                    mailto=self.s.contact_email, user_agent=self.s.tools.user_agent,
                                                    from_year=from_year, api_key=self.s.tools.openalex_api_key)])
        papers = [Paper(**d) for d in raw]
        return self._register(papers, sub_rq_id, "search_openalex", args, cached)

    def include_paper(self, pid: str, sub_rq_ids: list[str]) -> Paper | None:
        """`--include` 문헌 하나를 OpenAlex(DOI) 에서 가져와 pinned 로 등록. arXiv id 는 OpenAlex 가 DOI 로 색인하므로 DOI 만 받는다."""
        if pid.startswith("arxiv:"):
            if self.log:
                self.log.event("include_skipped", id=pid, reason="give the DOI (OpenAlex indexes arXiv papers by DOI)")
            return None
        args = {"doi": pid}
        raw, cached = self.cache.get_or_call("openalex_doi", args, lambda: (
            lambda p: p.model_dump() if p else None)(openalex.get_by_doi(pid, mailto=self.s.contact_email,
                                                                           api_key=self.s.tools.openalex_api_key)))
        if not raw:
            if self.log:
                self.log.event("include_skipped", id=pid, reason="not found in OpenAlex")
            return None
        p = Paper(**raw)
        p.pinned = True
        p.sub_rq_ids = list(sub_rq_ids)
        out = self._register([p], None, "include_paper", args, cached)
        out[0].pinned = True
        return out[0]

    def search_crossref(self, query: str, from_year: int | None = None, sub_rq_id: str | None = None) -> list[Paper]:
        """OpenAlex 폴백 (plan.md ADR-8). tool use 에는 노출하지 않는다 — search 노드가 OpenAlex 실패 시에만 부른다."""
        args = {"query": query, "from_year": from_year, "rows": self.s.tools.crossref_per_query}
        raw, cached = self.cache.get_or_call("crossref_search", args, lambda: [
            p.model_dump() for p in crossref.search(query, rows=self.s.tools.crossref_per_query, mailto=self.s.contact_email,
                                                    user_agent=self.s.tools.user_agent, from_year=from_year)])
        papers = [Paper(**d) for d in raw]
        return self._register(papers, sub_rq_id, "search_crossref", args, cached)

    def search_arxiv(self, query: str, sub_rq_id: str | None = None) -> list[Paper]:
        args = {"query": query, "max_results": self.s.tools.arxiv_per_query}
        raw, cached = self.cache.get_or_call("arxiv", args, lambda: [
            p.model_dump() for p in arxiv.search(query, max_results=self.s.tools.arxiv_per_query,
                                                 user_agent=self.s.tools.user_agent)])
        papers = [Paper(**d) for d in raw]
        return self._register(papers, sub_rq_id, "search_arxiv", args, cached)

    def verify_doi(self, doi: str) -> dict | None:
        """검색 도구가 이미 검증한 문헌(또는 arxiv id)은 Crossref 를 부르지 않고 즉시 EXISTS.
        (T2·T5 실행에서 모델이 arxiv id 를 Crossref 로 검증하려다 NOT FOUND 를 받고 멀쩡한 문헌을 버림.)"""
        key = doi.lower().strip().replace("https://doi.org/", "")
        args = {"doi": key}
        known = self.papers.get(key)
        if known is not None and known.verified:
            if self.log:
                self.log.tool("verify_doi", args, 1, True)
            return {"doi": key, "title": known.title, "year": known.year, "note": "already verified by search tool"}
        if key.startswith("arxiv:"):
            if self.log:
                self.log.tool("verify_doi", args, 0, True)
            return None  # arXiv id 는 Crossref 대상이 아님. 검색 결과에 없는 arxiv id 는 인용 불가
        res, cached = self.cache.get_or_call("crossref", args, lambda: crossref.verify_doi(
            key, mailto=self.s.contact_email, user_agent=self.s.tools.user_agent))
        if self.log:
            self.log.tool("verify_doi", args, 1 if res else 0, cached)
        if res and key in self.papers:
            self.papers[key].verified = True
        return res

    # ---- tool use 디스패치 (베이스라인 ReAct 용) --------------------------
    def dispatch(self, name: str, inputs: dict[str, Any]) -> str:
        """LLM tool_use 블록 → 실행 → 문자열 결과 (tool_result 에 넣을 내용)."""
        if name == "search_openalex":
            ps = self.search_openalex(inputs["query"], inputs.get("from_year"))
            return _format_papers(ps)
        if name == "search_arxiv":
            ps = self.search_arxiv(inputs["query"])
            return _format_papers(ps)
        if name == "verify_doi":
            r = self.verify_doi(inputs["doi"])
            return f"EXISTS: {r}" if r else "NOT FOUND — do not cite this DOI"
        return f"unknown tool {name}"

    # ---- 내부 ----------------------------------------------------------
    def _register(self, papers: list[Paper], sub_rq_id: str | None, name: str, args: dict, cached: bool) -> list[Paper]:
        with self._lock:
            papers = [p for p in papers if p.id not in self.excluded]   # --exclude: 레지스트리 밖 = 인용 불가
            for p in papers:
                if sub_rq_id and sub_rq_id not in p.sub_rq_ids:
                    p.sub_rq_ids.append(sub_rq_id)
                if p.id in self.papers:
                    ex = self.papers[p.id]
                    ex.sub_rq_ids = sorted(set(ex.sub_rq_ids) | set(p.sub_rq_ids))
                    if not ex.abstract and p.abstract:
                        ex.abstract = p.abstract
                    ex.pinned = ex.pinned or p.pinned
                else:
                    self.papers[p.id] = p
            out = [self.papers[p.id] for p in papers]
        if self.log:
            self.log.tool(name, {k: v for k, v in args.items() if v is not None}, len(papers), cached)
        return out


def _format_papers(ps: list[Paper], abstract_chars: int = 600) -> str:
    if not ps:
        return "no results"
    lines = []
    for p in ps:
        ab = (p.abstract or "")[:abstract_chars]
        lines.append(f"- id: {p.id} | {p.year} | {p.title} | {p.venue or ''} | cited_by={p.cited_by_count}\n  abstract: {ab}")
    return "\n".join(lines)
