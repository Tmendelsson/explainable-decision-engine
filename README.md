# Explainable Credit Decision Engine

> Plataforma de decisão explicável para análise de crédito, risco e elegibilidade, com microserviços, mensageria, auditoria, RAG e LLM para suporte à justificativa e revisão humana.

---

## Visão Geral

O **Explainable Credit Decision Engine** é uma plataforma backend projetada para simular cenários reais de decisão em ambientes financeiros e corporativos, como:

- **análise de crédito**
- **pré-aprovação de produtos financeiros**
- **classificação de risco**
- **triagem antifraude**
- **revisão manual assistida**
- **explicabilidade de decisões**

O sistema combina:

- **Motor de regras determinístico** — decisão objetiva baseada em regras dinâmicas configuráveis
- **Score de risco** — pontuação calculada a partir de sinais de elegibilidade, inconsistência e risco
- **Mensageria** — orquestração distribuída e desacoplada entre serviços
- **RAG** — recuperação de políticas e critérios institucionais como contexto *(MVP 4)*
- **LLM** — geração de justificativas auditáveis em linguagem natural *(MVP 4)*
- **Auditoria completa** — rastreabilidade imutável de cada decisão *(MVP 3)*

> **Importante:** o LLM **não decide**.  
> A decisão é sempre tomada pelo motor determinístico e pelas regras configuradas.  
> A IA é utilizada apenas para **explicação, contextualização e apoio à revisão humana**.

---

## Objetivo do Projeto

Este projeto foi desenhado para demonstrar conhecimentos em:

- arquitetura backend
- design de motores de decisão
- modelagem de domínio financeiro
- mensageria e sistemas distribuídos
- auditabilidade
- explicabilidade de IA
- integração entre regras de negócio e suporte analítico

É um projeto voltado para contextos semelhantes aos encontrados em:

- bancos
- fintechs
- plataformas de crédito
- plataformas antifraude
- sistemas de elegibilidade e underwriting

---

## Casos de Uso

O sistema foi pensado para suportar cenários como:

- análise de solicitação de **cartão de crédito**
- pré-avaliação de **empréstimo pessoal**
- elegibilidade para **financiamento**
- triagem de inconsistências cadastrais
- roteamento para **revisão manual**
- apoio à justificativa de decisões em contexto auditável

---

## Arquitetura

```text
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

## Fluxo de Decisão

1. O cliente ou sistema externo envia uma solicitação de avaliação.
2. O **Decision API / Orchestrator** recebe e valida a requisição.
3. O **Data Enrichment** agrega sinais complementares de perfil, risco e consistência.
4. O **Rule Engine Service** executa as regras determinísticas e calcula o score.
5. O resultado é persistido e registrado na trilha de auditoria.
6. Em MVPs futuros, o **RAG** recupera políticas relevantes e o **LLM** gera a justificativa explicável.
7. O sistema retorna:
   - decisão
   - score de risco
   - regras acionadas
   - justificativa (quando aplicável)

---

## Roadmap de MVPs

| MVP | Nome | Status |
|-----|------|--------|
| **MVP 1** | Core Credit Evaluation Engine | ✅ Em desenvolvimento |
| **MVP 2** | Arquitetura Distribuída (Microservices + RabbitMQ) | 🔜 Planejado |
| **MVP 3** | Auditabilidade & Governança | 🔜 Planejado |
| **MVP 4** | Explicabilidade com RAG + LLM | 🔜 Planejado |
| **MVP 5** | Plataforma do Analista (Admin + Observabilidade) | 🔜 Futuro |

---

# MVP 1 — Core Credit Evaluation Engine

Motor de decisão funcional em serviço único com regras dinâmicas, score de risco, classificação de elegibilidade e persistência.

## Stack

- Python 3.12
- FastAPI
- PostgreSQL 16
- SQLAlchemy 2.0 (async)
- Alembic
- Docker Compose

---

## Quick Start

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

---

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/api/v1/decisions/` | Submeter solicitação de decisão |
| `GET` | `/api/v1/decisions/{transaction_id}` | Consultar resultado por ID |
| `GET` | `/api/v1/rules/` | Listar regras ativas |
| `POST` | `/api/v1/rules/` | Criar nova regra |
| `PATCH` | `/api/v1/rules/{id}/toggle` | Ativar/desativar regra |
| `GET` | `/health` | Health check |

