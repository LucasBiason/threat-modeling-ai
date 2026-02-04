# DREAD Risk Scoring - Guia Completo

## O que é DREAD?

DREAD é um modelo de pontuação de risco que avalia ameaças em 5 dimensões, cada uma com escala de 1-10:

| Dimensão | Pergunta | Escala |
|----------|----------|--------|
| **D**amage | Qual o impacto se explorada? | 1=Mínimo, 10=Catastrófico |
| **R**eproducibility | Quão fácil é reproduzir o ataque? | 1=Muito difícil, 10=Sempre funciona |
| **E**xploitability | Quão fácil é executar o ataque? | 1=Precisa expert, 10=Automatizado |
| **A**ffected Users | Quantos usuários são impactados? | 1=Poucos, 10=Todos |
| **D**iscoverability | Quão fácil é descobrir a vulnerabilidade? | 1=Muito difícil, 10=Óbvia |

**Score Final** = (D + R + E + A + D) / 5

---

## Classificação de Risco

| Score | Nível | Ação |
|-------|-------|------|
| 1-3 | LOW | Monitorar, corrigir quando conveniente |
| 4-5 | MEDIUM | Planejar correção no próximo sprint |
| 6-7 | HIGH | Priorizar correção imediata |
| 8-10 | CRITICAL | Parar tudo e corrigir agora |

---

## Guia de Pontuação por Dimensão

### Damage (Impacto)

| Score | Descrição | Exemplos |
|-------|-----------|----------|
| 1-2 | Mínimo | Log excessivo, info não sensível vazada |
| 3-4 | Baixo | Dados de um usuário expostos temporariamente |
| 5-6 | Moderado | Dados de vários usuários, interrupção parcial |
| 7-8 | Alto | Dados sensíveis em massa, compliance violation |
| 9-10 | Catastrófico | Todos os dados, destruição de sistema, ransomware |

### Reproducibility (Reprodutibilidade)

| Score | Descrição | Exemplos |
|-------|-----------|----------|
| 1-2 | Raro | Precisa de condições muito específicas |
| 3-4 | Difícil | Precisa de timing específico, race condition |
| 5-6 | Moderado | Reproduzível com esforço, precisa de setup |
| 7-8 | Fácil | Reproduzível consistentemente com instruções |
| 9-10 | Sempre | 100% reproduzível, trivial |

### Exploitability (Facilidade de Exploração)

| Score | Descrição | Exemplos |
|-------|-----------|----------|
| 1-2 | Expert | Precisa de conhecimento profundo, zero-day |
| 3-4 | Avançado | Precisa de skills de pentest, customização |
| 5-6 | Intermediário | Scripts existem, precisa adaptar |
| 7-8 | Fácil | Ferramentas prontas (Metasploit, SQLmap) |
| 9-10 | Trivial | Exploit público, bots automatizados |

### Affected Users (Usuários Afetados)

| Score | Descrição | Exemplos |
|-------|-----------|----------|
| 1-2 | Poucos | Um usuário específico, admin interno |
| 3-4 | Alguns | Grupo pequeno, departamento |
| 5-6 | Muitos | Percentual significativo de usuários |
| 7-8 | Maioria | Maioria dos usuários do sistema |
| 9-10 | Todos | Todos os usuários, incluindo externos |

### Discoverability (Descoberta)

| Score | Descrição | Exemplos |
|-------|-----------|----------|
| 1-2 | Oculto | Precisa de acesso interno, código fonte |
| 3-4 | Difícil | Precisa de análise profunda, fuzzing |
| 5-6 | Moderado | Descoberto com scan de vulnerabilidades |
| 7-8 | Fácil | Visível em logs, comportamento anômalo |
| 9-10 | Óbvio | Público, documentado, na interface |

---

## Exemplos de Scoring por Tipo de Ameaça

### SQL Injection em API Pública

| Dimensão | Score | Justificativa |
|----------|-------|---------------|
| Damage | 9 | Acesso total ao banco de dados |
| Reproducibility | 9 | Sempre funciona se endpoint vulnerável |
| Exploitability | 8 | SQLmap automatiza |
| Affected Users | 10 | Todos os dados de usuários |
| Discoverability | 7 | Scan automatizado encontra |
| **TOTAL** | **8.6 CRITICAL** | |

### Bucket S3 Público (Misconfiguration)

| Dimensão | Score | Justificativa |
|----------|-------|---------------|
| Damage | 7 | Exposição de dados armazenados |
| Reproducibility | 10 | Sempre acessível se público |
| Exploitability | 10 | Só precisa da URL |
| Affected Users | 8 | Todos cujos dados estão no bucket |
| Discoverability | 9 | Ferramentas escaneiam buckets públicos |
| **TOTAL** | **8.8 CRITICAL** | |

