# Motor de Regras — Rule Engine

## Visão Geral

O motor de regras é o **decisor determinístico** do sistema. Ele avalia regras configuradas dinamicamente e produz uma decisão objetiva baseada em critérios quantificáveis.

> A decisão **sempre** vem aqui. O LLM só explica.

---

## Estrutura de uma Regra

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `name` | string | Identificador único da regra (ex: `LOW_CREDIT_SCORE`) |
| `description` | string | Descrição legível |
| `field` | string | Campo do payload avaliado (`monthly_income`, `age`, `credit_score`) |
| `operator` | enum | Operador de comparação |
| `value` | float | Valor de referência |
| `action` | enum | Ação disparada quando a regra é satisfeita |
| `weight` | float | Peso no score (penalidade) |
| `priority` | int | Ordem de avaliação (maior = avaliado primeiro) |
| `product_type` | string? | Produto ao qual a regra se aplica (`null` = global) |
| `is_active` | bool | Se a regra está ativa |

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
| `deny` | Rejeição imediata — score ignorado |
| `manual_review` | Penaliza score + sinaliza revisão |
| `flag` | Penaliza score |

---

## Lógica de Decisão

```
1. Carregar regras ativas do banco
2. Filtrar por: is_active=true AND (product_type=null OR product_type=produto_solicitado)
3. Ordenar por priority (desc)
4. Para cada regra:
   a. Obter valor do campo no payload
   b. Aplicar operador
   c. Se regra satisfeita:
      - action=deny  → adicionar à lista matched_deny
      - action=other → adicionar à lista matched_flag, acumular penalty

5. Calcular risk_score = 100 - total_penalty
   - Mínimo: 0
   - Máximo: 100

6. Determinar decisão final:
   - if matched_deny    → "deny"
   - elif risk_score < 50 → "deny"
   - elif risk_score < 70 → "manual_review"
   - else               → "approve"
```

---

## Regras Iniciais (seed)

| Nome | Campo | Condição | Ação | Peso |
|------|-------|----------|------|------|
| `UNDERAGE_APPLICANT` | age | < 18 | deny | 100 |
| `LOW_INCOME` | monthly_income | < 1500 | deny | 50 |
| `LOW_CREDIT_SCORE` | credit_score | < 500 | deny | 60 |
| `MEDIUM_CREDIT_RISK` | credit_score | < 650 | manual_review | 25 |
| `LOW_INCOME_FLAG` | monthly_income | < 3000 | flag | 15 |

---

## Exemplos de Avaliação

### Caso 1 — Aprovado
```
Input: age=30, monthly_income=8000, credit_score=750
Regras acionadas: nenhuma
Risk score: 100
Decisão: approve
```

### Caso 2 — Revisão manual
```
Input: age=25, monthly_income=2500, credit_score=600
Regras acionadas: MEDIUM_CREDIT_RISK (penalty=25), LOW_INCOME_FLAG (penalty=15)
Risk score: 100 - 25 - 15 = 60
Decisão: manual_review
```

### Caso 3 — Negado (regra eliminatória)
```
Input: age=16, monthly_income=5000, credit_score=800
Regras acionadas: UNDERAGE_APPLICANT (deny)
Risk score: N/A
Decisão: deny (imediato)
```

### Caso 4 — Negado por score
```
Input: age=30, monthly_income=2200, credit_score=530
Regras acionadas: MEDIUM_CREDIT_RISK (25), LOW_INCOME_FLAG (15)
Risk score: 100 - 25 - 15 = 60
Decisão: manual_review
```

---

## Versionamento de Regras

Cada regra possui um campo `version`. Em produções futuras (MVP 5), o sistema garantirá que:

- Decisões históricas possam ser reprocessadas com a versão de regra vigente na época
- Alterações de regra criam novas versões (nunca sobrescrevem)
- O audit service registra `rule_version` em cada decisão
