"""W1-1.4 스모크 테스트 — 실제 네트워크로 OpenAlex / arXiv / Crossref 가 동작하는지 확인. LLM 호출 없음.

실행:  uv run python scripts/smoke_tools.py
"""

from __future__ import annotations

import sys
import time

from research_agent.config import load_settings
from research_agent.tools import Tools


def main() -> int:
    s = load_settings()
    t = Tools(s, use_cache=False)
    ok = True

    t0 = time.time()
    try:
        ps = t.search_openalex("generative AI graduate students research productivity", from_year=2022)
        print(f"[openalex] {len(ps)} papers in {time.time()-t0:.1f}s")
        for p in ps[:3]:
            print(f"   {p.year} | {p.title[:70]} | doi={p.doi} | abstract={'yes' if p.abstract else 'NO'}")
        ok &= len(ps) >= 5
    except Exception as e:  # noqa: BLE001 — 429 = 일일 크레딧(1000, 검색당 10) 소진. 파이프라인은 Crossref 로 폴백한다
        print(f"[openalex] FAILED: {str(e)[:120]}  → 파이프라인은 Crossref 폴백으로 계속 (ADR-8)")

    t0 = time.time()
    ps = t.search_crossref("generative AI graduate students research productivity", from_year=2022)
    print(f"[crossref search] {len(ps)} papers in {time.time()-t0:.1f}s  (OpenAlex 폴백용, ADR-8)")
    for p in ps[:3]:
        print(f"   {p.year} | {p.title[:70]} | doi={p.doi} | abstract={'yes' if p.abstract else 'NO'}")
    ok &= len(ps) >= 5

    t0 = time.time()
    ps = t.search_arxiv("LLM agent long-term memory multi-step tasks")
    print(f"[arxiv]    {len(ps)} papers in {time.time()-t0:.1f}s")
    for p in ps[:3]:
        print(f"   {p.year} | {p.title[:70]} | id={p.id}")
    ok &= len(ps) >= 5

    t0 = time.time()
    r1 = t.verify_doi("10.1038/nature14539")      # 실존 (LeCun et al. 2015, Deep learning)
    r2 = t.verify_doi("10.9999/this-does-not-exist")
    print(f"[crossref] real={bool(r1)} fake={bool(r2)} in {time.time()-t0:.1f}s")
    ok &= bool(r1) and not r2

    n_abs = sum(1 for p in t.papers.values() if p.abstract)
    print(f"\n문헌 {len(t.papers)}편 수집, 초록 있음 {n_abs}편 ({n_abs/len(t.papers):.0%})")
    print("결과:", "통과" if ok else "실패 — 위 항목 확인")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
