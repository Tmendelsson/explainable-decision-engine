# Roadmap de MVPs — Explainable Credit Decision Engine

## Visão Geral

| MVP | Nome | Foco Principal | Status |
|-----|------|----------------|--------|
| MVP 1 | Core Credit Evaluation Engine | Motor de regras + score + persistência | ✅ Completo |
| MVP 2 | Arquitetura Distribuída | Microserviços + mensageria | ✅ Completo |
| MVP 3 | Auditabilidade & Governança | Auditoria + resiliência + replay | 🔜 Planejado |
| MVP 4 | Explicabilidade com RAG + LLM | Justificativa inteligente e auditável | 🔜 Planejado |
| MVP 5 | Plataforma do Analista | Admin + observabilidade + revisão humana | 🔜 Futuro |

---

## Objetivo do Roadmap

O projeto foi estruturado para evoluir de forma incremental, sem retrabalho, com foco em demonstrar:

- backend moderno
- arquitetura enterprise
- decisão determinística
- explicabilidade com IA
- contexto financeiro
- governança e rastreabilidade

> Cada MVP deve ser **publicável** e ter valor técnico visível no portfólio.

---

# MVP 1 — Core Credit Evaluation Engine

## Objetivo
Entregar um motor de decisão funcional em serviço único com:

- regras dinâmicas
- score de risco
- decisão final
- persistência
- API REST

---

## Serviços
- `decision-api`
- `postgres`

---

## Funcionalidades
- [x] `POST /decisions/` — submeter solicitação
- [x] `GET /decisions/{id}` — consultar resultado
- [x] motor de regras dinâmico
- [x] score de risco por peso
- [x] decisão:
  - `approve`
  - `deny`
  - `manual_review`
- [x] `GET /rules/` — listar regras
- [x] `POST /rules/` — criar regra
- [x] `PATCH /rules/{id}/toggle` — ativar/desativar regra
- [x] health check endpoint
- [x] Docker Compose
- [x] seed de regras iniciais

---

## Casos de uso cobertos
- cartão de crédito
- pré-análise de crédito
- elegibilidade básica
- triagem inicial de risco

---

## O que demonstra
- FastAPI bem estruturado
- modelagem de domínio limpa
- regra de negócio encapsulada
- persistência assíncrona
- API com cara de produto real

---

# MVP 2 — Arquitetura Distribuída

## Objetivo
Separar o fluxo em microserviços desacoplados via mensageria.

---

## Novos Serviços
- `enrichment-service`
- `rule-engine-service`
- `rabbitmq`

---

## Funcionalidades
- [x] `decision-api` vira orchestrator puro
- [x] `enrichment-service` retorna dados simulados de perfil e risco
- [x] `rule-engine-service` consome `DecisionRequested`
- [x] comunicação assíncrona via RabbitMQ
- [x] eventos:
  - `DecisionRequested`
  - `RulesEvaluated`
  - `DecisionCompleted`
- [x] `correlation_id` propagado em todos os serviços
- [x] logs estruturados do fluxo distribuído

---

## Casos de uso cobertos
- análise desacoplada
- enriquecimento de perfil
- processamento assíncrono
- base para alta escalabilidade

---

## O que demonstra
- microserviços reais
- mensageria
- desacoplamento
- arquitetura moderna

---

# MVP 3 — Auditabilidade & Governança

## Objetivo
Levar o sistema para um nível mais próximo de contexto enterprise e regulado.

---

## Novos Serviços
- `audit-service`
- `redis`

---

## Funcionalidades
- [ ] `audit-service` escuta todos os eventos
- [ ] trilha imutável de auditoria
- [ ] persistência de input, enriched data, score, decisão e regras
- [ ] idempotência por `transaction_id`
- [ ] retry automático
- [ ] Dead Letter Queue (DLQ)
- [ ] status transacional:
  - `pending`
  - `processing`
  - `completed`
  - `failed`
- [ ] endpoint de histórico de decisões
- [ ] base para replay de decisões

---

## Casos de uso cobertos
- rastreabilidade
- compliance
- investigação operacional
- revisão histórica

---

## O que demonstra
- maturidade arquitetural
- design para produção
- resiliência
- mentalidade enterprise

---

# MVP 4 — Explicabilidade com RAG + LLM

## Objetivo
Adicionar contexto institucional e explicação em linguagem natural de forma auditável e controlada.

---

## Novos Serviços
- `rag-service`
- `llm-reasoning-service`

---

## Funcionalidades
- [ ] indexação da base de conhecimento
- [ ] embeddings no pgvector
- [ ] recuperação semântica com filtros
- [ ] LLM recebe:
  - decisão
  - score
  - regras acionadas
  - contexto recuperado
- [ ] LLM gera:
  - `decision_explanation`
  - `analyst_summary`
  - `manual_review_recommendation`
- [ ] resposta do LLM validada por schema
- [ ] prompt + contexto + resposta auditados
- [ ] guardrail: LLM nunca altera decisão base

---

## Casos de uso cobertos
- justificativa de decisão
- apoio ao analista
- explicação auditável
- contextualização institucional

---

## O que demonstra
- RAG aplicado em caso real
- LLM integration responsável
- XAI / explicabilidade
- IA com guardrails

---

# MVP 5 — Plataforma do Analista

## Objetivo
Transformar o projeto em uma plataforma completa com gestão, observabilidade e experiência operacional.

---

## Funcionalidades
- [ ] Rule Management Dashboard
- [ ] Knowledge Base Manager
- [ ] Human Review Dashboard
- [ ] Observabilidade:
  - Prometheus
  - Grafana
- [ ] autenticação JWT
- [ ] RBAC
- [ ] multi-tenant (opcional)
- [ ] avaliação de qualidade do RAG e do LLM

---

## Perfis da Plataforma
### Gestor
- KPIs
- distribuição de decisões
- gestão de regras

### Analista
- fila de revisão manual
- explicação detalhada
- justificativa obrigatória de ação

### Dev/Ops
- health checks
- trilha de auditoria
- eventos distribuídos

### Cliente
- jornada simplificada
- status humanizado
- envio de documentos

---

## O que demonstra
- visão de produto
- full lifecycle
- engenharia + operação
- backend + plataforma

---

## Princípios do Projeto

1. **Cada MVP é publicável**
2. **Cada etapa adiciona valor real**
3. **A decisão é sempre determinística**
4. **A IA explica, não decide**
5. **Auditabilidade é parte do design, não um extra**