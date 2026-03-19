# Política de Elegibilidade por Produto
**Versão:** 1.2 | **Área:** Produtos & Crédito | **Vigência:** 2026-01-01

---

## 1. Objetivo

Define os critérios de elegibilidade específicos por produto, complementando a política geral de crédito.

---

## 2. Matriz de Elegibilidade

### Cartão de Crédito Padrão (`credit_card`)

| Critério | Mínimo | Notas |
|----------|--------|-------|
| Idade | 18 anos | Obrigatório |
| Renda mensal | R$ 1.500 | Comprovada ou declarada |
| Score de crédito | 500 | Score externo (0–1000) |
| Inadimplência | Nenhuma nos últimos 12 meses | Verifica bureau |

### Cartão Gold (`credit_card_gold`)

| Critério | Mínimo | Notas |
|----------|--------|-------|
| Idade | 21 anos | Recomendado (não eliminatório) |
| Renda mensal | R$ 5.000 | Eliminatório se abaixo |
| Score de crédito | 650 | Eliminatório se abaixo |
| Inadimplência | Nenhuma nos últimos 24 meses | Eliminatório |

### Cartão Platinum (`credit_card_platinum`)

| Critério | Mínimo | Notas |
|----------|--------|-------|
| Renda mensal | R$ 10.000 | Eliminatório |
| Score de crédito | 750 | Eliminatório |
| Relacionamento | 12 meses | Eliminatório |
| Inadimplência | Nenhuma nos últimos 36 meses | Eliminatório |

### Empréstimo Pessoal (`personal_loan`)

| Critério | Mínimo | Notas |
|----------|--------|-------|
| Idade | 18 anos | Obrigatório |
| Renda mensal | R$ 2.000 | Eliminatório |
| Score de crédito | 550 | Eliminatório se abaixo |
| Comprometimento de renda | Máx 35% | Incluindo parcela do empréstimo |

### Empréstimo Premium (`premium_loan`)

| Critério | Mínimo | Notas |
|----------|--------|-------|
| Renda mensal | R$ 7.500 | Eliminatório |
| Score de crédito | 700 | Eliminatório |
| Relacionamento | 6 meses | Eliminatório |

---

## 3. Regras de Comprometimento de Renda

Para empréstimos, o comprometimento de renda máximo permitido é:

| Produto | Comprometimento Máximo |
|---------|----------------------|
| personal_loan | 35% da renda mensal |
| premium_loan | 30% da renda mensal |

**Cálculo:**
```
comprometimento = (parcela_mensal / renda_mensal) * 100
se comprometimento > limite → revisão manual
se comprometimento > limite + 10% → negação automática
```

---

## 4. Downgrade de Produto

Quando o cliente solicita um produto e não atende os critérios mínimos, o sistema pode oferecer o produto imediatamente inferior:

```
credit_card_platinum → credit_card_gold
credit_card_gold     → credit_card
premium_loan         → personal_loan
```

O downgrade só é oferecido se o cliente atender os critérios do produto inferior.

---

## 5. Novos Produtos — Fase de Piloto

Produtos em fase de piloto possuem critérios mais restritivos temporariamente:

- Limite de aprovação reduzido em 30%
- Score mínimo acrescido de 50 pontos
- Obrigatoriedade de revisão manual para primeiras 1.000 aprovações

---

*Aprovado pela Diretoria de Produtos — vigência: 2026-01-01*
