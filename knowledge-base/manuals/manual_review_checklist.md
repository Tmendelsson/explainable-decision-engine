# Checklist de Revisão Manual
**Versão:** 1.1 | **Área:** Operações de Crédito | **Público:** Analistas de Crédito

---

## 1. Objetivo

Este checklist orienta o analista de crédito durante a revisão manual de solicitações encaminhadas pelo sistema automatizado. Toda decisão manual deve ser documentada com justificativa.

---

## 2. Quando uma Solicitação Chega para Revisão Manual

O sistema encaminha uma solicitação para revisão manual quando:

- Score de crédito entre 500 e 649
- Inconsistência de renda detectada (> 20%)
- Sinais de fraude de média gravidade
- Solicitação de produto premium em limiar de critérios
- Flag `manual_review_recommended = true` gerado pelo sistema de IA

---

## 3. Checklist de Verificação

### 3.1 Validação de Identidade

- [ ] CPF válido e sem restrições regulatórias
- [ ] Nome confere com base da Receita Federal
- [ ] Data de nascimento confirmada
- [ ] Telefone de contato ativo e responsivo

### 3.2 Verificação de Renda

- [ ] Comprovante de renda recebido (últimos 3 meses)
- [ ] Renda comprovada é compatível com a declarada (tolerância: ±20%)
- [ ] Fonte de renda identificada (CLT, autônomo, empresário)
- [ ] Extrato bancário confere com renda declarada

### 3.3 Análise de Score

- [ ] Score externo verificado em bureau principal
- [ ] Score interno calculado pelo motor de regras analisado
- [ ] Histórico de pagamentos dos últimos 24 meses revisado
- [ ] Dívidas em aberto identificadas e avaliadas

### 3.4 Análise de Perfil

- [ ] Produto solicitado é compatível com perfil de renda
- [ ] Histórico de relacionamento com a instituição verificado
- [ ] Solicitações anteriores analisadas (padrão de comportamento)

### 3.5 Verificação de Sinais de Risco

- [ ] Sinais de fraude listados pelo sistema revisados
- [ ] Geolocalização verificada se `GEO_MISMATCH` ativo
- [ ] Consistência dos dados cadastrais verificada

---

## 4. Critérios para Aprovação Manual

O analista pode aprovar uma solicitação mesmo com score abaixo do automático quando:

1. Renda comprovada é superior à declarada e supera o mínimo
2. Inconsistência de renda explicada por documentação
3. Score baixo causado por evento pontual e isolado (ex: atraso único, quitado)
4. Cliente com bom histórico de relacionamento (> 24 meses)

**Limite de alçada:** Analista pode aprovar até R$ 15.000 sem escalada. Acima disso, necessita aprovação do supervisor.

---

## 5. Critérios para Negação Manual

O analista deve negar a solicitação quando:

1. Documentação não comprova a renda declarada
2. Sinais de fraude confirmados após investigação
3. Inconsistência de dados não explicada pelo cliente
4. Comprometimento de renda comprovado ultrapassa 40%

---

## 6. Documentação Obrigatória

O analista **deve** registrar no sistema:

- Motivo principal da decisão (texto livre, mínimo 50 caracteres)
- Documentos analisados (lista)
- Sinais de risco considerados
- Se a sugestão do sistema de IA foi seguida ou divergida (e por quê)

---

## 7. SLA de Revisão

| Tipo de Caso | SLA |
|-------------|-----|
| Revisão padrão | 24 horas úteis |
| Revisão de produto premium | 48 horas úteis |
| Revisão com suspeita de fraude | 4 horas (escalada imediata) |

---

## 8. Exemplos de Justificativas

### Aprovação:
> "Score de 580 gerado por atraso pontual em 2023, quitado. Renda comprovada de R$ 8.500 supera o mínimo. Histórico de 36 meses sem outras ocorrências. Aprovado com limite de R$ 5.000."

### Negação:
> "Inconsistência de renda de 45% não explicada por documentação. Extrato bancário não comprova movimentação compatível com renda declarada de R$ 9.000. Solicitação negada."

---

*Aprovado pela Gerência de Operações de Crédito — vigência: 2026-01-01*
