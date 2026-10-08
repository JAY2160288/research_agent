"""실행 기록. runs/<timestamp>_<slug>/ 아래에 이벤트(JSONL), 비용, 최종 리포트를 남긴다.

재현성(goals.md O7)의 근거 자료이자, 설계평가에서 Planning/Reflection/Replanning 이
실제로 일어났음을 보여주는 증거다. 외부 서비스 없이 파일만 쓴다.
"""

from __future__ import annotations

import json
import re
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel

from .config import RUNS_DIR


def _slug(text: str, n: int = 40) -> str:
    s = re.sub(r"[^\w가-힣]+", "-", text).strip("-").lower()
    return s[:n] or "run"


class RunLogger:
    def __init__(self, topic: str, mode: str, runs_dir: Path = RUNS_DIR, *,
                 into: Path | None = None, prefix: str = ""):
        """새 실행 폴더 runs/<ts>_<mode>_<slug>/ 를 만든다.

        into/prefix: 이미 끝난 실행 폴더에 **덧붙여** 기록할 때 (LLM-judge 등 사후 작업). 새 폴더를 만들지 않고
        `<into>/<prefix>events.jsonl` 에 쓴다 — 채점 비용·호출이 원 실행의 events.jsonl·cost.json 과 섞이지 않는다.
        """
        if into is not None:
            self.dir = into
        else:
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            self.dir = runs_dir / f"{ts}_{mode}_{_slug(topic)}"
        self.dir.mkdir(parents=True, exist_ok=True)
        self._events = self.dir / f"{prefix}events.jsonl"
        self._t0 = time.monotonic()
        self._lock = threading.Lock()   # evaluate 배치·search 쿼리가 병렬로 돌아 이벤트 기록·비용 합산을 직렬화한다
        self.listeners: list[Callable[[dict[str, Any]], None]] = []   # 진행 표시용 — 이벤트마다 호출 (CLI 가 등록)
        self.cost_usd = 0.0
        self.input_tokens = 0
        self.output_tokens = 0
        self.llm_calls = 0
        self.event("run_start", topic=topic, mode=mode)

    # ---- 이벤트 -------------------------------------------------------
    def event(self, kind: str, **data: Any) -> None:
        rec = {"t": round(time.monotonic() - self._t0, 3), "kind": kind, **_jsonable(data)}
        with self._lock:
            with self._events.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        for fn in self.listeners:
            try:
                fn(rec)
            except Exception:  # noqa: BLE001 — 진행 표시가 실행을 죽이면 안 된다
                pass

    def seed(self, *, cost_usd: float = 0.0, llm_calls: int = 0, input_tokens: int = 0, output_tokens: int = 0) -> None:
        """재개(`--resume`) 시 이전 구간의 비용·호출 수를 이어받는다. 시간은 새로 센다 (상한은 재개 구간 기준)."""
        with self._lock:
            self.cost_usd += cost_usd
            self.llm_calls += llm_calls
            self.input_tokens += input_tokens
            self.output_tokens += output_tokens

    def llm(self, *, role: str, model: str, input_tokens: int, output_tokens: int,
            cost_usd: float, attempt: int, ok: bool, error: str | None = None,
            cache_read: int = 0, cache_write: int = 0) -> None:
        """input_tokens 는 캐시 미적중분. cache_read/cache_write 는 프롬프트 캐시 적중·생성 토큰 (비용 10% / 125%)."""
        with self._lock:
            self.llm_calls += 1
            self.input_tokens += input_tokens + cache_read + cache_write
            self.output_tokens += output_tokens
            self.cost_usd += cost_usd
        self.event("llm_call", role=role, model=model, input_tokens=input_tokens,
                   cache_read=cache_read, cache_write=cache_write,
                   output_tokens=output_tokens, cost_usd=round(cost_usd, 6),
                   attempt=attempt, ok=ok, error=error)

    def tool(self, name: str, args: dict[str, Any], n_results: int, cached: bool) -> None:
        self.event("tool_call", name=name, args=args, n_results=n_results, cached=cached)

    # ---- 산출물 -------------------------------------------------------
    def save(self, name: str, obj: Any) -> Path:
        """중간 산출물을 JSON 또는 텍스트로 저장."""
        if isinstance(obj, BaseModel):
            path = self.dir / f"{name}.json"
            path.write_text(obj.model_dump_json(indent=2, ensure_ascii=False) if hasattr(obj, "model_dump_json")
                            else json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
        elif isinstance(obj, str):
            path = self.dir / name
            path.write_text(obj, encoding="utf-8")
        else:
            path = self.dir / f"{name}.json"
            path.write_text(json.dumps(_jsonable(obj), ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def finish(self, status: str = "ok", **extra: Any) -> dict[str, Any]:
        summary = {
            "status": status,
            "elapsed_sec": round(time.monotonic() - self._t0, 1),
            "llm_calls": self.llm_calls,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost_usd": round(self.cost_usd, 4),
            **extra,
        }
        (self.dir / "cost.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        self.event("run_end", **summary)
        return summary

    @property
    def elapsed_min(self) -> float:
        return (time.monotonic() - self._t0) / 60


def _jsonable(x: Any) -> Any:
    if isinstance(x, BaseModel):
        return x.model_dump(mode="json")
    if isinstance(x, dict):
        return {k: _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    return x
