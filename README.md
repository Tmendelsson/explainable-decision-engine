# Explainable Decision Engine

> Motor de decisão inteligente com microserviços, mensageria, RAG e LLM para justificativas auditáveis.

---

## Visão Geral

Sistema que combina:

- **Motor de regras determinístico** — decisão objetiva baseada em regras dinâmicas configuráveis
- **Score de risco** — pontuação calculada por peso das regras acionadas
- **RAG** — recuperação de políticas e critérios institucionais como contexto *(MVP 4)*
- **LLM** — geração de explicações auditáveis em linguagem natural *(MVP 4)*
- **Auditoria completa** — rastreabilidade imutável de cada decisão *(MVP 3)*

---

## Arquitetura

```
                     +----------------------+
                     |     API Gateway      |
                     |  Auth / Rate Limit   |
                     +----------+-----------+
                                |
                                v
                +----------------------------------+
                | Decision API / Orchestrator      |
                | transaction + workflow control   |
                +--------+----------------+--------+
                         |                |
                         v                v
          +-----------------------+  +----------------------+
          | Data Enrichment       |  |     PostgreSQL       |
          | credit/fraud/profile  |  | transactions/rules   |
          +-----------+-----------+  |   audit/config       |
                      |              +----------------------+
                      v
               +----------------------+
               |  RabbitMQ / Broker   |
               +------+----------+----+
                      |          |
         +------------+          +-------------------+
         |                                           |
         v                                           v
+---------------------------+       +-------------------------------+
| Rule Engine Service       |       | Audit Service                 |
| score + deterministic     |       | immutable event persistence   |
| decision evaluation       |       +-------------------------------+
+-------------+-------------+
              |
              v
+---------------------------+
| RAG / Knowledge Retrieval |
| vector search + policies  |
+-------------+-------------+
              |
              v
+---------------------------+
| LLM Reasoning Service     |
| explanation / summary /   |
| review support            |
+-------------+-------------+
              |
              v
+---------------------------+
| Final Decision Composer   |
| consolidate result        |
| decision + rationale      |
+---------------------------+
```

---

## Roadmap de MVPs

| MVP | Nome | Status |
|-----|------|--------|
| **MVP 1** | Core Decision Engine | ✅ Em desenvolvimento |
| **MVP 2** | Arquitetura Distribuída (Microservices + RabbitMQ) | 🔜 Planejado |
| **MVP 3** | Auditabilidade & Robustez | 🔜 Planejado |
| **MVP 4** | IA — RAG + LLM | 🔜 Planejado |
| **MVP 5** | Plataforma Completa (Admin + Observabilidade) | 🔜 Futuro |

---

## MVP 1 — Core Decision Engine

Motor de decisão funcional em serviço único com regras dinâmicas, score de risco e persistência.

### Stack

- Python 3.12 + FastAPI
- PostgreSQL 16
- SQLAlchemy 2.0 (async)
- Alembic
- Docker Compose

### Quick Start

```bash
# 1. Copiar variáveis de ambiente
cp .env.example .env

# 2. Subir serviços
docker-compose up -d

# 3. Popular regras iniciais
python scripts/seed_rules.py

# 4. Acessar documentação interativa
open http://localhost:8000/docs
```

### Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/api/v1/decisions/` | Submeter solicitação de decisão |
| `GET` | `/api/v1/decisions/{transaction_id}` | Consultar resultado por ID |
| `GET` | `/api/v1/rules/` | Listar regras ativas |
| `POST` | `/api/v1/rules/` | Criar nova regra |
| `PATCH` | `/api/v1/rules/{id}/toggle` | Ativar/desativar regra |
| `GET` | `/health` | Health check |

### Exemplo de Requisição

```bash
curl -X POST http://localhost:8000/api/v1/decisions/ \
  -H "Content-Type: application/json" \
  -d '{
    "cpf": "123.456.789-00",
    "product": "credit_card",
    "monthly_income": 5000.0,
    "age": 30,
    "credit_score": 650
  }'
```

### Exemplo de Resposta

```json
{
  "transaction_id": "a1b2c3d4-...",
  "status": "completed",
  "decision": "approve",
  "risk_score": 85.0,
  "matched_rules": [],
  "created_at": "2026-03-19T17:00:00Z"
}
```

### Lógica de Decisão

```
Base score: 100 pontos

Regras eliminatórias (action=deny) → decisão = deny (independente do score)
Regras de peso (action=flag/manual_review) → subtraem weight do score

Score final:
  ≥ 70 → approve
  50–69 → manual_review
  < 50 → deny
```

---

## Estrutura do Repositório

```
explainable-decision-engine/
├── docker-compose.yml
├── .env.example
├── docs/
│   ├── architecture.md
│   ├── sequence-flow.md
│   ├── rule-engine.md
│   ├── rag-design.md
│   ├── audit-model.md
│   └── mvp-roadmap.md
├── services/
│   ├── decision-api/          ← MVP 1 (implementado)
│   ├── enrichment-service/    ← MVP 2
│   ├── rule-engine-service/   ← MVP 2
│   ├── rag-service/           ← MVP 4
│   ├── llm-reasoning-service/ ← MVP 4
│   └── audit-service/         ← MVP 3
├── shared/
│   ├── contracts/
│   ├── events/
│   ├── schemas/
│   ├── utils/
│   └── observability/
├── knowledge-base/
│   ├── policies/
│   ├── compliance/
│   ├── product-rules/
│   └── manuals/
├── infra/
│   ├── gateway/
│   ├── postgres/
│   ├── rabbitmq/
│   └── redis/
└── scripts/
```

---

## Conceitos Principais

### Por que RAG + LLM?

O sistema separa claramente três camadas:

| Camada | Tecnologia | Papel |
|--------|-----------|-------|
| **Determinística** | Motor de regras | **Decide** com base em thresholds e flags objetivos |
| **Contextual** | RAG + pgvector | **Contextualiza** com políticas e guidelines institucionais |
| **Explicativa** | LLM | **Explica** a decisão e apoia revisão humana |

> O LLM **nunca altera** a decisão. Ele apenas explica e apoia.

### Exemplo de Resposta com IA (MVP 4)

```json
{
  "transaction_id": "uuid",
  "decision": "deny",
  "risk_score": 42,
  "matched_rules": ["LOW_CREDIT_SCORE", "INCOME_INCONSISTENCY"],
  "policy_references": ["credit_policy_premium_v2", "fraud_signals_guide"],
  "explanation": "A solicitação foi negada porque o perfil apresentou score de crédito abaixo do mínimo exigido para o produto solicitado, além de divergência entre renda declarada e faixa estimada segundo as regras de elegibilidade vigentes.",
  "manual_review_recommended": false
}
```

---

## Licença

MIT
