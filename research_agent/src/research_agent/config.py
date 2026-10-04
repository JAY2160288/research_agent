"""설정 로딩. config/models.yaml + .env 를 읽어 하나의 Settings 객체로 만든다."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]  # research_agent/ 프로젝트 루트
CONFIG_PATH = ROOT / "config" / "models.yaml"
PROMPTS_DIR = ROOT / "prompts"
RUNS_DIR = ROOT / "runs"


class LLMConfig(BaseModel):
    model: str
    judge_model: str
    max_tokens: int = 8192             # 베이스라인 ReAct·최종 브리프용 상한
    node_max_tokens: int = 6000        # 그래프 노드 1회 호출 상한. 노드 출력은 2~3k 토큰이면 충분 — 더 크면 폭주 출력이 잘려 JSON 이 깨진다
    max_retries: int = 2
    request_timeout_sec: float = 180   # HTTP 요청 1건 상한. SDK 기본 600초라 멈춘 요청 하나가 10분 상한을 통째로 먹는다 (2026-10-04 관찰)
    sdk_max_retries: int = 2           # 연결 오류·타임아웃·429 에 대한 SDK 자동 재시도


class Limits(BaseModel):
    max_cost_usd: float = 1.0
    max_minutes: float = 10.0
    max_react_steps: int = 15


class Price(BaseModel):
    input: float  # USD per 1M tokens
    output: float


class ToolsConfig(BaseModel):
    openalex_per_query: int = 15
    arxiv_per_query: int = 10
    crossref_per_query: int = 15       # OpenAlex 실패(429 등) 시 폴백 검색 (ADR-8)
    cache_dir: str = ".cache"
    user_agent: str = "research-agent/0.1"
    # 그래프 노드 상한 (plan.md §3.2)
    search_min_per_subrq: int = 10     # search 결정적 검증: sub-RQ 당 후보 ≥ 이 값
    search_workers: int = 4            # OpenAlex 병렬 요청 수 (arXiv 는 순차)
    arxiv_max_queries_per_subrq: int = 2  # arXiv 는 3초/요청 → sub-RQ 당 쿼리 상한
    arxiv_interval_sec: float = 3.0    # arXiv 요청 간격 (공식 권고 3초)
    arxiv_max_failures: int = 2        # 연속 실패 시 이 실행에서 arXiv 차단 (circuit breaker)
    evaluate_per_subrq: int = 12       # evaluate 에 넘길 sub-RQ 당 후보 상한 (초록 있음·피인용·최신 순)
    evaluate_batch: int = 10           # evaluate LLM 1회 호출당 문헌 수
    min_relevance: int = 3             # synthesize·coverage 계산에 쓰는 relevance 하한
    min_evidence_per_subrq: int = 3    # Critic: sub-RQ 당 evidence ≥ 이 값


class GraphConfig(BaseModel):
    """그래프 모드의 품질 게이트 설정. ablation 조건 B/C/D 는 이 두 값으로 만든다 (plan.md §6.3)."""
    critic: Literal["none", "deterministic", "full"] = "full"  # none=B, deterministic=C, full=D(결정적 + LLM 비판)
    max_replans: int = 2               # Critic 미달 시 Replan 상한 (plan.md §3.3). 0 이면 루프 없음
    replan_budget_fraction: float = 0.6  # 경과 시간·비용이 상한의 이 비율을 넘으면 Replan 을 건너뛰고 write 로 (완주 우선, O1)


class Settings(BaseModel):
    llm: LLMConfig
    limits: Limits = Field(default_factory=Limits)
    pricing: dict[str, Price]
    tools: ToolsConfig = Field(default_factory=ToolsConfig)
    graph: GraphConfig = Field(default_factory=GraphConfig)
    anthropic_api_key: str | None = None
    contact_email: str | None = None

    def price_for(self, model: str) -> Price:
        return self.pricing.get(model) or self.pricing["default"]


def load_settings(config_path: Path = CONFIG_PATH, env_path: Path | None = None) -> Settings:
    load_dotenv(env_path or ROOT / ".env")
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return Settings(
        **raw,
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        contact_email=os.getenv("CONTACT_EMAIL"),
    )


def load_prompt(name: str) -> str:
    """prompts/<name>.md 를 읽는다. 프롬프트는 코드에 두지 않는다 (plan.md §3.1)."""
    return (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")
