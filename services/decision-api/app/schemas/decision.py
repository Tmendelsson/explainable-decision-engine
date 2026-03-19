from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DecisionRequest(BaseModel):
    cpf: str = Field(..., min_length=11, max_length=14, description="CPF do solicitante")
    product: str = Field(..., description="Produto solicitado (ex: credit_card, personal_loan)")
    monthly_income: float = Field(..., gt=0, description="Renda mensal em R$")
    age: int = Field(..., gt=0, lt=120, description="Idade do solicitante")
    credit_score: Optional[int] = Field(None, ge=0, le=1000, description="Score de crédito (0–1000)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "cpf": "123.456.789-00",
                "product": "credit_card",
                "monthly_income": 5000.0,
                "age": 30,
                "credit_score": 650,
            }
        }
    }


class DecisionResponse(BaseModel):
    transaction_id: str
    status: str
    decision: str
    risk_score: float
    matched_rules: List[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class DecisionDetailResponse(DecisionResponse):
    cpf: str
    product: str
    monthly_income: float
    age: int
    credit_score: Optional[int]
