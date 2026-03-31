# Fluxo de Sequência — Explainable Credit Decision Engine

## Objetivo

Este documento descreve como uma solicitação percorre a plataforma, desde a entrada até a decisão final e sua explicação auditável.

---

# MVP 1 — Fluxo Síncrono

Neste estágio, a plataforma opera como um serviço único com persistência local.

```text
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

### Resultado do MVP 1
O cliente recebe:
- decisão
- score de risco
- regras acionadas
- timestamp da análise

---

# MVP 2 — Fluxo com Microserviços e RabbitMQ

Neste estágio, o fluxo passa a ser desacoplado e orientado a eventos.

```text
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

### Resultado do MVP 2
A plataforma passa a suportar:
- desacoplamento
- eventos
- enrichment externo
- escalabilidade por serviço

---

# MVP 4 — Fluxo com RAG + LLM

Neste estágio, o sistema passa a explicar a decisão usando contexto institucional e IA.

```text
Decision API   Rule Engine   RAG Service   LLM Service   Audit Service
     |               |            |              |              |
     |-- DecisionRequested ------------------------------> (RabbitMQ)
     |               |            |              |              |
     |               |-- avalia   |              |              |
     |               |-- score    |              |              |
     |               |-- decide   |              |              |
     |               |-- publish RulesEvaluated ---------------->|
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
     |                                           |-- valida JSON|
     |                                           |-- publish LLMReasoningCompleted
     |                                                          |
     |<-- consolida resultado ----------------------------------|
     |                                                          |
     |-- publish DecisionCompleted ----------------------------->|
     |                                                          |-- INSERT imutável
```

### Resultado do MVP 4
A resposta final passa a incluir:
- explicação da decisão
- referências de política
- recomendação de revisão manual
- justificativa em linguagem natural

---

## Identidade de Rastreio

Cada requisição carrega dois identificadores propagados ao longo de toda a jornada.

| Campo | Gerado por | Escopo |
|-------|-----------|--------|
| `transaction_id` | Decision API | Único por solicitação |
| `correlation_id` | API Gateway / Orchestrator | Propagado em logs, headers e mensagens |

Esses identificadores permitem:

- rastreamento distribuído
- correlação de eventos
- replay de decisões
- investigação operacional

---

## Resumo da Jornada

### MVP 1
- decisão síncrona
- persistência local
- regras e score

### MVP 2
- microserviços
- mensageria
- enrichment desacoplado

### MVP 4
- RAG
- explicação com LLM
- auditoria completa

---

## Princípio Fundamental

> A plataforma sempre separa:
> - **quem decide**
> - **quem contextualiza**
> - **quem explica**
> - **quem audita**

Isso é o que torna o sistema mais robusto, explicável e confiável.