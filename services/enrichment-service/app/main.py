"""
Enrichment Service — MVP 2

Responsável por enriquecer o perfil do solicitante com dados externos simulados:
  - score de crédito
  - histórico de tentativas
  - flags de fraude
  - perfil transacional
  - inconsistências cadastrais

No MVP 2 os dados são simulados. No MVP 5 podem ser integrados a bureaus externos.
"""
from fastapi import FastAPI

app = FastAPI(
    title="Enrichment Service",
    description="Data Enrichment Service — MVP 2. Enriquece perfis com sinais externos.",
    version="0.0.1",
)


@app.get("/health", tags=["infra"])
async def health():
    return {"status": "healthy", "service": "enrichment-service", "mvp": 2}


# TODO (MVP 2):
# @app.post("/enrich")
# async def enrich_profile(request: EnrichmentRequest) -> EnrichmentResponse:
#     Retorna dados enriquecidos para o orchestrator
