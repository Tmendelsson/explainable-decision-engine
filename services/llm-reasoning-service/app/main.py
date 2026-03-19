"""
LLM Reasoning Service — MVP 4

Usa o contexto recuperado pelo RAG + resultado do motor de regras
para gerar explicações auditáveis.

Responsabilidades:
  - Montar prompt com: decisão, score, regras acionadas, contexto RAG
  - Chamar LLM (OpenAI / Ollama)
  - Validar resposta por schema JSON
  - Publicar evento LLMReasoningCompleted

Saída sempre em JSON estruturado:
  {
    "decision_explanation": "...",
    "policy_summary": "...",
    "manual_review_needed": false,
    "confidence_note": "high"
  }

GUARDRAILS:
  - O LLM NUNCA altera a decisão base
  - Prompt instrui a não inventar critérios
  - Resposta validada por Pydantic antes de publicar
  - Prompt + contexto + resposta auditados integralmente
"""
from fastapi import FastAPI

app = FastAPI(
    title="LLM Reasoning Service",
    description="LLM Reasoning Service — MVP 4. Explicabilidade com guardrails.",
    version="0.0.1",
)


@app.get("/health", tags=["infra"])
async def health():
    return {"status": "healthy", "service": "llm-reasoning-service", "mvp": 4}


# TODO (MVP 4):
# @app.post("/reason")
# async def generate_explanation(request: ReasoningRequest) -> ReasoningResponse:
#     Recebe decisão + contexto RAG → retorna explicação estruturada
