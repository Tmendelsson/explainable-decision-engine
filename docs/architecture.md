# Arquitetura — Explainable Credit Decision Engine

## Visão Macro

O sistema é composto por **7 serviços principais** organizados em camadas, com foco em:

- análise de crédito
- avaliação de risco
- explicabilidade
- auditabilidade
- revisão manual assistida

```text
[Cliente / Sistema Externo]
            ↓
      [API Gateway]
            ↓
[Decision API / Orchestrator]
      ↓                 ↓
[Data Enrichment]   [PostgreSQL]
      ↓
   [RabbitMQ]
   ↙         ↘
[Rule Engine]   [Audit Service]
      ↓
[RAG Service] (pgvector)
      ↓
[LLM Reasoning Service]
      ↓
[Final Decision Composer]
```

---

## Objetivo Arquitetural

A arquitetura foi desenhada para separar claramente:

- **decisão determinística**
- **contextualização institucional**
- **explicação assistida por IA**
- **rastreabilidade forense**

Isso garante que a plataforma possa operar em cenários mais sensíveis, como:

- análise de crédito
- elegibilidade financeira
- triagem de inconsistências
- revisão manual assistida
- justificativa auditável de decisões

---

## Serviços

### 1. API Gateway
**Responsabilidades:**
- autenticação
- rate limiting
- roteamento
- propagação de `correlation_id`
- proteção da borda da aplicação

**Stack sugerida:**
- Nginx ou Traefik

---

### 2. Decision API / Orchestrator
**Coração da plataforma.**

Responsável por:

- receber a solicitação de análise
- validar o payload
- gerar `transaction_id`
- coordenar o fluxo
- persistir estado inicial e resultado final
- consolidar resposta ao cliente

> Ele **não decide sozinho**.  
> Seu papel é **orquestrar** a jornada da análise.

---

### 3. Data Enrichment Service
Responsável por enriquecer a solicitação com sinais adicionais de risco e consistência.

Exemplos de dados enriquecidos:
- score de crédito
- histórico de tentativas
- flags de fraude
- consistência cadastral
- indicadores de perfil de risco

Seu papel é fornecer dados objetivos e estruturados para a decisão.

---

### 4. Rule Engine Service
É o **decisor determinístico principal**.

Responsável por:

- carregar regras ativas
- aplicar regras eliminatórias
- calcular score de risco
- determinar a decisão base:
  - `approve`
  - `manual_review`
  - `deny`

Saídas principais:
- `base_decision`
- `risk_score`
- `matched_rules`

> A decisão **sempre nasce aqui**.

---

### 5. RAG / Knowledge Retrieval Service
Responsável por recuperar contexto institucional relevante para a explicação.

Funções:
- indexar políticas, manuais e critérios
- gerar embeddings
- armazenar contexto no `pgvector`
- recuperar trechos relevantes por similaridade semântica
- filtrar por produto, tipo de política e versão ativa

Exemplos de fontes:
- política de crédito
- diretrizes de elegibilidade
- sinais de fraude
- checklist de revisão manual

---

### 6. LLM Reasoning Service
Responsável por gerar explicações estruturadas e apoio à revisão humana.

Recebe:
- decisão base
- score de risco
- regras acionadas
- contexto recuperado via RAG

Gera:
- explicação da decisão
- resumo para analista
- recomendação de revisão manual
- justificativa em linguagem natural

> O LLM **nunca altera a decisão base**.  
> Seu papel é **explicar e apoiar**, não decidir.

---

### 7. Audit Service
Responsável por registrar de forma imutável todos os eventos da jornada de decisão.

Registra:
- payload original
- dados enriquecidos
- score e decisão
- regras acionadas
- contexto recuperado
- prompt do LLM
- resposta do LLM
- versões dos componentes envolvidos

Esse serviço é essencial para:

- compliance
- replay de decisões
- explicabilidade forense
- rastreabilidade operacional

---

## Fluxo de Dados

```text
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
  - consulta políticas relevantes
  - filtra por produto, tipo e versão ativa
        ↓
  [LLM Reasoning]
  - recebe decisão + score + regras + contexto
  - gera explanation, summary, review note
        ↓
  [Orchestrator]
  - consolida resposta final
  - publica DecisionCompleted → [Audit Service]
        ↓
  Retorna resposta ao cliente
```

---

## Estrutura da Resposta Final

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

| Camada | Serviço | Papel |
|--------|---------|-------|
| Determinística | Rule Engine | **Decide** com regras objetivas |
| Contextual | RAG Service | **Contextualiza** com políticas institucionais |
| Explicativa | LLM Service | **Explica** e apoia revisão humana |
| Rastreável | Audit Service | **Registra** tudo permanentemente |

> A plataforma foi desenhada para garantir que **a IA não substitua a lógica de negócio**, apenas a complemente com contexto e explicabilidade.

---

## Princípios Arquiteturais

1. **Decisão sempre determinística**
2. **Explicabilidade sem interferência da IA**
3. **Auditabilidade por design**
4. **Separação clara entre cálculo, contexto e explicação**
5. **Preparação para cenários enterprise e regulados**