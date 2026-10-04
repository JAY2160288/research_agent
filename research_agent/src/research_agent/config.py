"""설정 로딩. config/models.yaml + .env 를 읽어 하나의 Settings 객체로 만든다."""

from __future__ import annotations

import os
from pathlib import Path

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
    max_tokens: int = 8192
    max_retries: int = 2


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
    cache_dir: str = ".cache"
    user_agent: str = "research-agent/0.1"


class Settings(BaseModel):
    llm: LLMConfig
    limits: Limits = Field(default_factory=Limits)
    pricing: dict[str, Price]
    tools: ToolsConfig = Field(default_factory=ToolsConfig)
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
