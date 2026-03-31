"""
Rule Engine Service — MVP 2

Responsabilidades:
  - Consumir evento DecisionRequested do RabbitMQ
  - Carregar regras ativas do banco de dados
  - Avaliar regras eliminatórias e de penalidade contra o payload enriquecido
  - Calcular score de risco
  - Publicar evento RulesEvaluated
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.messaging.consumer import close_connection, start_consumer

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logger.info("Rule Engine Service starting version=%s", settings.app_version)
    await start_consumer()
    yield
    logger.info("Rule Engine Service shutting down")
    await close_connection()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Rule Engine Service — MVP 2. "
        "Decisor determinístico via eventos RabbitMQ."
    ),
    lifespan=lifespan,
)


@app.get("/health", tags=["infra"])
async def health():
    return {
        "status": "healthy",
        "service": "rule-engine-service",
        "version": settings.app_version,
    }

