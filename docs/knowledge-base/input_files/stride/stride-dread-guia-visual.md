# Guia Visual STRIDE e DREAD

**Fonte:** Infográficos educacionais e material didático sobre modelagem de ameaças. Conteúdo capturado e estruturado por LLM para uso no RAG.

## Unificando STRIDE e DREAD para Priorizar Riscos

O processo de modelagem de ameaças em duas etapas:

1. **Passo 1: Identificar Ameaças com STRIDE**
2. **Passo 2: Priorizar Riscos com DREAD**

---

## Passo 1: Identificar Ameaças com STRIDE

### S - Spoofing (Falsificação de Identidade)
- **Definição:** Um invasor se passa por um usuário, componente ou sistema legítimo para obter acesso não autorizado.
- **Violação:** Autenticidade
- **Mitigações:** MFA, políticas de senhas fortes, validação de certificados digitais

### T - Tampering (Adulteração de Dados)
- **Definição:** Modificação não autorizada de dados ou código, seja em trânsito ou em repouso, violando a integridade.
- **Violação:** Integridade
- **Mitigações:** HTTPS/TLS, assinaturas digitais, checksums e validação rigorosa de entradas

### R - Repudiation (Repúdio)
- **Definição:** A capacidade de um usuário negar ter realizado uma ação devido à falta de logs ou provas adequadas.
- **Violação:** Não-repúdio
- **Mitigações:** Logs de auditoria seguros e à prova de violação, registros imutáveis, assinaturas digitais

### I - Information Disclosure (Divulgação de Informações)
- **Definição:** Exposição de dados confidenciais ou sensíveis a indivíduos ou sistemas não autorizados.
- **Violação:** Confidencialidade
- **Mitigações:** Criptografia em repouso e em trânsito, controle de acesso rigoroso, tratamento seguro de erros

### D - Denial of Service (Negação de Serviço)
- **Definição:** Tornar um sistema ou recurso indisponível para usuários legítimos, sobrecarregando-o ou explorando falhas.
- **Violação:** Disponibilidade
- **Mitigações:** Rate limiting, CAPTCHAs, WAF, arquitetura com escalabilidade automática

### E - Elevation of Privilege (Elevação de Privilégio)
- **Definição:** Um usuário ou processo obtém um nível de acesso mais alto do que o permitido.
- **Violação:** Autorização
- **Mitigações:** Princípio do menor privilégio, RBAC, higienização de entradas, auditorias regulares

---

## Passo 2: Priorizar Riscos com DREAD

DREAD é um mnemônico para quantificar e priorizar ameaças. Usado em conjunto com STRIDE.

### As Cinco Categorias DREAD

| Letra | Nome | Pergunta | Escala |
|-------|------|----------|--------|
| **D** | Dano Potencial | Qual o tamanho do dano se a ameaça for explorada? | 1-5 ou 1-8 |
| **R** | Reprodutibilidade | Quão fácil é reproduzir o ataque? | 1-5 ou 1-8 |
| **E** | Explorabilidade | Quanta habilidade ou recurso é necessário? | 1-5 ou 1-8 |
| **A** | Abrangência (Usuários Afetados) | Quantos usuários seriam impactados? | 1-5 ou 1-8 |
| **D** | Detectabilidade | Quão fácil é descobrir a vulnerabilidade? | 1-5 ou 1-8 |

### Como Calcular e Priorizar

1. **Atribua uma pontuação** para cada categoria (ex.: 1 a 5 ou 1 a 8)
2. **Calcule a pontuação total:** some as notas ou use a média `(Soma) / 5`
3. **Priorize:** ordene as ameaças da maior para a menor pontuação. Resolva as de maior score primeiro.

### Exemplo: Ameaça de Spoofing

| DREAD | Score | Justificativa |
|-------|-------|---------------|
| Dano Potencial | 5 | Custo financeiro e de reputação alto |
| Reprodutibilidade | 4 | Vulnerabilidade de API pode ser fácil de reproduzir |
| Explorabilidade | 5 | Falha na API pode ser simples de explorar com ferramentas |
| Abrangência | 5 | Pode afetar todos os usuários do sistema |
| Detectabilidade | 4 | Descoberta pode exigir trabalho, mas não muito complexa |
| **TOTAL** | **23** (soma) ou **4.6** (média) | **Prioridade ALTA/Crítica** |

---

## Aplicando STRIDE na Prática: Processo de 3 Passos

### 1. Desenhe o Diagrama de Fluxo de Dados (DFD)

Mapeie os componentes: processos, armazenamentos de dados, atores externos, fluxos de dados e **Fronteiras de Confiança (Trust Boundaries)**.

**Elementos do DFD:**
- Processos (ex.: API, Servidor Web)
- Fluxos de Dados (ex.: Requisição HTTPS)
- Armazenamentos de Dados (ex.: Banco de Dados)
- Atores Externos (ex.: Usuário, Sistema Terceiro)

### 2. Analise Ameaças em Cada Elemento

Para cada parte do diagrama, pergunte: *"Como um invasor poderia aplicar Spoofing aqui? Ou Tampering? Ou Denial of Service?"*

**Ameaças por tipo de componente:**
- **Processo:** S, T, R, I, D, E (todas)
- **Fluxo de Dados:** T, I, D
- **Armazenamento de Dados:** T, I, D
- **Ator Externo:** S, R

### 3. Identifique Mitigações e Documente os Riscos

Para cada ameaça encontrada, defina um controle de segurança. Priorize usando DREAD.

---

## Exemplo: Fluxo de Login Web (STRIDE por Categoria)

### Spoofing
- **Pergunta-chave:** Alguém pode fingir ser quem não é?
- **Exemplo:** Backend aceita JWT sem validar assinatura. Invasor forja token.

### Tampering
- **Pergunta-chave:** Alguém pode modificar meus dados?
- **Exemplo:** Comunicação HTTP (sem HTTPS) permite MITM alterar requisição.

### Repudiation
- **Pergunta-chave:** É possível executar uma ação e depois negar?
- **Exemplo:** Sem logs de auditoria, usuário pode negar ações maliciosas.

### Information Disclosure
- **Pergunta-chave:** Alguém pode acessar dados que não deveria?
- **Exemplo:** Stack trace completo em erro revela versão do banco e estrutura.

### Denial of Service
- **Pergunta-chave:** É possível derrubar o sistema?
- **Exemplo:** Endpoint `/auth` sem rate limiting permite milhões de tentativas.

### Elevation of Privilege
- **Pergunta-chave:** Um usuário comum pode se tornar administrador?
- **Exemplo:** Campo `role` no JWT não protegido; invasor altera para `admin`.

---

## Referências

- Material didático processado com auxílio de LLM para extração e estruturação em Markdown
- NotebookLM (infográficos)
