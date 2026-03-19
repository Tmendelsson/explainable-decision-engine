# Fluxo de Sequência — Explainable Decision Engine

## MVP 1 — Fluxo Síncrono

```
Cliente          Decision API         PostgreSQL
  |                   |                    |
  |--- POST /decisions/-->|               |
  |                   |                    |
  |                   |-- valida payload   |
  |                   |-- gera transaction_id
  |                   |                    |
  |                   |-- SELECT rules --->|
  |                   |<-- rules ----------|
  |                   |                    |
  |                   |-- avalia regras    |
  |                   |-- calcula score    |
  |                   |-- determina decisão|
  |                   |                    |
  |                   |-- INSERT decision->|
  |                   |<-- decision -------|
  |                   |                    |
  |<-- 201 response --|                    |
```

---

## MVP 2 — Fluxo com Microserviços e RabbitMQ

```
Cliente    Decision API    Enrichment    RabbitMQ    Rule Engine
  |             |               |             |           |
  |--POST ------>|               |             |           |
  |             |-- GET enrich ->|             |           |
  |             |<-- data -------|             |           |
  |             |                             |           |
  |             |-- publish DecisionRequested->|          |
  |             |                             |--consume->|
  |             |                             |           |-- avalia
  |             |                             |           |-- calcula
  |             |                             |<- publish DecisionEvaluated
  |             |<-- consume DecisionEvaluated|           |
  |             |-- consolida resultado        |           |
  |             |                             |           |
  |<-- 200 ------|                             |           |
```

---

## MVP 4 — Fluxo com RAG + LLM

```
Decision API   Rule Engine   RAG Service   LLM Service   Audit Service
     |               |            |              |              |
     |-- DecisionRequested ------> (RabbitMQ)
     |               |            |              |              |
     |               |-- avalia   |              |              |
     |               |-- score    |              |              |
     |               |-- decide   |              |              |
     |               |-- publish RulesEvaluated             |              |
     |                            |              |              |
     |                            |<-- contexto  |              |
     |                            |   da decisão |              |
     |                            |-- busca semântica          |
     |                            |-- filtra metadados         |
     |                            |-- retorna chunks           |
     |                                           |              |
     |                                           |<-- chunks    |
     |                                           |-- monta prompt
     |                                           |-- chama LLM  |
     |                                           |-- valida JSON |
     |                                           |-- publish LLMCompleted
     |                                                          |
     |<-- consolida resultado -------------------------        |
     |                                                          |
     |-- publish DecisionCompleted -----------------------------> (escuta)
     |                                                          |-- INSERT imutável
```

---

## Identidade de Rastreio

Cada requisição carrega dois identificadores propagados em todos os serviços:

| Campo | Gerado por | Escopo |
|-------|-----------|--------|
| `transaction_id` | Decision API | Único por solicitação de crédito |
| `correlation_id` | API Gateway / Orchestrator | Propaga em headers e mensagens |

Esses IDs permitem rastrear toda a jornada de uma decisão em logs distribuídos e na tabela de auditoria.
