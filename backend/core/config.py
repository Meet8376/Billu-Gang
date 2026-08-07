"""
Application Settings & Environment Configuration (LangChain & LangGraph Enabled).
Member 2 — Backend Core & Model Adapter Lead
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Core settings and configuration loaded from environment variables."""

    # Server Settings
    APP_NAME: str = "AE-01 Unified Agentic Coding Harness - Backend Core"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # LangChain / LangGraph Engine Config
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "ae-01-harness"

    # API Keys & Provider Config
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    DEFAULT_MODEL: str = "gpt-4o"
    FALLBACK_MODEL: str = "gpt-4o-mini"

    # Budget & Cost Limits
    MAX_BUDGET_USD: float = 10.0

    # CORS Settings
    CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