---

## Exemplo de Requisição

```bash
curl -X POST http://localhost:8000/api/v1/decisions/ \
  -H "Content-Type: application/json" \
  -d '{
    "cpf": "123.456.789-00",
    "product": "credit_card",
    "monthly_income": 5000.0,
    "age": 30,
    "credit_score": 650,
    "has_recent_default": false,
    "declared_employment_type": "CLT"
  }'
```

---

## Exemplo de Resposta

```json
{
  "transaction_id": "a1b2c3d4-...",
  "status": "completed",
  "decision": "approve",
  "risk_score": 85.0,
  "matched_rules": [],
  "manual_review_recommended": false,
  "created_at": "2026-03-19T17:00:00Z"
}
```

---

## Lógica de Decisão

```text
Base score: 100 pontos

Regras eliminatórias (action=deny)
→ decisão = deny (independente do score)

Regras de peso (action=flag/manual_review)
→ subtraem weight do score

Faixas de decisão:
  ≥ 70  → approve
  50–69 → manual_review
  < 50  → deny
```

---

## Exemplos de Regras de Negócio

Exemplos de regras que podem ser configuradas no motor:

- score de crédito abaixo do mínimo permitido
- renda incompatível com o produto solicitado
- idade fora da política de elegibilidade
- inadimplência recente
- inconsistência entre perfil declarado e dados analisados
- múltiplas tentativas em janela curta
- produto restrito para determinado perfil de risco

---

## Modelo de Domínio

As principais entidades do sistema incluem:

- **Applicant** — dados do solicitante
- **CreditRequest** — solicitação de crédito/produto
- **DecisionResult** — resultado consolidado da análise
- **Rule** — regra configurável de decisão
- **RiskSignal** — sinal de risco detectado
- **PolicyReference** — política ou guideline utilizada como referência
- **AuditEvent** — evento auditável
- **ManualReviewQueue** — fila de revisão humana

---

## Conceitos Principais

## Regras Determinísticas vs Explicação Assistida

O sistema separa claramente três camadas:

| Camada | Tecnologia | Papel |
|--------|-----------|-------|
| **Determinística** | Motor de regras | **Decide** com base em thresholds, políticas e sinais objetivos |
| **Contextual** | RAG + pgvector | **Contextualiza** com políticas e guidelines institucionais |
| **Explicativa** | LLM | **Explica** a decisão e apoia revisão humana |

> O LLM **nunca altera** a decisão.  
> Ele apenas explica, sumariza e apoia.

---

## Exemplo de Resposta com IA (MVP 4)

```json
{
  "transaction_id": "uuid",
  "decision": "deny",
  "risk_score": 42,
  "matched_rules": ["LOW_CREDIT_SCORE", "INCOME_INCONSISTENCY"],
  "policy_references": [
    "credit_policy_premium_v2",
    "fraud_signals_guide"
  ],
  "explanation": "A solicitação foi negada porque o perfil apresentou score de crédito abaixo do mínimo exigido para o produto solicitado, além de divergência entre renda declarada e faixa estimada segundo as regras de elegibilidade vigentes.",
  "manual_review_recommended": false
}
```

---

## Estrutura do Repositório

```text
explainable-credit-decision-engine/
├── docker-compose.yml
├── .env.example
├── docs/
│   ├── architecture.md
│   ├── sequence-flow.md
│   ├── rule-engine.md
│   ├── domain-model.md
│   ├── financial-use-cases.md
│   ├── rule-versioning.md
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

## Próximos Passos

- finalizar o núcleo de decisão do MVP 1
- adicionar versionamento de regras
- implementar score breakdown
- iniciar pipeline assíncrono com RabbitMQ
- estruturar trilha de auditoria
- preparar base documental para RAG
- adicionar explicabilidade com LLM

---

## Objetivo de Portfólio

Este projeto foi pensado para demonstrar domínio prático em:

- Python backend moderno
- arquitetura orientada a serviços
- modelagem de decisão
- sistemas auditáveis
- IA aplicada com responsabilidade
- domínio de risco, crédito e elegibilidade

---

## Status

🚧 Projeto em evolução contínua — roadmap incremental por MVPs.