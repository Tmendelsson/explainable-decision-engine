from typing import Callable

# Mapeamento de operadores para funções comparadoras
OPERATORS: dict[str, Callable[[float, float], bool]] = {
    "lt": lambda a, b: a < b,
    "gt": lambda a, b: a > b,
    "lte": lambda a, b: a <= b,
    "gte": lambda a, b: a >= b,
    "eq": lambda a, b: a == b,
}


def evaluate_rules(
    payload: dict, rules: list
) -> tuple[list[str], list[str], float]:
    """
    Avalia as regras ativas contra o payload da solicitação.

    Retorna:
        matched_deny  — regras eliminatórias acionadas
        matched_flag  — regras de penalidade acionadas
        total_penalty — soma dos pesos das regras de penalidade
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
            continue

        try:
            if operator_fn(float(field_value), float(rule.value)):
                if rule.action == "deny":
                    matched_deny.append(rule.name)
                else:
                    matched_flag.append(rule.name)
                    total_penalty += rule.weight
        except (TypeError, ValueError):
            continue

    return matched_deny, matched_flag, total_penalty
