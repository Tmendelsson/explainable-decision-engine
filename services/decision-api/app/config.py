from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Explainable Decision Engine"
    app_version: str = "1.0.0"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://decision_user:decision_pass@localhost:5432/decision_engine"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
