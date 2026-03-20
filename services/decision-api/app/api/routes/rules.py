import logging
import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limiter import limiter
from app.database import get_db
from app.models.rule import Rule
from app.schemas.rule import RuleCreate, RuleResponse
from app.services.decision_service import invalidate_rules_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rules", tags=["rules"])


@router.get(
    "/",
    response_model=List[RuleResponse],
    summary="Listar regras do motor",
)
@limiter.limit("200/minute")
async def list_rules(
    request: Request,
    active_only: bool = True,
    skip: int = Query(default=0, ge=0, description="Número de registros a pular"),
    limit: int = Query(default=50, ge=1, le=200, description="Máximo de registros retornados"),
    db: AsyncSession = Depends(get_db),
):
    """Retorna regras com paginação. Por padrão, retorna apenas regras ativas."""
    query = select(Rule)
    if active_only:
        query = query.where(Rule.is_active == True)
    query = query.order_by(Rule.priority.desc(), Rule.name).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post(
    "/",
    response_model=RuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova regra",
)
@limiter.limit("30/minute")
async def create_rule(
    request: Request,
    rule_data: RuleCreate,
    db: AsyncSession = Depends(get_db),
):
    """Adiciona uma nova regra ao motor de decisão."""
    rule = Rule(
        id=str(uuid.uuid4()),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        **rule_data.model_dump(),
    )
    try:
        db.add(rule)
        await db.commit()
        await db.refresh(rule)
    except IntegrityError as exc:
        await db.rollback()
        logger.warning('"Duplicate rule name rejected", "name": "%s"', rule_data.name)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe uma regra com o nome '{rule_data.name}'.",
        ) from exc
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.error('"Failed to create rule", "error": "%s"', str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar regra.",
        ) from exc

    invalidate_rules_cache()
    logger.info('"Rule created", "id": "%s", "name": "%s"', rule.id, rule.name)
    return rule


@router.patch(
    "/{rule_id}/toggle",
    response_model=RuleResponse,
    summary="Ativar ou desativar uma regra",
)
@limiter.limit("60/minute")
async def toggle_rule(
    request: Request,
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
    try:
        await db.commit()
        await db.refresh(rule)
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.error('"Failed to toggle rule", "rule_id": "%s", "error": "%s"', rule_id, str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar regra.",
        ) from exc

    invalidate_rules_cache()
    logger.info('"Rule toggled", "id": "%s", "is_active": %s', rule.id, rule.is_active)
    return rule


@router.get(
    "/{rule_id}",
    response_model=RuleResponse,
    summary="Obter regra por ID",
)
@limiter.limit("200/minute")
async def get_rule(
    request: Request,
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
