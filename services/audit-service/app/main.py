"""
Audit Service — MVP 3

Responsável pela persistência imutável de todos os eventos do sistema.

Responsabilidades:
  - Escutar: DecisionRequested, EnrichmentCompleted, RulesEvaluated,
             ContextRetrieved, LLMReasoningCompleted, DecisionCompleted
  - Persistir cada evento de forma INSERT-ONLY (sem UPDATE, sem DELETE)
  - Garantir rastreabilidade completa por transaction_id
  - Incluir: prompt enviado ao LLM, contexto RAG, versão dos componentes

O audit service é OBRIGATÓRIO antes de ativar o LLM (MVP 4).
"""
from fastapi import FastAPI

app = FastAPI(
    title="Audit Service",
    description="Audit Service — MVP 3. Persistência imutável de eventos.",
    version="0.0.1",
)


@app.get("/health", tags=["infra"])
async def health():
    return {"status": "healthy", "service": "audit-service", "mvp": 3}


# TODO (MVP 3):
# @app.get("/audit/{transaction_id}")
# async def get_audit_trail(transaction_id: str):
#     Retorna todos os eventos de uma transação em ordem cronológica
