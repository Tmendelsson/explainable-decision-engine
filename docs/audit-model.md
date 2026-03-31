# Modelo de Auditoria — Explainable Credit Decision Engine

## Objetivo

O sistema de auditoria garante **rastreabilidade completa, imutável e reprocessável** de cada decisão.

Ele foi projetado para suportar cenários com necessidade de:

- compliance
- explicabilidade forense
- investigação operacional
- replay de decisões
- revisão de regras e políticas

Esse componente é especialmente importante em domínios como:

- crédito
- elegibilidade financeira
- revisão manual
- prevenção de inconsistências e fraude

---

## Princípios do Modelo de Auditoria

1. **Toda decisão deve ser reconstituível**
2. **Toda entrada relevante deve ser rastreável**
3. **A decisão deve ser explicável tecnicamente e operacionalmente**
4. **A IA deve ser auditável, incluindo contexto e prompt**
5. **Nenhum evento auditável pode ser alterado ou apagado**

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

-- INSERT-only table
-- Nunca atualizar, nunca deletar
```

---

## Estrutura Esperada por Evento

### 1. DecisionRequested

```json
{
  "transaction_id": "uuid",
  "correlation_id": "uuid",
  "cpf_hash": "sha256(cpf)",
  "product": "credit_card",
  "payload_snapshot": {
    "monthly_income": 5000,
    "age": 30,
    "credit_score": 650
  }
}
```

---

### 2. EnrichmentCompleted

```json
{
  "transaction_id": "uuid",
  "credit_score_source": "mock_bureau_v1",
  "fraud_flags": [],
  "attempt_count_last_30d": 1,
  "profile_risk_indicators": {
    "income_consistency": "ok",
    "application_velocity": "normal"
  },
  "latency_ms": 180
}
```

---

### 3. RulesEvaluated

```json
{
  "transaction_id": "uuid",
  "base_decision": "deny",
  "risk_score": 72,
  "matched_rules": ["LOW_CREDIT_SCORE"],
  "manual_review_recommended": false,
  "rules_version_snapshot": [
    { "rule_id": "uuid", "version": 1 }
  ]
}
```

---

### 4. ContextRetrieved

```json
{
  "transaction_id": "uuid",
  "retrieved_chunks": [
    {
      "chunk_id": "uuid",
      "title": "Política de Crédito Premium v2",
      "version": "2",
      "score": 0.91
    }
  ]
}
```

---

### 5. LLMReasoningCompleted

```json
{
  "transaction_id": "uuid",
  "model_used": "gpt-4o-mini",
  "prompt_sent": "...",
  "context_used": [
    {
      "chunk_id": "uuid",
      "title": "Política de Crédito Premium v2",
      "score": 0.91
    }
  ],
  "llm_response": {
    "decision_explanation": "...",
    "confidence_note": "high"
  },
  "latency_ms": 1240
}
```

---

### 6. DecisionCompleted

```json
{
  "transaction_id": "uuid",
  "final_decision": "deny",
  "risk_score": 72,
  "matched_rules": ["LOW_CREDIT_SCORE"],
  "policy_references": ["credit_policy_premium_v2"],
  "manual_review_recommended": false
}
```

---

## Regras de Segurança e Privacidade

### Dados sensíveis
- `cpf` **nunca** deve ser armazenado em claro
- apenas `sha256(cpf)` deve ser persistido em auditoria
- dados sensíveis devem ser mascarados ou minimizados sempre que possível

### IA auditável
- o prompt do LLM deve ser registrado integralmente
- o contexto recuperado pelo RAG deve ser persistido
- a versão do modelo utilizado deve ser registrada

---

## Consultas Úteis

```sql
-- Trilha completa de uma transação
SELECT event_type, service_name, created_at, payload
FROM audit_events
WHERE transaction_id = 'uuid'
ORDER BY created_at;

-- Todas as decisões de um CPF
SELECT ae.transaction_id, ae.created_at, ae.payload->>'final_decision'
FROM audit_events ae
WHERE ae.payload->>'cpf_hash' = sha256('12345678900')
  AND ae.event_type = 'DecisionCompleted';

-- Decisões encaminhadas para revisão manual
SELECT *
FROM audit_events
WHERE event_type = 'DecisionCompleted'
  AND payload->>'manual_review_recommended' = 'true';
```

---

## Replay de Decisões (MVP 5)

O modelo de auditoria foi desenhado para permitir **reprocessamento histórico**.

Isso permite simular uma decisão antiga com:

- novas regras
- nova política de crédito
- novo contexto institucional
- novo modelo de LLM

Esse replay é possível porque cada evento registra:

- versão das regras
- versão dos documentos
- versão do serviço
- versão do modelo utilizado

---

## Valor Arquitetural

Esse modelo de auditoria demonstra domínio em:

- rastreabilidade enterprise
- explicabilidade de sistemas críticos
- observabilidade de negócio
- segurança de dados
- design para ambientes regulados