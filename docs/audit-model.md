# Modelo de Auditoria

## Objetivo

O sistema de auditoria garante **rastreabilidade completa e imutável** de cada decisão, incluindo o contexto de IA utilizado. Fundamental para compliance, explicabilidade forense e replay de decisões.

---

## Eventos Auditados

| Evento | Quando | O que contém |
|--------|--------|--------------|
| `DecisionRequested` | Início do fluxo | payload original, correlation_id, timestamp |
| `EnrichmentCompleted` | Após enriquecimento | dados enriquecidos, fonte, latência |
| `RulesEvaluated` | Após motor de regras | regras acionadas, score, decisão base, versão das regras |
| `ContextRetrieved` | Após RAG | chunks recuperados, document_ids, versões, scores de relevância |
| `LLMReasoningCompleted` | Após LLM | prompt enviado, contexto, resposta completa, modelo, latência |
| `DecisionCompleted` | Fim do fluxo | decisão final consolidada, todos os metadados |

---

## Schema de Auditoria

```sql
CREATE TABLE audit_events (
    id              UUID PRIMARY KEY,
    transaction_id  UUID NOT NULL,
    correlation_id  UUID NOT NULL,
    event_type      TEXT NOT NULL,
    payload         JSONB NOT NULL,
    created_at      TIMESTAMP NOT NULL,
    service_name    TEXT NOT NULL,
    service_version TEXT NOT NULL
);

-- Nunca atualizar, nunca deletar
-- INSERT-only table
```

---

## Campos Obrigatórios por Evento

### DecisionRequested
```json
{
  "transaction_id": "uuid",
  "correlation_id": "uuid",
  "cpf_hash": "sha256(cpf)",
  "product": "credit_card",
  "payload_snapshot": { ... }
}
```

### RulesEvaluated
```json
{
  "transaction_id": "uuid",
  "base_decision": "deny",
  "risk_score": 72,
  "matched_rules": ["LOW_CREDIT_SCORE"],
  "rules_version_snapshot": [ { "rule_id": "...", "version": 1 } ]
}
```

### LLMReasoningCompleted
```json
{
  "transaction_id": "uuid",
  "model_used": "gpt-4o-mini",
  "prompt_sent": "...",
  "context_used": [ { "chunk_id": "...", "title": "...", "score": 0.91 } ],
  "llm_response": { "decision_explanation": "...", "confidence_note": "high" },
  "latency_ms": 1240
}
```

---

## Princípios de Imutabilidade

1. A tabela `audit_events` é **insert-only** — sem UPDATE, sem DELETE
2. O `cpf` nunca é armazenado em claro — apenas `sha256(cpf)`
3. Cada evento tem `service_version` para correlacionar com o deploy exato
4. O prompt do LLM é registrado integralmente — incluindo contexto RAG injetado

---

## Consultas Úteis

```sql
-- Trilha completa de uma transação
SELECT event_type, service_name, created_at, payload
FROM audit_events
WHERE transaction_id = 'uuid'
ORDER BY created_at;

-- Todas as decisões de um CPF
SELECT ae.transaction_id, ae.created_at, ae.payload->>'base_decision'
FROM audit_events ae
WHERE ae.payload->>'cpf_hash' = sha256('12345678900')
  AND ae.event_type = 'DecisionCompleted';

-- Decisões com LLM em revisão manual
SELECT *
FROM audit_events
WHERE event_type = 'LLMReasoningCompleted'
  AND payload->>'manual_review_needed' = 'true';
```

---

## Replay de Decisões (MVP 5)

O modelo de auditoria permite **reprocessar** qualquer decisão histórica com:

- Novas versões de regras
- Nova política carregada no RAG
- Novo modelo de LLM

Isso é possível porque cada evento registra a versão exata dos componentes utilizados no momento da decisão original.
