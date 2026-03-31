#!/usr/bin/env python3
"""
Seed script — popula o banco com regras iniciais do motor de decisão.

Uso:
  # Com o compose rodando (recomendado):
  docker-compose exec decision-api python /app/../../../scripts/seed_rules.py

  # Local (requer banco acessível em localhost:5432):
  DATABASE_URL=postgresql+asyncpg://... python scripts/seed_rules.py
"""
import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone

# Adiciona o path do serviço decision-api
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "services", "decision-api"),
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.database import Base
from app.models.rule import Rule

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://decision_user:decision_pass@localhost:5432/decision_engine",
)

INITIAL_RULES = [
    {
        "name": "UNDERAGE_APPLICANT",
        "description": "Negação automática para menores de 18 anos.",
        "field": "age",
        "operator": "lt",
        "value": 18.0,
        "action": "deny",
        "weight": 100.0,
        "priority": 10,
        "product_type": None,
    },
    {
        "name": "LOW_INCOME_HARD",
        "description": "Renda mensal abaixo do mínimo absoluto (R$ 1.500). Negação imediata.",
        "field": "monthly_income",
        "operator": "lt",
        "value": 1500.0,
        "action": "deny",
        "weight": 100.0,
        "priority": 9,
        "product_type": None,
    },
    {
        "name": "CRITICAL_CREDIT_SCORE",
        "description": "Score de crédito abaixo do mínimo absoluto (< 300). Negação imediata.",
        "field": "credit_score",
        "operator": "lt",
        "value": 300.0,
        "action": "deny",
        "weight": 100.0,
        "priority": 9,
        "product_type": None,
    },
    {
        "name": "LOW_CREDIT_SCORE",
        "description": "Score de crédito abaixo do mínimo padrão (< 500). Negação.",
        "field": "credit_score",
        "operator": "lt",
        "value": 500.0,
        "action": "deny",
        "weight": 60.0,
        "priority": 8,
        "product_type": None,
    },
    {
        "name": "MEDIUM_CREDIT_RISK",
        "description": "Score na faixa de risco médio (500–649). Penalidade no score e sinalização de revisão.",
        "field": "credit_score",
        "operator": "lt",
        "value": 650.0,
        "action": "manual_review",
        "weight": 25.0,
        "priority": 5,
        "product_type": None,
    },
    {
        "name": "LOW_INCOME_FLAG",
        "description": "Renda na faixa de risco baixo (R$ 1.500–R$ 3.000). Penalidade no score.",
        "field": "monthly_income",
        "operator": "lt",
        "value": 3000.0,
        "action": "flag",
        "weight": 15.0,
        "priority": 3,
        "product_type": None,
    },
    {
        "name": "PREMIUM_INCOME_REQUIREMENT",
        "description": "Renda abaixo do mínimo para produto Gold (R$ 5.000). Negação para produto premium.",
        "field": "monthly_income",
        "operator": "lt",
        "value": 5000.0,
        "action": "deny",
        "weight": 80.0,
        "priority": 8,
        "product_type": "credit_card_gold",
    },
    {
        "name": "PREMIUM_SCORE_REQUIREMENT",
        "description": "Score abaixo do mínimo para produto Gold (< 650). Negação para produto premium.",
        "field": "credit_score",
        "operator": "lt",
        "value": 650.0,
        "action": "deny",
        "weight": 80.0,
        "priority": 8,
        "product_type": "credit_card_gold",
    },
]


async def seed() -> None:
    engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        inserted = 0
        skipped = 0

        for rule_data in INITIAL_RULES:
            existing = await session.execute(
                select(Rule).where(Rule.name == rule_data["name"])
            )
            if existing.scalar_one_or_none():
                print(f"  ⏭  Já existe: {rule_data['name']}")
                skipped += 1
                continue

            rule = Rule(
                id=str(uuid.uuid4()),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                **rule_data,
            )
            session.add(rule)
            inserted += 1

        await session.commit()

    print(f"\n✅ Seed concluído: {inserted} regras criadas, {skipped} já existiam.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
