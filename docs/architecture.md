# Arquitetura — Explainable Decision Engine

## Visão Macro

O sistema é composto por **7 serviços** organizados em camadas:

```
[Cliente] → [API Gateway] → [Decision API / Orchestrator]
                                    ↓              ↓
                          [Enrichment]        [PostgreSQL]
                                    ↓
                              [RabbitMQ]
                             ↙          ↘
                  [Rule Engine]        [Audit Service]
                        ↓
               [RAG Service] (pgvector)
                        ↓
            [LLM Reasoning Service]
                        ↓
           [Final Decision Composer]
```

---

## Serviços

### 1. API Gateway
- Nginx ou Traefik
- Responsável por: autenticação, rate limiting, roteamento, propagação de `correlation_id`

### 2. Decision API / Orchestrator
- **Coração do sistema**
- Recebe a requisição, gera `transaction_id`, coordena todo o fluxo
- Não decide sozinho — **orquestra**
- Persiste o estado inicial e o resultado final

### 3. Data Enrichment Service
- Enriquece o perfil com sinais externos:
  - score de crédito
  - histórico de tentativas
  - flags de fraude
  - consistência cadastral
- Fornece dados "frios" e objetivos para o motor

### 4. Rule Engine Service
- **Decisor determinístico principal**
- Carrega regras ativas do banco
- Aplica regras eliminatórias e calcula score de risco
- Emite: `base_decision`, `risk_score`, `matched_rules`

### 5. RAG / Knowledge Retrieval Service
- Indexa documentos de políticas e critérios
- Gera e armazena embeddings no pgvector
- Consulta por similaridade semântica + filtros de metadados
- Retorna trechos relevantes para o contexto de raciocínio

### 6. LLM Reasoning Service
- Recebe: resultado do motor + contexto do RAG
- Gera: explicação estruturada, resumo para analista, recomendação de revisão
- **Saída sempre em JSON validado — nunca altera a decisão base**

### 7. Audit Service
- Escuta eventos via RabbitMQ
- Persiste de forma imutável: input, enriched data, decisão, prompt, resposta do LLM, versões
- Fundamental para compliance e explicabilidade forense

---

## Fluxo de Dados

```
POST /decisions/credit-card
        ↓
  [Orchestrator]
  - valida payload
  - gera transaction_id + correlation_id
  - persiste estado inicial
        ↓
  [Enrichment Service]
  - credit_score
  - fraud_flags
  - profile_risk_indicators
        ↓
  publica DecisionRequested → [RabbitMQ]
        ↓
  [Rule Engine]
  - aplica regras eliminatórias
  - calcula score
  - base_decision = deny | approve | manual_review
        ↓
  [RAG Service]
  - query semântica com contexto da decisão
  - filtra por: produto, tipo de política, versão ativa
        ↓
  [LLM Reasoning]
  - recebe: decisão + score + regras + contexto RAG
  - gera: explanation, summary, manual_review_note
        ↓
  [Orchestrator]
  - consolida resposta final
  - publica DecisionCompleted → [Audit Service]
        ↓
  Retorna resposta ao cliente
```

---

## Decisão Final — Estrutura

```json
{
  "transaction_id": "uuid",
  "status": "completed",
  "decision": "deny",
  "risk_score": 72,
  "matched_rules": ["LOW_CREDIT_SCORE", "INCOME_INCONSISTENCY"],
  "policy_references": ["credit_policy_premium_v2", "fraud_signals_guide"],
  "explanation": "A solicitação foi negada devido ao score abaixo do mínimo e inconsistência de renda.",
  "manual_review_recommended": false,
  "created_at": "2026-03-19T17:00:00Z"
}
```

---

## Separação de Responsabilidades

| Camada | Quem faz | O que faz |
|--------|----------|-----------|
| Determinística | Rule Engine | **Decide** com regras objetivas |
| Contextual | RAG Service | **Contextualiza** com políticas institucionais |
| Explicativa | LLM Service | **Explica** e apoia revisão humana |
| Rastreável | Audit Service | **Registra** tudo permanentemente |

> A decisão **sempre** vem do motor de regras. O LLM nunca altera a decisão.
