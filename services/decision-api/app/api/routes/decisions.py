import logging
import os

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limiter import limiter
from app.database import get_db
from app.schemas.decision import DecisionRequest, DecisionDetailResponse, DecisionResponse
from app.services.decision_service import get_decision_by_transaction, process_decision

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/decisions", tags=["decisions"])

# When RABBITMQ_URL is set the request goes through the async orchestrator.
# In tests (no RabbitMQ) the classic MVP-1 synchronous path is used instead.
_USE_ORCHESTRATOR = bool(os.getenv("RABBITMQ_URL"))

if _USE_ORCHESTRATOR:
    from app.services.orchestrator import orchestrate_decision


@router.post(
    "/",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submeter solicitação de decisão",
)
@limiter.limit("100/minute")
async def create_decision(
    request: Request,
    payload: DecisionRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Processa uma solicitação de crédito e retorna a decisão.

    MVP 2: quando RABBITMQ_URL está configurado, o fluxo passa por
    enrichment-service (HTTP) e rule-engine-service (RabbitMQ).
    Sem RABBITMQ_URL (testes / MVP-1 local), usa o caminho síncrono.
    """
    if _USE_ORCHESTRATOR:
        decision = await orchestrate_decision(payload, db)
    else:
        decision = await process_decision(payload, db)
    return decision


@router.get(
    "/{transaction_id}",
    response_model=DecisionDetailResponse,
    summary="Consultar decisão por transaction_id",
)
@limiter.limit("200/minute")
async def get_decision(
    request: Request,
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retorna o resultado completo de uma decisão pelo seu transaction_id."""
    decision = await get_decision_by_transaction(transaction_id, db)
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decisão com transaction_id '{transaction_id}' não encontrada.",
        )
    return decision
