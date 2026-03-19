# Roadmap de MVPs

## Visão Geral

| MVP | Nome | Foco Principal | Status |
|-----|------|----------------|--------|
| MVP 1 | Core Decision Engine | Motor de regras + persistência | ✅ Em desenvolvimento |
| MVP 2 | Arquitetura Distribuída | Microserviços + mensageria | 🔜 Planejado |
| MVP 3 | Auditabilidade & Robustez | Auditoria + resiliência | 🔜 Planejado |
| MVP 4 | IA (RAG + LLM) | Explicabilidade inteligente | 🔜 Planejado |
| MVP 5 | Plataforma Completa | Admin + Observabilidade | 🔜 Futuro |

---

## MVP 1 — Core Decision Engine

**Objetivo:** Motor de decisão funcional com regras dinâmicas, score de risco e persistência.

### Serviços
- `decision-api` (monolito modular)
- `postgres`

### Funcionalidades
- [x] `POST /decisions/` — submeter solicitação
- [x] `GET /decisions/{id}` — consultar resultado
- [x] Motor de regras dinâmico (regras no banco)
- [x] Score de risco por peso
- [x] Decisão: `approve` | `deny` | `manual_review`
- [x] `GET /rules/` — listar regras
- [x] `POST /rules/` — criar regra
- [x] `PATCH /rules/{id}/toggle` — ativar/desativar regra
- [x] Health check endpoint
- [x] Docker Compose
- [x] Seed de regras iniciais

### O que demonstra
- Backend sólido com FastAPI
- Modelagem de domínio limpa
- Regra de negócio encapsulada
- Persistência com SQLAlchemy async
- Organização de código profissional

---

## MVP 2 — Arquitetura Distribuída

**Objetivo:** Separar em microserviços reais comunicando via mensageria.

### Novos Serviços
- `enrichment-service`
- `rule-engine-service` (extraído do decision-api)
- `rabbitmq`

### Funcionalidades
- [ ] `decision-api` vira orchestrator puro
- [ ] `enrichment-service` retorna dados simulados (score, flags)
- [ ] `rule-engine-service` consome `DecisionRequested`
- [ ] Comunicação assíncrona via RabbitMQ
- [ ] Eventos: `DecisionRequested`, `DecisionCompleted`
- [ ] `correlation_id` propagado em todos os serviços
- [ ] Logs estruturados mostrando fluxo distribuído

### O que demonstra
- Microserviços de verdade
- Mensageria assíncrona
- Desacoplamento de responsabilidades
- Arquitetura moderna

---

## MVP 3 — Auditabilidade & Robustez

**Objetivo:** Nível enterprise com rastreabilidade completa e resiliência.

### Novos Serviços
- `audit-service`
- `redis` (cache + idempotência)

### Funcionalidades
- [ ] `audit-service` escuta todos os eventos
- [ ] Registro imutável: input, enriched data, decisão, regras, timestamps
- [ ] Idempotência por `transaction_id`
- [ ] Retry automático em falhas transitórias
- [ ] Dead Letter Queue (DLQ) para mensagens com erro
- [ ] Status da transação: `pending → processing → completed | failed`
- [ ] Endpoint de histórico de decisões

### O que demonstra
- Maturidade de arquitetura
- Sistemas resilientes
- Compliance mindset
- Mentalidade de produção

---

## MVP 4 — IA (RAG + LLM)

**Objetivo:** Adicionar explicabilidade inteligente — o grande diferencial do portfólio.

### Novos Serviços
- `rag-service` (pgvector)
- `llm-reasoning-service`

### Funcionalidades
- [ ] Indexação da base de conhecimento (`knowledge-base/`)
- [ ] Embeddings gerados e armazenados no pgvector
- [ ] Recuperação semântica com filtros (produto, tipo, versão ativa)
- [ ] LLM recebe: decisão + score + regras + contexto RAG
- [ ] LLM gera: `decision_explanation`, `analyst_summary`, `manual_review_recommendation`
- [ ] Resposta do LLM em JSON validado por schema
- [ ] Prompt + contexto + resposta auditados e persistidos
- [ ] Guardrail: LLM nunca altera decisão base

### Estrutura do Prompt LLM
```
Você é um assistente especializado em análise de crédito.
Com base nas regras acionadas e nos trechos de política fornecidos,
explique a decisão de forma clara e objetiva.
Não invente critérios. Se houver ambiguidade, sinalize revisão manual.

[Dados da solicitação]
[Decisão do motor de regras]
[Contexto recuperado pelo RAG]
```

### Saída do LLM
```json
{
  "decision_explanation": "...",
  "policy_summary": "...",
  "manual_review_needed": false,
  "confidence_note": "high"
}
```

### O que demonstra
- RAG aplicado em sistema real
- LLM integration com responsabilidade
- Explicabilidade (XAI)
- IA com guardrails e auditoria

---

## MVP 5 — Plataforma Completa

**Objetivo:** Produto final com painel de administração e observabilidade.

### Funcionalidades
- [ ] Rule Management Dashboard
- [ ] Knowledge Base Manager (upload + reindexação)
- [ ] Human Review Dashboard (analistas)
- [ ] Observabilidade: Prometheus + Grafana
- [ ] Autenticação JWT
- [ ] Multi-tenant (opcional)
- [ ] Avaliação automática de qualidade do RAG e LLM

### Front-End (4 perfis)
- **Gestor** — KPIs, distribuição de decisões, gestão de regras
- **Analista** — Fila de revisão com SLA, explicação detalhada, ação obrigatória com justificativa
- **Dev/Ops** — Health check em tempo real, trilha de auditoria completa
- **Cliente** — Jornada em steps, status humanizado, envio de documentos

---

## Princípios do Projeto

1. **Cada MVP é publicável** — tem valor técnico visível desde o primeiro commit
2. **Progressivo sem retrabalho** — cada MVP constrói em cima do anterior
3. **Decisão sempre determinística** — LLM explica, nunca decide
4. **Auditabilidade by design** — tudo rastreável desde MVP 1
