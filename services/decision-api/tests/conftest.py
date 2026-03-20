"""
conftest.py — shared fixtures for all tests.

Uses an in-memory SQLite database so tests run without a live PostgreSQL instance.
"""
import os

# Set env vars BEFORE any app module is imported (pydantic-settings reads at import time)
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_decision.db")
os.environ.setdefault("CORS_ORIGINS", '["http://localhost:3000"]')
os.environ.setdefault("DEBUG", "false")

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.database import Base, get_db
from app.services import decision_service

TEST_DB_URL = "sqlite+aiosqlite:///./test_decision.db"

_test_engine = create_async_engine(TEST_DB_URL, echo=False)
_TestSession = async_sessionmaker(bind=_test_engine, expire_on_commit=False, class_=AsyncSession)


async def _override_get_db():
    async with _TestSession() as session:
        yield session


app.dependency_overrides[get_db] = _override_get_db


@pytest_asyncio.fixture(autouse=True)
async def reset_db():
    """Create all tables before each test, drop after."""
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Invalidate any stale in-memory rules cache between tests
    decision_service.invalidate_rules_cache()
    yield
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
