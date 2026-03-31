from typing import List, Optional
from pydantic import BaseModel, Field


class EnrichmentRequest(BaseModel):
    transaction_id: str
    correlation_id: str
    cpf: str
    product: str
    monthly_income: float
    age: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "transaction_id": "uuid-here",
                "correlation_id": "uuid-here",
                "cpf": "123.456.789-00",
                "product": "credit_card",
                "monthly_income": 5000.0,
                "age": 30,
            }
        }
    }


class EnrichmentResponse(BaseModel):
    transaction_id: str
    correlation_id: str
    credit_score: Optional[int] = Field(None, description="Score de crédito externo (0–1000)")
    fraud_flags: List[str] = Field(default_factory=list, description="Sinais de fraude identificados")
    estimated_income_range: Optional[str] = Field(None, description="Faixa estimada de renda")
    profile_risk_indicators: List[str] = Field(default_factory=list, description="Indicadores de risco do perfil")
    income_inconsistency: bool = Field(False, description="True se renda declarada difere >40% da estimada")
