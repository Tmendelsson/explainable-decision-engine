from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.rule import Rule
from app.schemas.rule import RuleCreate, RuleResponse

router = APIRouter(prefix="/rules", tags=["rules"])


@router.get(
    "/",
    response_model=List[RuleResponse],
    summary="Listar regras do motor",
)
async def list_rules(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """Retorna todas as regras. Por padrão, retorna apenas regras ativas."""
    query = select(Rule)
    if active_only:
        query = query.where(Rule.is_active == True)

    result = await db.execute(query.order_by(Rule.priority.desc(), Rule.name))
    return result.scalars().all()


@router.post(
    "/",
    response_model=RuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova regra",
)
async def create_rule(
    rule_data: RuleCreate,
    db: AsyncSession = Depends(get_db),
):
    """Adiciona uma nova regra ao motor de decisão."""
    import uuid
    from datetime import datetime, timezone

    rule = Rule(
        id=str(uuid.uuid4()),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        **rule_data.model_dump(),
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.patch(
    "/{rule_id}/toggle",
    response_model=RuleResponse,
    summary="Ativar ou desativar uma regra",
)
async def toggle_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Inverte o estado ativo/inativo de uma regra sem excluí-la."""
    result = await db.execute(select(Rule).where(Rule.id == rule_id))
    rule = result.scalar_one_or_none()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Regra '{rule_id}' não encontrada.",
        )

    rule.is_active = not rule.is_active
    await db.commit()
    await db.refresh(rule)
    return rule


@router.get(
    "/{rule_id}",
    response_model=RuleResponse,
    summary="Obter regra por ID",
)
async def get_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retorna os detalhes de uma regra específica."""
    result = await db.execute(select(Rule).where(Rule.id == rule_id))
    rule = result.scalar_one_or_none()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Regra '{rule_id}' não encontrada.",
        )

    return rule
