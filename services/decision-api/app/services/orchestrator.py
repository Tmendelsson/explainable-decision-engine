"""
Orchestrator — Decision API MVP 2

Fluxo:
  1. Gera transaction_id + correlation_id
  2. Chama enrichment-service via HTTP (síncrono para manter latência previsível)
  3. Publica DecisionRequested no RabbitMQ
  4. Aguarda RulesEvaluated (com timeout configurável)
  5. Persiste Decision com sinais enriquecidos e retorna
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.logging import mask_cpf
from app.core.messaging import publish_decision_requested, wait_for_rules_evaluated
from app.models.decision import Decision
from app.schemas.decision import DecisionRequest

logger = logging.getLogger(__name__)
settings = get_settings()


async def _call_enrichment(
    transaction_id: str,
    correlation_id: str,
    request: DecisionRequest,
) -> dict[str, Any]:
    """
    Chama o enrichment-service via POST /enrich.
    Retorna o dict de resposta ou lança HTTPException em caso de falha.
    """
    payload = {
        "transaction_id": transaction_id,
        "correlation_id": correlation_id,
        "cpf": request.cpf,
        "product": request.product,
        "monthly_income": request.monthly_income,
        "age": request.age,
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                f"{settings.enrichment_service_url}/enrich", json=payload
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        logger.error(
            "Enrichment service returned %d transaction_id=%s",
            exc.response.status_code,
            transaction_id,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Enrichment service returned an error.",
        ) from exc
    except httpx.RequestError as exc:
        logger.error(
            "Enrichment service unreachable transaction_id=%s: %s",
            transaction_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Enrichment service is unavailable.",
        ) from exc


async def orchestrate_decision(
    request: DecisionRequest, db: AsyncSession
) -> Decision:
    """
    Orquestra o fluxo assíncrono de decisão MVP 2:
      enrichment (HTTP) → DecisionRequested (MQ) → RulesEvaluated (MQ) → persist
    """
    transaction_id = str(uuid.uuid4())
    correlation_id = str(uuid.uuid4())

    # ── Step 1: Enrich ────────────────────────────────────────────────────────
    enriched = await _call_enrichment(transaction_id, correlation_id, request)

    # Use enriched credit_score if the caller didn't provide one
    effective_credit_score = request.credit_score or enriched.get("credit_score")

    logger.info(
        "Enrichment done transaction_id=%s credit_score=%s flags=%s cpf=%s",
        transaction_id,
        enriched.get("credit_score"),
        enriched.get("fraud_flags"),
        mask_cpf(request.cpf),
    )

    # ── Step 2: Publish DecisionRequested ─────────────────────────────────────
    event_payload = {
        "cpf": request.cpf,
        "product": request.product,
        "monthly_income": request.monthly_income,
        "age": request.age,
        "credit_score": effective_credit_score,
    }

    await publish_decision_requested(
        transaction_id=transaction_id,
        correlation_id=correlation_id,
        payload=event_payload,
        enriched_data=enriched,
    )

    # ── Step 3: Wait for RulesEvaluated ───────────────────────────────────────
    result = await wait_for_rules_evaluated(
        transaction_id, timeout=settings.rules_evaluated_timeout
    )

    if result is None:
        logger.error(
            "Timeout waiting for RulesEvaluated transaction_id=%s", transaction_id
        )
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Rule engine did not respond in time.",
        )

    base_decision: str = result["base_decision"]
    risk_score: float = result["risk_score"]
    matched_rules: list[str] = result["matched_rules"]

    logger.info(
        "Rules evaluated transaction_id=%s decision=%s score=%.2f cpf=%s",
        transaction_id,
        base_decision,
        risk_score,
        mask_cpf(request.cpf),
    )

    # ── Step 4: Persist ───────────────────────────────────────────────────────
    decision = Decision(
        id=str(uuid.uuid4()),
        transaction_id=transaction_id,
        correlation_id=correlation_id,
        cpf=request.cpf,
        product=request.product,
        monthly_income=request.monthly_income,
        age=request.age,
        credit_score=effective_credit_score,
        status="completed",
        decision=base_decision,
        risk_score=risk_score,
        matched_rules=matched_rules,
        input_payload=request.model_dump(),
        enriched_data=enriched,
        created_at=datetime.now(timezone.utc),
    )

    try:
        db.add(decision)
        await db.commit()
        await db.refresh(decision)
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.error(
            "Failed to persist decision transaction_id=%s: %s", transaction_id, exc
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao persistir decisão.",
        ) from exc

    return decision
