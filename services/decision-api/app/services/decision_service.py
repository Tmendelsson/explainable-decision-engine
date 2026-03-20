import logging
import time
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.logging import mask_cpf
from app.models.decision import Decision
from app.models.rule import Rule
from app.schemas.decision import DecisionRequest
from app.services.rule_engine import evaluate_rules
from app.services.scoring import calculate_risk_score, determine_decision

logger = logging.getLogger(__name__)
settings = get_settings()

# ---------------------------------------------------------------------------
# In-memory rules cache (TTL-based, invalidated on rule mutations)
# ---------------------------------------------------------------------------
_rules_cache: list | None = None
_rules_cache_ts: float = 0.0


def invalidate_rules_cache() -> None:
    global _rules_cache, _rules_cache_ts
    _rules_cache = None
    _rules_cache_ts = 0.0
    logger.info('"Rules cache invalidated"')


async def _get_active_rules(db: AsyncSession) -> list:
    global _rules_cache, _rules_cache_ts
    now = time.monotonic()
    if _rules_cache is not None and (now - _rules_cache_ts) < settings.rules_cache_ttl_seconds:
        return _rules_cache
    result = await db.execute(select(Rule).where(Rule.is_active == True))
    _rules_cache = result.scalars().all()
    _rules_cache_ts = now
    logger.info('"Rules cache refreshed", "count": %d', len(_rules_cache))
    return _rules_cache


async def process_decision(request: DecisionRequest, db: AsyncSession) -> Decision:
    """
    Processa uma solicitação de decisão:
      1. Carrega regras ativas (com cache)
      2. Filtra por produto ou global
      3. Avalia regras contra o payload
      4. Calcula score e determina decisão
      5. Persiste e retorna o resultado
    """
    all_rules = await _get_active_rules(db)

    applicable_rules = [
        r for r in all_rules
        if r.product_type is None or r.product_type == request.product
    ]

    payload = {
        "monthly_income": request.monthly_income,
        "age": request.age,
        "credit_score": request.credit_score,
    }

    matched_deny, matched_flag, total_penalty = evaluate_rules(payload, applicable_rules)

    risk_score = calculate_risk_score(total_penalty)
    final_decision = determine_decision(
        matched_deny,
        risk_score,
        settings.approve_threshold,
        settings.manual_review_threshold,
    )
    all_matched = matched_deny + matched_flag

    logger.info(
        '"Decision processed", "cpf": "%s", "product": "%s", "decision": "%s", "risk_score": %.2f',
        mask_cpf(request.cpf),
        request.product,
        final_decision,
        risk_score,
    )

    decision = Decision(
        id=str(uuid.uuid4()),
        transaction_id=str(uuid.uuid4()),
        cpf=request.cpf,
        product=request.product,
        monthly_income=request.monthly_income,
        age=request.age,
        credit_score=request.credit_score,
        status="completed",
        decision=final_decision,
        risk_score=risk_score,
        matched_rules=all_matched,
        input_payload=request.model_dump(),
        created_at=datetime.now(timezone.utc),
    )

    try:
        db.add(decision)
        await db.commit()
        await db.refresh(decision)
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.error('"Failed to persist decision", "error": "%s"', str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao persistir decisão.",
        ) from exc

    return decision


async def get_decision_by_transaction(
    transaction_id: str, db: AsyncSession
) -> Decision | None:
    result = await db.execute(
        select(Decision).where(Decision.transaction_id == transaction_id)
    )
    return result.scalar_one_or_none()

