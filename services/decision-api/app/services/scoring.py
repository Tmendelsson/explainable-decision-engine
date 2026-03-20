def calculate_risk_score(penalty: float) -> float:
    """Calcula o score de risco subtraindo a penalidade do score base."""
    score = max(0.0, 100.0 - penalty)
    return round(score, 2)


def determine_decision(
    matched_deny: list[str],
    risk_score: float,
    approve_threshold: float = 70.0,
    manual_review_threshold: float = 50.0,
) -> str:
    """
    Determina a decisão final:
      - Regra eliminatória                  → deny imediato
      - Score < manual_review_threshold     → deny
      - Score < approve_threshold           → manual_review
      - Score >= approve_threshold          → approve
    """
    if matched_deny:
        return "deny"
    if risk_score < manual_review_threshold:
        return "deny"
    if risk_score < approve_threshold:
        return "manual_review"
    return "approve"
