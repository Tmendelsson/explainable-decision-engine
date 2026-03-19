"""
Shared Events — Definição dos eventos de domínio

Todos os eventos trafegam via RabbitMQ (MVP 2+).
Cada serviço publica e/ou consome eventos específicos.

Publicadores e consumidores:
  DecisionRequested     → publicado por: Decision API         | consumido por: Rule Engine, Audit
  EnrichmentCompleted   → publicado por: Enrichment Service   | consumido por: Decision API, Audit
  RulesEvaluated        → publicado por: Rule Engine          | consumido por: RAG, Decision API, Audit
  ContextRetrieved      → publicado por: RAG Service          | consumido por: LLM Reasoning, Audit
  LLMReasoningCompleted → publicado por: LLM Reasoning        | consumido por: Decision API, Audit
  DecisionCompleted     → publicado por: Decision API         | consumido por: Audit
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    transaction_id: str
    correlation_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    service_name: str
    service_version: str = "1.0.0"


class DecisionRequestedEvent(BaseEvent):
    event_type: str = "DecisionRequested"
    service_name: str = "decision-api"
    payload: Dict[str, Any]
    enriched_data: Optional[Dict[str, Any]] = None


class EnrichmentCompletedEvent(BaseEvent):
    event_type: str = "EnrichmentCompleted"
    service_name: str = "enrichment-service"
    credit_score: Optional[int]
    fraud_flags: List[str]
    estimated_income_range: Optional[str]
    profile_risk_indicators: List[str]
    latency_ms: int


class RulesEvaluatedEvent(BaseEvent):
    event_type: str = "RulesEvaluated"
    service_name: str = "rule-engine-service"
    base_decision: str
    risk_score: float
    matched_rules: List[str]
    rules_version_snapshot: List[Dict[str, Any]]


class ContextRetrievedEvent(BaseEvent):
    event_type: str = "ContextRetrieved"
    service_name: str = "rag-service"
    query_used: str
    chunks_retrieved: List[Dict[str, Any]]
    latency_ms: int


class LLMReasoningCompletedEvent(BaseEvent):
    event_type: str = "LLMReasoningCompleted"
    service_name: str = "llm-reasoning-service"
    model_used: str
    prompt_sent: str
    context_used: List[Dict[str, Any]]
    llm_response: Dict[str, Any]
    latency_ms: int


class DecisionCompletedEvent(BaseEvent):
    event_type: str = "DecisionCompleted"
    service_name: str = "decision-api"
    final_decision: str
    risk_score: float
    matched_rules: List[str]
    policy_references: Optional[List[str]] = None
    explanation: Optional[str] = None
    manual_review_recommended: bool = False
