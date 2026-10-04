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
    def key(tool: str, args: dict[str, Any]) -> str:
        norm = json.dumps({k: args[k] for k in sorted(args)}, ensure_ascii=False, sort_keys=True)
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
