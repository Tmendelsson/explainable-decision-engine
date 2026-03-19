BASE_SCORE = 100.0

APPROVE_THRESHOLD = 70.0
MANUAL_REVIEW_THRESHOLD = 50.0


def calculate_risk_score(penalty: float) -> float:
    """Calcula o score de risco subtraindo a penalidade do score base."""
    score = max(0.0, BASE_SCORE - penalty)
    return round(score, 2)


def determine_decision(matched_deny: list[str], risk_score: float) -> str:
    """
    Determina a decisão final:
      - Regra eliminatória → deny imediato
      - Score < 50  → deny
      - Score 50-69 → manual_review
      - Score >= 70 → approve
    """
    if matched_deny:
        return "deny"
    if risk_score < MANUAL_REVIEW_THRESHOLD:
        return "deny"
    if risk_score < APPROVE_THRESHOLD:
        return "manual_review"
    return "approve"
