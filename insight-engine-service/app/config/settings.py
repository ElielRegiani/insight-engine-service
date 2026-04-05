"""Environment-driven settings for Insight Service."""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _templates_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "prompts" / "templates"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    data_service_base_url: str = Field(
        default="http://localhost:8000",
        description="Base URL of the Data Service.",
    )
    ml_service_base_url: str = Field(
        default="http://localhost:8001",
        description="Base URL of the ML Service.",
    )

    data_service_timeout_seconds: float = 30.0
    data_service_max_retries: int = 3
    data_service_retry_backoff_seconds: float = 1.0

    ml_service_timeout_seconds: float = 60.0
    ml_service_max_retries: int = 2
    ml_service_retry_backoff_seconds: float = 0.5

    openai_api_key: str = Field(default="", description="OpenAI API key (empty = mock LLM in dev)")
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        description="OpenAI-compatible API base URL.",
    )
    openai_model: str = Field(default="gpt-4o-mini", description="Chat model name.")

    llm_max_tokens: int = 700
    llm_temperature: float = 0.3

    cache_ttl_seconds: float = 300.0
    summary_symbols: str = Field(
        default="PETR4,VALE3,ITUB4",
        description="Comma-separated symbols for daily market summary context.",
    )

    log_level: str = "INFO"

    templates_dir: Path = Field(default_factory=_templates_dir)

    @property
    def summary_symbol_list(self) -> List[str]:
        return [s.strip().upper() for s in self.summary_symbols.split(",") if s.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