### Session Fixation

| Dimensão | Score | Justificativa |
|----------|-------|---------------|
| Damage | 6 | Hijack de sessão individual |
| Reproducibility | 7 | Reproduzível com link malicioso |
| Exploitability | 5 | Precisa de engenharia social |
| Affected Users | 3 | Um usuário por vez |
| Discoverability | 4 | Precisa analisar fluxo de autenticação |
| **TOTAL** | **5.0 MEDIUM** | |

### Logs sem Sanitização (Info Disclosure)

| Dimensão | Score | Justificativa |
|----------|-------|---------------|
| Damage | 5 | Exposição de dados em logs |
| Reproducibility | 8 | Sempre loga dados sensíveis |
| Exploitability | 3 | Precisa acesso aos logs |
| Affected Users | 6 | Usuários cujos dados são logados |
| Discoverability | 2 | Precisa acesso interno |
| **TOTAL** | **4.8 MEDIUM** | |

### DDoS em API sem Rate Limiting

| Dimensão | Score | Justificativa |
|----------|-------|---------------|
| Damage | 6 | Indisponibilidade do serviço |
| Reproducibility | 10 | Sempre funciona sem proteção |
| Exploitability | 9 | Ferramentas de stress testing |
| Affected Users | 10 | Todos os usuários |
| Discoverability | 8 | Óbvio pela falta de 429 responses |
| **TOTAL** | **8.6 CRITICAL** | |

---

## DREAD por Categoria STRIDE

### Spoofing (Falsificação de Identidade)

| Ameaça | D | R | E | A | D | Total |
|--------|---|---|---|---|---|-------|
| Credential Stuffing | 7 | 9 | 9 | 8 | 9 | 8.4 |
| Session Hijacking | 6 | 7 | 5 | 3 | 4 | 5.0 |
| API Key Theft | 8 | 8 | 6 | 6 | 5 | 6.6 |

### Tampering (Adulteração)

| Ameaça | D | R | E | A | D | Total |
|--------|---|---|---|---|---|-------|
| SQL Injection | 9 | 9 | 8 | 10 | 7 | 8.6 |
| XSS Stored | 7 | 9 | 7 | 8 | 6 | 7.4 |
| Man-in-the-Middle | 8 | 5 | 4 | 6 | 3 | 5.2 |

### Repudiation (Não-Repúdio)

| Ameaça | D | R | E | A | D | Total |
|--------|---|---|---|---|---|-------|
| Audit Log Tampering | 6 | 6 | 5 | 8 | 3 | 5.6 |
| Missing Logs | 4 | 10 | 1 | 7 | 2 | 4.8 |

### Information Disclosure

| Ameaça | D | R | E | A | D | Total |
|--------|---|---|---|---|---|-------|
| S3 Bucket Público | 7 | 10 | 10 | 8 | 9 | 8.8 |
| Error Messages Verbose | 4 | 9 | 8 | 5 | 8 | 6.8 |
| Unencrypted Traffic | 7 | 7 | 5 | 7 | 4 | 6.0 |

### Denial of Service

| Ameaça | D | R | E | A | D | Total |
|--------|---|---|---|---|---|-------|
| API sem Rate Limit | 6 | 10 | 9 | 10 | 8 | 8.6 |
| Resource Exhaustion | 5 | 7 | 6 | 8 | 5 | 6.2 |
| Algorithmic Complexity | 6 | 6 | 4 | 8 | 3 | 5.4 |

### Elevation of Privilege

| Ameaça | D | R | E | A | D | Total |
|--------|---|---|---|---|---|-------|
| IDOR (Insecure Direct Object Ref) | 7 | 8 | 7 | 6 | 6 | 6.8 |
| Broken Access Control | 8 | 7 | 6 | 7 | 5 | 6.6 |
| JWT Algorithm None | 9 | 9 | 8 | 10 | 4 | 8.0 |

---

## Processo de Scoring

1. **Para cada ameaça STRIDE identificada:**
   - Avalie cada dimensão DREAD (1-10)
   - Calcule a média

2. **Priorize pela média:**
   - CRITICAL (8-10): Correção imediata
   - HIGH (6-7): Próximo sprint
   - MEDIUM (4-5): Backlog
   - LOW (1-3): Aceitar ou monitorar

3. **Documente justificativas** para auditoria

---

## Referências

- OWASP Risk Rating Methodology
- Microsoft SDL Threat Modeling
- NIST SP 800-30 Risk Assessment
- FAIR (Factor Analysis of Information Risk)
