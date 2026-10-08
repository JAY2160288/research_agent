"""도구 응답 캐시 (diskcache). 키 = 도구명 + 정규화된 인자.

용도: (1) 개발 중 반복 실행 비용·rate limit 절감, (2) ablation 공정성 — 같은 검색 스냅샷 위에서
구조만 바꿔 비교 (plan.md §6.3). live 재현 시에는 `--no-cache` 로 끈다.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from diskcache import Cache


class ToolCache:
    def __init__(self, cache_dir: str | Path, enabled: bool = True):
        self.enabled = enabled
        self._c = Cache(str(cache_dir)) if enabled else None

    @staticmethod
    def _norm_value(v: Any) -> Any:
        """문자열 인자(검색 쿼리)는 소문자·공백 정리·양끝 따옴표 제거. plan 노드가 실행마다 쿼리를 조금씩 다르게 써서
        같은 주제 재실행에도 캐시가 거의 안 맞았다 (2026-10-08 클린룸 관찰) — 대소문자·공백 차이만이라도 흡수한다.
        단어 순서는 바꾸지 않는다 (검색 엔진의 순위가 달라질 수 있으므로)."""
        if isinstance(v, str):
            return " ".join(v.strip().strip('"\'').split()).lower()
        return v

    @classmethod
    def key(cls, tool: str, args: dict[str, Any]) -> str:
        norm = json.dumps({k: cls._norm_value(args[k]) for k in sorted(args)}, ensure_ascii=False, sort_keys=True)
        return f"{tool}:{hashlib.sha1(norm.encode()).hexdigest()}"

    def get_or_call(self, tool: str, args: dict[str, Any], fn: Callable[[], Any]) -> tuple[Any, bool]:
        """(결과, 캐시 적중 여부)"""
        if not self.enabled or self._c is None:
            return fn(), False
        k = self.key(tool, args)
        if k in self._c:
            return self._c[k], True
        out = fn()
        self._c[k] = out
        return out, False
