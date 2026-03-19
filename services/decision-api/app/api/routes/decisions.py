from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.decision import DecisionRequest, DecisionResponse, DecisionDetailResponse
from app.services.decision_service import process_decision, get_decision_by_transaction

router = APIRouter(prefix="/decisions", tags=["decisions"])


@router.post(
    "/",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submeter solicitação de decisão",
)
async def create_decision(
    request: DecisionRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Processa uma solicitação de crédito e retorna a decisão imediatamente.

    A decisão é baseada em regras dinâmicas configuradas no banco de dados.
    Cada regra pode ter ação `deny` (eliminatória) ou `flag`/`manual_review` (penalidade no score).
    """
    decision = await process_decision(request, db)
    return decision


@router.get(
    "/{transaction_id}",
    response_model=DecisionDetailResponse,
    summary="Consultar decisão por transaction_id",
)
async def get_decision(
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
