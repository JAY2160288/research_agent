"""Anthropic SDK 래퍼. 프로젝트의 유일한 LLM 호출 지점 (plan.md ADR-2).

- `call(...)`      : 프롬프트 → Pydantic 모델. SDK 의 structured output(`messages.parse`) 사용.
                     스키마·검증 실패 시 오류를 붙여 최대 max_retries 회 재요청.
- `call_with_tools`: ReAct 베이스라인용. tool use 루프의 한 턴을 수행하고 원 응답을 돌려준다.
- 모든 호출은 RunLogger 에 토큰·비용·시도 횟수를 남기고, 비용 상한을 넘으면 CostLimitExceeded.

모델명은 config/models.yaml 에서만 바꾼다. 다른 공급자 지원은 non-goal (goals.md §3).
"""

from __future__ import annotations

from typing import Any, TypeVar

import anthropic
from pydantic import BaseModel, ValidationError

from .config import Settings
from .runlog import RunLogger

T = TypeVar("T", bound=BaseModel)


class CostLimitExceeded(RuntimeError):
    pass


class TimeLimitExceeded(RuntimeError):
    pass


class LLMError(RuntimeError):
    pass


class LLM:
    def __init__(self, settings: Settings, log: RunLogger | None = None, client: anthropic.Anthropic | None = None):
        self.s = settings
        self.log = log
        self.client = client or anthropic.Anthropic(api_key=settings.anthropic_api_key, max_retries=3)

    # ------------------------------------------------------------------
    def _cost(self, model: str, usage: Any) -> tuple[int, int, float]:
        p = self.s.price_for(model)
        i, o = int(getattr(usage, "input_tokens", 0) or 0), int(getattr(usage, "output_tokens", 0) or 0)
        return i, o, (i * p.input + o * p.output) / 1_000_000

    def _guard(self) -> None:
        if self.log is None:
            return
        if self.log.cost_usd > self.s.limits.max_cost_usd:
            raise CostLimitExceeded(f"cost {self.log.cost_usd:.3f} > {self.s.limits.max_cost_usd}")
        if self.log.elapsed_min > self.s.limits.max_minutes:
            raise TimeLimitExceeded(f"elapsed {self.log.elapsed_min:.1f}min > {self.s.limits.max_minutes}")

    # ------------------------------------------------------------------
    def call(
        self,
        *,
        role: str,
        system: str,
        user: str,
        schema: type[T],
        model: str | None = None,
        max_tokens: int | None = None,
    ) -> T:
        """구조화 출력 호출. 결과는 schema 인스턴스. 검증 실패는 오류 메시지를 되먹여 재시도."""
        model = model or self.s.llm.model
        max_tokens = max_tokens or self.s.llm.max_tokens
        messages: list[dict[str, Any]] = [{"role": "user", "content": user}]
        last_err: str | None = None

        for attempt in range(1, self.s.llm.max_retries + 2):
            self._guard()
            resp = self.client.messages.parse(
                model=model, max_tokens=max_tokens, system=system, messages=messages, output_format=schema,
            )
            i, o, cost = self._cost(model, resp.usage)
            parsed = next((b.parsed_output for b in resp.content if getattr(b, "parsed_output", None) is not None), None)
            raw_text = "".join(getattr(b, "text", "") for b in resp.content)

            if parsed is None:
                last_err = f"no parsed output (stop_reason={resp.stop_reason}); raw={raw_text[:300]}"
            else:
                try:
                    obj = schema.model_validate(parsed if isinstance(parsed, dict) else parsed.model_dump())
                    if self.log:
                        self.log.llm(role=role, model=model, input_tokens=i, output_tokens=o, cost_usd=cost, attempt=attempt, ok=True)
                    return obj
                except ValidationError as e:
                    last_err = f"schema validation failed: {e.errors(include_url=False)[:5]}"

            if self.log:
                self.log.llm(role=role, model=model, input_tokens=i, output_tokens=o, cost_usd=cost, attempt=attempt, ok=False, error=last_err)
            # 되먹임: 이전 응답과 오류를 대화에 추가해 수정 요청
            messages.append({"role": "assistant", "content": raw_text or "(empty)"})
            messages.append({"role": "user", "content": f"Your previous output was rejected: {last_err}\n"
                                                        f"Return a corrected object that satisfies the schema exactly."})
        raise LLMError(f"{role}: failed after retries — {last_err}")

    # ------------------------------------------------------------------
    def call_with_tools(
        self,
        *,
        role: str,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        tool_choice: dict[str, Any] | None = None,
        model: str | None = None,
        max_tokens: int | None = None,
    ) -> anthropic.types.Message:
        """ReAct 한 턴. 호출자가 tool_use 블록을 꺼내 실행하고 tool_result 를 messages 에 붙인다."""
        self._guard()
        model = model or self.s.llm.model
        kwargs: dict[str, Any] = dict(model=model, max_tokens=max_tokens or self.s.llm.max_tokens,
                                      system=system, messages=messages, tools=tools)
        if tool_choice:
            kwargs["tool_choice"] = tool_choice
        resp = self.client.messages.create(**kwargs)
        i, o, cost = self._cost(model, resp.usage)
        if self.log:
            self.log.llm(role=role, model=model, input_tokens=i, output_tokens=o, cost_usd=cost, attempt=1, ok=True)
        return resp


def schema_as_tool(schema: type[BaseModel], name: str, description: str) -> dict[str, Any]:
    """Pydantic 모델을 tool 정의로 변환 (베이스라인에서 최종 출력 강제용)."""
    return {"name": name, "description": description, "input_schema": schema.model_json_schema()}
