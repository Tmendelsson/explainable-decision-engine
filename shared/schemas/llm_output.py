"""
LLM Output Schema — Contrato de saída do LLM Reasoning Service (MVP 4)

A resposta do LLM SEMPRE deve ser validada contra este schema.
O LLM nunca altera a decisão base — apenas explica e apoia.
"""
from typing import Literal, Optional

from pydantic import BaseModel, Field


class LLMReasoningOutput(BaseModel):
    """Schema validado para saída do LLM. Prompts devem instruir este formato."""

    decision_explanation: str = Field(
        ...,
        description="Explicação da decisão em linguagem de negócio",
    )
    policy_summary: str = Field(
        ...,
        description="Resumo das políticas que fundamentam a decisão",
    )
    manual_review_needed: bool = Field(
        ...,
        description="True se o LLM identificou ambiguidade que merece revisão",
    )
    confidence_note: Literal["high", "medium", "low"] = Field(
        ...,
        description="Nível de confiança do LLM na explicação gerada",
    )
    analyst_note: Optional[str] = Field(
        None,
        description="Nota adicional para o analista em casos de revisão manual",
    )
