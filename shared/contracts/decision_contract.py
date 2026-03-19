"""
Shared Contracts — DecisionRequest / DecisionResponse

Contratos compartilhados entre serviços via eventos e APIs internas.
Utilizados a partir do MVP 2 para comunicação entre microserviços.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DecisionRequestContract(BaseModel):
    """
    Contrato de entrada para o fluxo de decisão.
    Publicado como evento DecisionRequested no RabbitMQ (MVP 2).
    """
    transaction_id: str
    correlation_id: str
    cpf: str
    product: str
    monthly_income: float
    age: int
    credit_score: Optional[int] = None
    enriched_data: Optional[Dict[str, Any]] = None
    requested_at: datetime = Field(default_factory=datetime.utcnow)


class DecisionResponseContract(BaseModel):
    """
    Contrato de saída após avaliação completa.
    Publicado como evento DecisionCompleted no RabbitMQ (MVP 2).
    """
    transaction_id: str
    correlation_id: str
    decision: str
    risk_score: float
    matched_rules: List[str]
    policy_references: Optional[List[str]] = None
    explanation: Optional[str] = None
    manual_review_recommended: bool = False
    completed_at: datetime = Field(default_factory=datetime.utcnow)
