# Guia de Sinais de Fraude
**Versão:** 1.3 | **Área:** Compliance & Prevenção a Fraudes | **Vigência:** 2026-01-01

---

## 1. Objetivo

Este guia define os principais sinais de alerta de fraude que o sistema de decisão deve identificar e como cada sinal deve influenciar a avaliação.

---

## 2. Categorias de Sinais de Fraude

### 2.1 Sinais de Alta Gravidade (score penalty: 50–100 pontos)

Esses sinais, individualmente, podem resultar em negação automática ou obrigatoriedade de revisão manual com equipe antifraude.

| Sinal | Código | Ação Recomendada |
|-------|--------|-----------------|
| CPF com bloqueio regulatório | `CPF_BLOCKED` | Negação automática |
| Tentativas múltiplas em < 1h | `VELOCITY_HIGH` | Negação automática |
| IP originado em servidor/VPN | `SUSPICIOUS_IP` | Revisão antifraude |
| Dados cadastrais alterados há < 24h | `RECENT_DATA_CHANGE` | Revisão antifraude |
| Score de identidade digital < 30 | `LOW_ID_SCORE` | Negação automática |

### 2.2 Sinais de Média Gravidade (score penalty: 20–49 pontos)

Combinação de 2 ou mais sinais médios deve escalar para revisão manual.

| Sinal | Código | Ação Recomendada |
|-------|--------|-----------------|
| Geolocalização inconsistente | `GEO_MISMATCH` | Penalização de score |
| Dispositivo nunca utilizado antes | `NEW_DEVICE` | Monitoramento |
| Horário de acesso atípico | `UNUSUAL_HOUR` | Penalização de score |
| Divergência entre CEP e perfil | `ZIP_MISMATCH` | Penalização de score |
| Produto solicitado fora do perfil | `OUT_OF_PROFILE` | Revisão manual |

### 2.3 Sinais de Baixa Gravidade (score penalty: 5–19 pontos)

Isoladamente não alteram a decisão, mas contribuem para o score global.

| Sinal | Código | Ação Recomendada |
|-------|--------|-----------------|
| Primeiro acesso ao produto | `FIRST_ACCESS` | Monitoramento |
| E-mail diferente do cadastrado | `EMAIL_MISMATCH` | Penalização |
| Número de telefone alterado < 30 dias | `PHONE_CHANGE` | Monitoramento |

---

## 3. Combinação de Sinais

A gravidade de uma solicitação aumenta quando múltiplos sinais são identificados simultaneamente:

```
1 sinal médio       → score penalty normal
2 sinais médios     → penalty x 1.5
3+ sinais médios    → escalada obrigatória para antifraude
1 sinal médio + 1 alto → negação automática ou escalada
```

---

## 4. Inconsistência de Dados Cadastrais

A inconsistência cadastral é definida como:

- Nome declarado difere do constante no CPF (Receita Federal)
- Data de nascimento diverge em mais de 1 dia
- Endereço completamente diferente dos últimos 12 meses
- Telefone e e-mail nunca utilizados em transações anteriores

**Critério:** 2 ou mais inconsistências simultâneas → sinal `DATA_INCONSISTENCY` ativo.

---

## 5. Velocidade de Transações (Velocity Check)

| Janela de Tempo | Número de Tentativas | Ação |
|-----------------|---------------------|------|
| 1 hora | ≥ 3 | Bloqueio temporário de 2h |
| 24 horas | ≥ 5 | Revisão manual obrigatória |
| 7 dias | ≥ 10 | Encaminhamento para equipe antifraude |

---

## 6. Diretrizes para Analistas

Quando o sistema identifica sinais de fraude e encaminha para revisão manual, o analista deve:

1. Verificar identidade do solicitante por canal adicional (e-mail ou SMS de confirmação)
2. Comparar dados com fontes externas (Receita Federal, Serasa)
3. Documentar o racional da decisão final
4. Registrar todos os sinais identificados no sistema de auditoria
5. Em caso de suspeita confirmada, acionar equipe de compliance

---

*Aprovado pela Gerência de Prevenção a Fraudes — vigência: 2026-01-01*
