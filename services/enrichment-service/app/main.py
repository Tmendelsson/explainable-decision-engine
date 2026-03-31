"""
Enrichment Service — MVP 2

Responsável por enriquecer o perfil do solicitante com dados externos simulados:
  - score de crédito
  - flags de fraude
  - faixa de renda estimada
  - indicadores de risco de perfil
  - inconsistência de renda declarada

No MVP 2 os dados são simulados deterministicamente.
No MVP 5 podem ser integrados a bureaus externos (Serasa, SPC, etc.).
"""
import logging

from fastapi import FastAPI

from app.schemas.enrich import EnrichmentRequest, EnrichmentResponse
from app.services.simulator import (
    has_income_inconsistency,
    simulate_credit_score,
    simulate_fraud_flags,
    simulate_income_range,
    simulate_profile_risk_indicators,
)

logger = logging.getLogger(__name__)


app = FastAPI(
    title="Enrichment Service",
    description="Data Enrichment Service — MVP 2. Enriquece perfis com sinais externos simulados.",
    version="0.2.0",
)


@app.get("/health", tags=["infra"])
async def health():
    return {"status": "healthy", "service": "enrichment-service", "version": "0.2.0"}


@app.post("/enrich", response_model=EnrichmentResponse, tags=["enrichment"])
async def enrich_profile(request: EnrichmentRequest) -> EnrichmentResponse:
    """
    Enriquece o perfil do solicitante com dados externos simulados.

    Chamado sincronamente pelo decision-api antes de publicar o evento
    DecisionRequested no RabbitMQ.
    """
    logger.info(
        "Enriching profile transaction_id=%s product=%s",
        request.transaction_id,
        request.product,
    )

    credit_score = simulate_credit_score(request.monthly_income, request.age)
    fraud_flags = simulate_fraud_flags(request.cpf, request.monthly_income)
    income_range = simulate_income_range(request.monthly_income)
    risk_indicators = simulate_profile_risk_indicators(
        request.monthly_income, credit_score, fraud_flags
    )
    inconsistency = has_income_inconsistency(request.monthly_income, income_range)

    logger.info(
        "Enrichment complete transaction_id=%s credit_score=%d flags=%s",
        request.transaction_id,
        credit_score,
        fraud_flags,
    )

    return EnrichmentResponse(
        transaction_id=request.transaction_id,
        correlation_id=request.correlation_id,
        credit_score=credit_score,
        fraud_flags=fraud_flags,
        estimated_income_range=income_range,
        profile_risk_indicators=risk_indicators,
        income_inconsistency=inconsistency,
    )
