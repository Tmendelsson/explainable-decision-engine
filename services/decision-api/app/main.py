from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, Base
from app.api.routes import decisions, rules

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
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
