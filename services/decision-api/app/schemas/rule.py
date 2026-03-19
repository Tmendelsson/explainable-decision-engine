from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RuleCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str
    field: str = Field(..., description="Campo do payload: monthly_income | age | credit_score")
    operator: str = Field(..., description="Operador: lt | gt | lte | gte | eq")
    value: float = Field(..., description="Valor de referência para comparação")
    action: str = Field(..., description="Ação: deny | manual_review | flag")
    weight: float = Field(default=10.0, ge=0, le=100, description="Penalidade no score (0–100)")
    priority: int = Field(default=0, ge=0, description="Ordem de avaliação (maior = primeiro)")
    is_active: bool = True
    product_type: Optional[str] = Field(None, description="Produto alvo. None = global")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "LOW_INCOME",
                "description": "Renda mensal abaixo do mínimo exigido",
                "field": "monthly_income",
                "operator": "lt",
                "value": 1500.0,
                "action": "deny",
                "weight": 50.0,
                "priority": 9,
                "is_active": True,
                "product_type": None,
            }
        }
    }


class RuleResponse(BaseModel):
    id: str
    name: str
    description: str
    field: str
    operator: str
    value: float
    action: str
    weight: float
    priority: int
    is_active: bool
    product_type: Optional[str]
    version: int
    created_at: datetime

    model_config = {"from_attributes": True}
