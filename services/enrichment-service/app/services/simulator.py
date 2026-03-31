"""
Simulador de dados externos.

Em produção, cada função seria uma chamada a um bureau externo
(Serasa, SPC, sistema interno de fraude, etc.).
No MVP 2, os dados são determinísticos com base no perfil para
garantir resultados previsíveis em testes e demos.
"""
from typing import Optional


def simulate_credit_score(monthly_income: float, age: int) -> int:
    """
    Simula score de crédito externo (0–1000).
    Lógica determinística baseada em renda e idade para reprodutibilidade.
    """
    base = 500

    if monthly_income >= 10_000:
        base += 200
    elif monthly_income >= 5_000:
        base += 100
    elif monthly_income >= 3_000:
        base += 50
    elif monthly_income < 1_500:
        base -= 150

    if age >= 40:
        base += 50
    elif age >= 25:
        base += 20
    elif age < 21:
        base -= 80

    return max(0, min(1000, base))


def simulate_fraud_flags(cpf: str, monthly_income: float) -> list[str]:
    """
    Simula flags de fraude com base em padrões do CPF e renda.
    CPFs terminados em 9 simulam perfil suspeito para fins de demo.
    """
    flags: list[str] = []
    cpf_digits = cpf.replace(".", "").replace("-", "").replace(" ", "")

    if cpf_digits.endswith("9"):
        flags.append("VELOCITY_HIGH")

    if monthly_income > 50_000:
        flags.append("OUT_OF_PROFILE")

    return flags


def simulate_income_range(monthly_income: float) -> str:
    """Retorna a faixa de renda estimada por modelos internos."""
    if monthly_income < 2_000:
        return "1000-2000"
    if monthly_income < 4_000:
        return "2000-4000"
    if monthly_income < 7_000:
        return "4000-7000"
    if monthly_income < 12_000:
        return "7000-12000"
    return "12000+"


def simulate_profile_risk_indicators(
    monthly_income: float, credit_score: int, fraud_flags: list[str]
) -> list[str]:
    """Indicadores adicionais de risco baseados no perfil combinado."""
    indicators: list[str] = []

    if credit_score < 500:
        indicators.append("POOR_CREDIT_HISTORY")

    if monthly_income < 2_000 and credit_score < 600:
        indicators.append("HIGH_FINANCIAL_VULNERABILITY")

    if fraud_flags:
        indicators.append("FRAUD_SIGNAL_DETECTED")

    return indicators


def has_income_inconsistency(declared_income: float, range_str: str) -> bool:
    """
    Verifica se a renda declarada está fora da faixa estimada por >40%.
    """
    try:
        parts = range_str.split("-")
        low = float(parts[0])
        high = float(parts[1]) if len(parts) > 1 else float(parts[0]) * 1.5
        mid = (low + high) / 2
        deviation = abs(declared_income - mid) / mid
        return deviation > 0.40
    except (ValueError, ZeroDivisionError, IndexError):
        return False
