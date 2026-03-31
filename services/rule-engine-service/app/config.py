from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Rule Engine Service"
    app_version: str = "0.2.0"
    debug: bool = False
    app_env: str = "development"

    # Must be set via environment / .env
    database_url: str
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"

    # RabbitMQ topology
    exchange_name: str = "decision.events"
    decision_requested_routing_key: str = "decision.requested"
    rules_evaluated_routing_key: str = "rules.evaluated"
    queue_name: str = "rule-engine.decision-requested"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
