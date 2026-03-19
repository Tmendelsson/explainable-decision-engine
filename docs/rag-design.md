# RAG Design — Knowledge Retrieval Service

## Objetivo

O RAG (Retrieval-Augmented Generation) fornece **contexto institucional** para o LLM raciocinar sobre a decisão. Em vez de depender apenas de regras numéricas, o sistema consulta o "conhecimento corporativo" na forma de políticas, manuais e diretrizes.

---

## Papel no Sistema

```
[Rule Engine] → decisão determinística
      +
[RAG Service] → contexto de políticas relevantes
      =
[LLM Service] → explicação fundamentada e auditável
```

---

## Fontes da Base de Conhecimento

| Arquivo | Tipo | Descrição |
|---------|------|-----------|
| `credit_policy_v1.md` | credit_policy | Política geral de crédito |
| `credit_policy_premium_v2.md` | credit_policy | Política para produtos premium |
| `fraud_signals_guide.md` | compliance | Guia de sinais de fraude |
| `customer_eligibility_policy.md` | product_rules | Elegibilidade por produto |
| `manual_review_checklist.md` | manual | Checklist de revisão humana |

---

## Estrutura de Metadados

Cada chunk indexado terá os seguintes metadados:

```json
{
  "document_id": "uuid",
  "title": "Política de Crédito Premium v2",
  "policy_type": "credit_policy",
  "version": "2",
  "product_type": "credit_card_gold",
  "effective_date": "2026-01-01",
  "source": "credit_policy_premium_v2.md",
  "chunk_index": 3,
  "is_active": true
}
```

---

## Pipeline de Indexação

```
1. Carregar documento (.md ou .txt)
2. Chunking (tamanho: 512 tokens, overlap: 50 tokens)
3. Gerar embeddings (OpenAI text-embedding-3-small ou sentence-transformers)
4. Salvar chunk + embedding + metadados no pgvector
```

---

## Pipeline de Recuperação

```
Query de entrada:
  - produto: credit_card_gold
  - decisão: deny
  - regras acionadas: [LOW_CREDIT_SCORE, INCOME_INCONSISTENCY]

1. Construir query semântica:
   "políticas de elegibilidade para credit_card_gold com score baixo"

2. Filtros de metadados:
   - product_type IN (null, "credit_card_gold")
   - is_active = true

3. Busca vetorial (top-k=5)

4. Retornar: chunk_text, document_title, policy_type, version
```

---

## Estratégia de Consulta

A consulta não é busca semântica pura. Combina:

| Componente | Técnica |
|-----------|---------|
| Relevância semântica | cosine similarity no pgvector |
| Filtros de produto | metadata filtering |
| Filtros de versão ativa | metadata filtering |
| Ranking | score de relevância + prioridade do tipo |

---

## Schema do Banco Vetorial (pgvector)

```sql
CREATE TABLE knowledge_chunks (
    id          UUID PRIMARY KEY,
    document_id UUID NOT NULL,
    title       TEXT NOT NULL,
    policy_type TEXT NOT NULL,
    product_type TEXT,
    version     TEXT NOT NULL,
    source_file TEXT NOT NULL,
    chunk_index INT NOT NULL,
    chunk_text  TEXT NOT NULL,
    embedding   vector(1536),  -- OpenAI ada-002 dimension
    is_active   BOOLEAN DEFAULT true,
    created_at  TIMESTAMP NOT NULL
);

CREATE INDEX ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops);
```

---

## Guardrails

1. **Limite de contexto** — máximo 5 chunks por consulta, cada um com no máximo 512 tokens
2. **Sem inventar critérios** — prompt instrui o LLM a usar apenas o que foi recuperado
3. **Versão auditada** — document_id e version de cada chunk são salvos no audit log
4. **Fallback gracioso** — se RAG retornar vazio, LLM explica com base apenas nas regras acionadas

---

## Evolução Futura (MVP 5)

- Upload de documentos via API
- Reindexação automática por versão
- Dashboard de documentos ativos
- Avaliação de qualidade da recuperação (hit rate, MRR)
