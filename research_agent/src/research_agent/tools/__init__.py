"""도구 레지스트리. 캐시·로깅을 붙인 실행 함수와, LLM 에 넘길 tool 정의를 한 곳에서 관리.

tool use 에 노출되는 도구 3개 (키 불필요):
  search_openalex(query, from_year?) → 문헌 목록
  search_arxiv(query)                → 문헌 목록
  verify_doi(doi)                    → 실존 여부
"""

from __future__ import annotations

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
        "description": "Check that a DOI exists in Crossref. Every DOI you cite in the final report must pass this check.",
        "input_schema": {
            "type": "object",
            "properties": {"doi": {"type": "string"}},
            "required": ["doi"],
        },
    },
]


class Tools:
    def __init__(self, settings: Settings, log: RunLogger | None = None, use_cache: bool = True):
        self.s = settings
        self.log = log
        self.cache = ToolCache(settings.tools.cache_dir, enabled=use_cache)
        self.papers: dict[str, Paper] = {}  # 이번 실행에서 본 모든 문헌 (id → Paper)

    # ---- 개별 도구 ----------------------------------------------------
    def search_openalex(self, query: str, from_year: int | None = None, sub_rq_id: str | None = None) -> list[Paper]:
        args = {"query": query, "from_year": from_year, "per_page": self.s.tools.openalex_per_query}
        raw, cached = self.cache.get_or_call("openalex", args, lambda: [
            p.model_dump() for p in openalex.search(query, per_page=self.s.tools.openalex_per_query,
                                                    mailto=self.s.contact_email, user_agent=self.s.tools.user_agent,
                                                    from_year=from_year)])
        papers = [Paper(**d) for d in raw]
        return self._register(papers, sub_rq_id, "search_openalex", args, cached)

    def search_arxiv(self, query: str, sub_rq_id: str | None = None) -> list[Paper]:
        args = {"query": query, "max_results": self.s.tools.arxiv_per_query}
        raw, cached = self.cache.get_or_call("arxiv", args, lambda: [
            p.model_dump() for p in arxiv.search(query, max_results=self.s.tools.arxiv_per_query,
                                                 user_agent=self.s.tools.user_agent)])
        papers = [Paper(**d) for d in raw]
        return self._register(papers, sub_rq_id, "search_arxiv", args, cached)

    def verify_doi(self, doi: str) -> dict | None:
        args = {"doi": doi.lower().strip()}
        res, cached = self.cache.get_or_call("crossref", args, lambda: crossref.verify_doi(
            doi, mailto=self.s.contact_email, user_agent=self.s.tools.user_agent))
        if self.log:
            self.log.tool("verify_doi", args, 1 if res else 0, cached)
        if res and args["doi"] in self.papers:
            self.papers[args["doi"]].verified = True
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
        for p in papers:
            if sub_rq_id and sub_rq_id not in p.sub_rq_ids:
                p.sub_rq_ids.append(sub_rq_id)
            if p.id in self.papers:
                ex = self.papers[p.id]
                ex.sub_rq_ids = sorted(set(ex.sub_rq_ids) | set(p.sub_rq_ids))
                if not ex.abstract and p.abstract:
                    ex.abstract = p.abstract
            else:
                self.papers[p.id] = p
        if self.log:
            self.log.tool(name, {k: v for k, v in args.items() if v is not None}, len(papers), cached)
        return [self.papers[p.id] for p in papers]


def _format_papers(ps: list[Paper], abstract_chars: int = 600) -> str:
    if not ps:
        return "no results"
    lines = []
    for p in ps:
        ab = (p.abstract or "")[:abstract_chars]
        lines.append(f"- id: {p.id} | {p.year} | {p.title} | {p.venue or ''} | cited_by={p.cited_by_count}\n  abstract: {ab}")
    return "\n".join(lines)
