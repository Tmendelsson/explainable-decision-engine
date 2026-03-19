from fastapi import HTTPException, status


class DecisionNotFoundError(HTTPException):
    def __init__(self, transaction_id: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decisão com transaction_id '{transaction_id}' não encontrada.",
        )


class RuleNotFoundError(HTTPException):
    def __init__(self, rule_id: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Regra '{rule_id}' não encontrada.",
        )


class InvalidRuleOperatorError(HTTPException):
    def __init__(self, operator: str) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Operador inválido: '{operator}'. Use: lt, gt, lte, gte, eq.",
        )
