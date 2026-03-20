from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Explainable Decision Engine"
    app_version: str = "1.0.0"
    debug: bool = False

    # Must be set via .env — no hardcoded default to avoid credential leaks
    database_url: str

    # CORS — explicit whitelist; set CORS_ORIGINS in .env for production
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Risk scoring thresholds (configurable per environment)
    approve_threshold: float = 70.0
    manual_review_threshold: float = 50.0

    # In-memory rules cache TTL (seconds)
    rules_cache_ttl_seconds: int = 300

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
