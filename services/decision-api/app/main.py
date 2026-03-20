import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import get_settings
from app.core.limiter import limiter
from app.core.logging import setup_logging
from app.database import engine, Base
from app.api.routes import decisions, rules

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.debug)
    logger.info('"Application starting", "version": "%s"', settings.app_version)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    logger.info('"Application shutting down"')
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Motor de decisão explicável com regras dinâmicas, score de risco "
        "e explicabilidade via IA. MVP 1 — Core Decision Engine."
    ),
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS — explicit whitelist (never allow_origins=["*"] in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
    allow_credentials=False,
)

app.include_router(decisions.router, prefix="/api/v1")
app.include_router(rules.router, prefix="/api/v1")


@app.get("/health", tags=["infra"])
async def health_check():
    return {
        "status": "healthy",
        "service": "decision-api",
        "version": settings.app_version,
    }
