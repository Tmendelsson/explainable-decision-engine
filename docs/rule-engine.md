# Motor de Regras — Rule Engine

## Visão Geral

O motor de regras é o **decisor determinístico principal** do sistema.

Ele é responsável por avaliar sinais objetivos e produzir uma decisão clara, baseada em:

- critérios configuráveis
- score de risco
- regras eliminatórias
- faixas de elegibilidade

> A decisão **sempre** nasce aqui.  
> O LLM apenas explica.

---

## Objetivo no Domínio

No contexto deste projeto, o motor de regras simula cenários reais como:

- análise de crédito
- elegibilidade de produto
- triagem de inconsistências
- encaminhamento para revisão manual
- avaliação de risco inicial

---

## Estrutura de uma Regra

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `name` | string | Identificador único da regra |
| `description` | string | Descrição legível |
| `field` | string | Campo do payload avaliado |
| `operator` | enum | Operador de comparação |
| `value` | float/string/bool | Valor de referência |
| `action` | enum | Ação disparada quando a regra é satisfeita |
| `weight` | float | Peso da penalidade |
| `priority` | int | Ordem de avaliação |
| `product_type` | string? | Produto ao qual a regra se aplica |
| `is_active` | bool | Indica se a regra está ativa |
| `version` | int | Versão da regra |

---

## Operadores Suportados

| Operador | Significado |
|----------|-------------|
| `lt` | menor que |
| `gt` | maior que |
| `lte` | menor ou igual |
| `gte` | maior ou igual |
| `eq` | igual a |

---

## Ações Disponíveis

| Ação | Efeito |
|------|--------|
| `deny` | Rejeição imediata |
| `manual_review` | Penaliza score e força revisão |
| `flag` | Penaliza score |

---

## Lógica de Decisão

```text
1. Carregar regras ativas do banco
2. Filtrar por:
   is_active = true
   AND (product_type = null OR product_type = produto_solicitado)

3. Ordenar por priority DESC

4. Avaliar cada regra:
   a. Ler valor do campo
   b. Aplicar operador
   c. Se satisfeita:
      - action = deny → registrar como eliminatória
      - action = manual_review/flag → acumular penalidade

5. Calcular risk_score = 100 - total_penalty

6. Determinar decisão:
   - se houver regra eliminatória → deny
   - senão, se score < 50 → deny
   - senão, se score < 70 → manual_review
   - senão → approve
```

---

## Faixas de Decisão

| Faixa de Score | Decisão |
|---------------|---------|
| `>= 70` | `approve` |
| `50–69` | `manual_review` |
| `< 50` | `deny` |

---

## Regras Iniciais (seed)

| Nome | Campo | Condição | Ação | Peso |
|------|-------|----------|------|------|
| `UNDERAGE_APPLICANT` | age | `< 18` | deny | 100 |
| `LOW_INCOME` | monthly_income | `< 1500` | deny | 50 |
| `LOW_CREDIT_SCORE` | credit_score | `< 500` | deny | 60 |
| `MEDIUM_CREDIT_RISK` | credit_score | `< 650` | manual_review | 25 |
| `LOW_INCOME_FLAG` | monthly_income | `< 3000` | flag | 15 |

---

## Exemplos de Regras de Negócio Futuras

- histórico recente de inadimplência
- renda incompatível com produto solicitado
- excesso de tentativas em janela curta
- inconsistência cadastral
- perfil de alto risco para determinado produto
- exigência de revisão manual por faixa de score

---

## Exemplos de Avaliação

### Caso 1 — Aprovado

```text
Input:
age = 30
monthly_income = 8000
credit_score = 750

Regras acionadas: nenhuma
Risk score: 100
Decisão: approve
```

---

### Caso 2 — Revisão Manual

```text
Input:
age = 25
monthly_income = 2500
credit_score = 600

Regras acionadas:
- MEDIUM_CREDIT_RISK (25)
- LOW_INCOME_FLAG (15)

Risk score: 60
Decisão: manual_review
```

---

### Caso 3 — Negado por Regra Eliminatória

```text
Input:
age = 16
monthly_income = 5000
credit_score = 800

Regras acionadas:
- UNDERAGE_APPLICANT

Decisão: deny
```

---

### Caso 4 — Negado por Score

```text
Input:
age = 30
monthly_income = 1800
credit_score = 580

Regras acionadas:
- MEDIUM_CREDIT_RISK (25)
- LOW_INCOME_FLAG (15)

Risk score: 60
Decisão: manual_review
```

---

## Versionamento de Regras

Cada regra deve possuir `version`.

Objetivos:
- preservar histórico
- permitir replay
- evitar sobrescrita destrutiva
- suportar governança de mudança

### Regra importante
> Alterar uma regra **não substitui** a versão anterior.  
> A mudança cria uma **nova versão**.

---

## Valor Arquitetural

O Rule Engine demonstra:

- encapsulamento de regra de negócio
- flexibilidade de configuração
- decisão objetiva
- base sólida para contexto regulado e auditável