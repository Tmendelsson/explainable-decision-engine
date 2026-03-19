"""
RAG Service (Knowledge Retrieval) — MVP 4

Responsável por indexar e recuperar contexto da base de conhecimento.

Responsabilidades:
  - Indexar documentos de políticas (knowledge-base/)
  - Gerar embeddings (OpenAI ou sentence-transformers)
  - Armazenar chunks + embeddings no pgvector
  - Recuperar trechos relevantes usando busca semântica + filtros de metadados
  - Devolver contexto para o LLM Reasoning Service

Fontes indexadas:
  - knowledge-base/policies/
  - knowledge-base/compliance/
  - knowledge-base/product-rules/
  - knowledge-base/manuals/
"""
from fastapi import FastAPI

app = FastAPI(
    title="RAG Service",
    description="Knowledge Retrieval Service — MVP 4. RAG com pgvector.",
    version="0.0.1",
)


@app.get("/health", tags=["infra"])
async def health():
    return {"status": "healthy", "service": "rag-service", "mvp": 4}


# TODO (MVP 4):
# @app.post("/index")
# async def index_document(file_path: str): ...
#
# @app.post("/retrieve")
# async def retrieve_context(request: RetrievalRequest) -> RetrievalResponse:
#     Retorna os top-k chunks mais relevantes com metadados
