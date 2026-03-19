import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.decision import Decision
from app.models.rule import Rule
from app.schemas.decision import DecisionRequest
from app.services.rule_engine import evaluate_rules
from app.services.scoring import calculate_risk_score, determine_decision


async def process_decision(request: DecisionRequest, db: AsyncSession) -> Decision:
    """
    Processa uma solicitação de decisão:
      1. Carrega regras ativas do banco
      2. Filtra por produto ou global
      3. Avalia regras contra o payload
      4. Calcula score e determina decisão
      5. Persiste e retorna o resultado
    """
    result = await db.execute(select(Rule).where(Rule.is_active == True))
    all_rules = result.scalars().all()

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
    final_decision = determine_decision(matched_deny, risk_score)
    all_matched = matched_deny + matched_flag

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

    db.add(decision)
    await db.commit()
    await db.refresh(decision)

    return decision


async def get_decision_by_transaction(
    transaction_id: str, db: AsyncSession
) -> Decision | None:
    result = await db.execute(
        select(Decision).where(Decision.transaction_id == transaction_id)
    )
    return result.scalar_one_or_none()
