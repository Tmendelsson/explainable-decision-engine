"""
Rule Engine Service — MVP 2

No MVP 2, a lógica de avaliação de regras é extraída do decision-api
e passa a rodar como serviço independente, consumindo eventos do RabbitMQ.

Responsabilidades:
  - Consumir evento DecisionRequested
  - Carregar regras ativas do banco
  - Aplicar regras eliminatórias
  - Calcular score de risco
  - Publicar evento RulesEvaluated
"""
from fastapi import FastAPI

app = FastAPI(
    title="Rule Engine Service",
    description="Rule Engine Service — MVP 2. Decisor determinístico via eventos.",
    version="0.0.1",
)


@app.get("/health", tags=["infra"])
async def health():
    return {"status": "healthy", "service": "rule-engine-service", "mvp": 2}


# TODO (MVP 2):
# Inicializar consumer do RabbitMQ no lifespan
# handler: consume DecisionRequested → evaluate → publish RulesEvaluated
