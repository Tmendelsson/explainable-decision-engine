"""
Evaluator — Rule Engine Service MVP 2

Lógica de avaliação de regras e cálculo de score.
Espelho deliberado de decision-api para isolamento de serviço.
MVP 3+: esta versão se torna a fonte canônica; decision-api herda via shared lib.
"""
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)

OPERATORS: dict[str, Callable[[float, float], bool]] = {
    "lt": lambda a, b: a < b,
    "gt": lambda a, b: a > b,
    "lte": lambda a, b: a <= b,
    "gte": lambda a, b: a >= b,
    "eq": lambda a, b: a == b,
}


def evaluate_rules(
    payload: dict[str, Any], rules: list
) -> tuple[list[str], list[str], float]:
    """
    Avalia as regras ativas contra o payload enriquecido.

    Returns:
        matched_deny  — nomes de regras eliminatórias acionadas
        matched_flag  — nomes de regras de penalidade acionadas
        total_penalty — soma dos pesos das penalidades
    """
    matched_deny: list[str] = []
    matched_flag: list[str] = []
    total_penalty: float = 0.0

    sorted_rules = sorted(rules, key=lambda r: r.priority, reverse=True)

    for rule in sorted_rules:
        field_value = payload.get(rule.field)
        if field_value is None:
            continue

        operator_fn = OPERATORS.get(rule.operator)
        if operator_fn is None:
            logger.warning("Skipping rule %s: unknown operator %s", rule.name, rule.operator)
            continue

        try:
            if operator_fn(float(field_value), float(rule.value)):
                if rule.action == "deny":
                    matched_deny.append(rule.name)
                else:
                    matched_flag.append(rule.name)
                    total_penalty += rule.weight
        except (TypeError, ValueError) as exc:
            logger.warning("Type error evaluating rule %s: %s", rule.name, exc)

    return matched_deny, matched_flag, total_penalty


def calculate_risk_score(penalty: float) -> float:
    return round(max(0.0, 100.0 - penalty), 2)


def determine_decision(
    matched_deny: list[str],
    risk_score: float,
    approve_threshold: float = 70.0,
    manual_review_threshold: float = 50.0,
) -> str:
    if matched_deny:
        return "deny"
    if risk_score < manual_review_threshold:
        return "deny"
    if risk_score < approve_threshold:
        return "manual_review"
    return "approve"
