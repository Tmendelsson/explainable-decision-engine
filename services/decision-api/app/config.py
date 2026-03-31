from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Explainable Decision Engine"
    app_version: str = "2.0.0"
    debug: bool = False
    app_env: str = "development"

    # Must be set via .env — no hardcoded default to avoid credential leaks
    database_url: str

    # CORS — explicit whitelist; set CORS_ORIGINS in .env for production
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Risk scoring thresholds (configurable per environment)
    approve_threshold: float = 70.0
    manual_review_threshold: float = 50.0

    # In-memory rules cache TTL (seconds)
    rules_cache_ttl_seconds: int = 300

    # ── MVP 2: RabbitMQ ──────────────────────────────────────────────────────
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    exchange_name: str = "decision.events"
    decision_requested_routing_key: str = "decision.requested"
    rules_evaluated_routing_key: str = "rules.evaluated"
    rules_evaluated_queue: str = "decision-api.rules-evaluated"

    # Timeout (seconds) waiting for RulesEvaluated reply from rule-engine
    rules_evaluated_timeout: float = 10.0

    # ── MVP 2: Enrichment Service ─────────────────────────────────────────────
    enrichment_service_url: str = "http://enrichment-service:8001"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
