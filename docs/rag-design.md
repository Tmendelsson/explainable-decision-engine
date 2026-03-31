# RAG Design — Knowledge Retrieval Service

## Objetivo

O RAG (Retrieval-Augmented Generation) fornece **contexto institucional e normativo** para a explicação da decisão.

Em vez de depender apenas de score e regras numéricas, o sistema consulta o “conhecimento corporativo” da plataforma, incluindo:

- políticas de crédito
- critérios de elegibilidade
- diretrizes de revisão manual
- sinais de fraude
- manuais operacionais

---

## Papel no Sistema

```text
[Rule Engine] → decisão determinística
      +
[RAG Service] → contexto institucional relevante
      =
[LLM Service] → explicação fundamentada, contextualizada e auditável
```

---

## Princípio Fundamental

> O RAG **não decide**.  
> Ele apenas fornece **base contextual** para que a explicação gerada seja mais precisa, útil e auditável.

---

## Fontes da Base de Conhecimento

| Arquivo | Tipo | Descrição |
|---------|------|-----------|
| `credit_policy_v1.md` | credit_policy | Política geral de crédito |
| `credit_policy_premium_v2.md` | credit_policy | Política para produtos premium |
| `fraud_signals_guide.md` | compliance | Guia de sinais de inconsistência e fraude |
| `customer_eligibility_policy.md` | product_rules | Elegibilidade por produto |
| `manual_review_checklist.md` | manual | Checklist de revisão humana |

---

## Estrutura de Metadados

Cada chunk indexado possui metadados para permitir filtragem contextual e auditável.

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

```text
1. Carregar documento (.md ou .txt)
2. Fazer chunking
3. Gerar embeddings
4. Salvar chunk + embedding + metadados no pgvector
```

### Estratégia inicial
- tamanho do chunk: `~512 tokens`
- overlap: `~50 tokens`

---

## Pipeline de Recuperação

### Exemplo de contexto de entrada
- produto: `credit_card_gold`
- decisão: `deny`
- regras acionadas:
  - `LOW_CREDIT_SCORE`
  - `INCOME_INCONSISTENCY`

### Fluxo de recuperação

```text
1. Construir query semântica
   Ex:
   "políticas de elegibilidade para credit_card_gold com score baixo e inconsistência de renda"

2. Aplicar filtros de metadados:
   - product_type IN (null, "credit_card_gold")
   - is_active = true

3. Executar busca vetorial (top-k=5)

4. Retornar:
   - chunk_text
   - document_title
   - policy_type
   - version
```

---

## Estratégia de Consulta

A recuperação combina:

| Componente | Técnica |
|-----------|---------|
| Relevância semântica | cosine similarity no pgvector |
| Filtro por produto | metadata filtering |
| Filtro por versão ativa | metadata filtering |
| Priorização | score semântico + prioridade do tipo |

---

## Schema do Banco Vetorial

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
    embedding   vector(1536),
    is_active   BOOLEAN DEFAULT true,
    created_at  TIMESTAMP NOT NULL
);

CREATE INDEX ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops);
```

---

## Guardrails

1. **Limite de contexto**  
   Máximo de 5 chunks por consulta

2. **Sem inventar critérios**  
   O LLM só pode explicar com base:
   - nas regras acionadas
   - no contexto recuperado

3. **Versão auditada**  
   Cada chunk usado é registrado no audit log

4. **Fallback gracioso**  
   Se não houver contexto relevante, o sistema explica apenas com base nas regras acionadas

---

## Valor de Produto

O RAG aumenta a qualidade da explicação porque permite:

- associar a decisão a políticas reais
- justificar melhor revisão manual
- apoiar o trabalho de analistas
- enriquecer a trilha auditável

---

## Evolução Futura (MVP 5)

- upload de documentos via API
- reindexação automática
- dashboard de documentos ativos
- versionamento de políticas
- avaliação de qualidade da recuperação:
  - hit rate
  - MRR
  - cobertura por produto