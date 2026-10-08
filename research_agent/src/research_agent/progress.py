"""CLI 진행 표시 (2026-10-08, docs/quality.md C1, ADR-12). 파이프라인 코드는 손대지 않고 RunLogger 이벤트만 구독한다.

6~8분짜리 실행을 깜깜이로 기다리지 않도록 노드 전이·검색/평가 편수·Critic 판정·Replan 쿼리·누적 비용을 한 줄씩 찍는다.
의존성 없음(rich 미사용) — 어떤 터미널·로그 파일에서도 같은 출력. `--quiet` 로 끈다.
"""

from __future__ import annotations

from typing import Any, Callable

_KO = {"understand": "주제 이해", "plan": "조사 계획", "search": "문헌 탐색", "evaluate": "문헌 평가",
       "synthesize": "종합", "gap": "Gap 도출", "critic": "Critic 검사", "replan": "재계획", "write": "리포트 작성"}


class Progress:
    """RunLogger.listeners 에 등록하는 콜백. `echo` 는 한 줄 출력 함수 (테스트에서는 리스트 append)."""

    def __init__(self, echo: Callable[[str], None]):
        self.echo = echo
        self.cost = 0.0
        self.calls = 0
        self.tool_calls = 0
        self.tool_cached = 0
        self._last_cost_line = 0.0

    @staticmethod
    def _min(rec: dict[str, Any]) -> str:
        return f"{rec.get('t', 0) / 60:.1f}분"

    def __call__(self, rec: dict[str, Any]) -> None:
        k = rec.get("kind")
        if k == "run_start":
            self.echo(f"▶ 실행 시작: {rec.get('topic', '')[:70]}  (mode={rec.get('mode')})")
        elif k == "resumed":
            self.echo(f"↻ 재개: 라운드 {rec.get('round')} · 끝난 노드 {', '.join(rec.get('done') or [])} · 이전 비용 ${(rec.get('prior') or {}).get('cost_usd', 0):.2f}")
        elif k == "node_start":
            r = rec.get("round", 0)
            tag = f"[r{r + 1}] " if rec.get("node") in _KO and rec.get("node") not in ("understand", "plan", "write") else ""
            self.echo(f"  {tag}{_KO.get(rec.get('node'), rec.get('node'))} …")
        elif k == "node_end":
            self.echo(f"  ✓ {_KO.get(rec.get('node'), rec.get('node'))}  ({self._min(rec)} · ${self.cost:.2f} · LLM {self.calls}회)")
        elif k == "node_skipped":
            self.echo(f"  ↷ {_KO.get(rec.get('node'), rec.get('node'))} 건너뜀 (재개)")
        elif k == "node_reused":
            self.echo(f"  ↷ {_KO.get(rec.get('node'), rec.get('node'))} 재사용 ({rec.get('source')})")
        elif k == "llm_call":
            self.calls += 1
            self.cost += float(rec.get("cost_usd") or 0.0)
            if not rec.get("ok"):
                self.echo(f"    ↺ {rec.get('role')} 재시도 {rec.get('attempt')}: {str(rec.get('error'))[:90]}")
        elif k == "tool_call":
            self.tool_calls += 1
            if rec.get("cached"):
                self.tool_cached += 1
        elif k == "node_check":
            node = rec.get("node")
            if node == "search":
                counts = rec.get("counts") or {}
                self.echo(f"    후보 {sum(counts.values())}편 ({', '.join(f'{k} {v}' for k, v in counts.items())}) · 검색 {self.tool_calls}회 (캐시 {self.tool_cached})")
                if rec.get("issues"):
                    self.echo(f"    ⚠ 후보 부족: {rec['issues']}")
            elif node == "evaluate" and rec.get("evaluated") is not None:
                self.echo(f"    평가 {rec.get('evaluated')}편 (후보 {rec.get('candidates')}편 중 이번 라운드 신규)")
            elif node == "write":
                c = rec.get("checks") or {}
                if c:
                    self.echo(f"    인용 검증 {c.get('citations_verified')}/{c.get('citations_total')} · claim 출처 {c.get('claims_with_source')}/{c.get('claims_total')}"
                              f" · sub-RQ {c.get('sub_rqs_covered')}/{c.get('sub_rqs')} · Gap {c.get('gaps_with_2_evidence')}/{c.get('gaps')}")
        elif k == "evaluate_batches":
            self.echo(f"    배치 {rec.get('batches')}개 × 병렬 {rec.get('workers')}")
        elif k == "critique":
            verdict = "통과" if rec.get("passed") else "미달"
            det = rec.get("issues") or []
            maj = rec.get("llm_major") or []
            self.echo(f"    Critic r{rec.get('round')}: {verdict}  결정적 이슈 {len(det)} · LLM major {len(maj)}" +
                      (f" · 재검색 대상 {rec.get('uncovered')}" if rec.get("uncovered") else ""))
            for x in (det + maj)[:3]:
                self.echo(f"      - {str(x)[:110]}")
        elif k == "replan":
            qs = rec.get("queries") or {}
            self.echo(f"    Replan {rec.get('round')}: " + "; ".join(f"{k} +{len(v)}개" for k, v in qs.items()))
        elif k == "openalex_fallback":
            self.echo(f"    ⚠ OpenAlex 실패 {rec.get('failed_queries')}/{rec.get('total')} → Crossref 폴백")
        elif k == "arxiv_disabled":
            self.echo(f"    ⚠ arXiv 차단 (실패 {rec.get('after_failures')}회, {rec.get('skipped_queries')}개 쿼리 생략)")
        elif k == "include_papers":
            self.echo(f"    고정 문헌 {len(rec.get('registered') or [])}/{len(rec.get('requested') or [])} 등록")
        elif k in ("replan_limit", "replan_skipped_budget"):
            self.echo("    Replan 상한·예산 도달 → 미달 항목은 §7 한계에 기재하고 리포트 작성")
        elif k == "limit_exceeded":
            self.echo(f"  ⚠ 상한 초과: {rec.get('error')}")
        elif k == "grace_write":
            self.echo("  … 종합·Gap 까지 끝나 있어 리포트는 작성합니다")
        elif k == "interrupted":
            self.echo("  ✋ 중단됨 — `agent run --resume <결과 폴더>` 로 이어서 실행할 수 있습니다")
        elif k == "error":
            self.echo(f"  ✗ 오류: {rec.get('error')}")
