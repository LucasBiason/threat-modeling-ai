# DREAD Agent

## Visão geral

O **DREAD Agent** é o agente responsável por atribuir pontuação de risco no modelo **DREAD** a uma lista de ameaças já identificadas (normalmente pelo STRIDE). Ele enriquece cada ameaça com `dread_score` (média 1–10) e `dread_details` (notas por dimensão).

**Arquivo:** `app/threat_analysis/agents/dread/agent.py`

## Objetivo

- Receber uma lista de ameaças (objetos com `component_id`, `threat_type`, `description`, `mitigation`, etc.).
- Para cada ameaça, calcular uma pontuação DREAD nas 5 dimensões (1–10 cada).
- Retornar a mesma lista de ameaças com os campos adicionais:
  - `dread_score`: média das 5 notas, arredondada em 2 casas decimais.
  - `dread_details`: objeto com `damage`, `reproducibility`, `exploitability`, `affected_users`, `discoverability`.

## Metodologia DREAD

DREAD é um modelo de avaliação de risco com cinco dimensões (cada uma 1–10):

| Dimensão            | Descrição                                                     |
| ------------------- | ------------------------------------------------------------- |
| **D**amage          | Quanto dano pode resultar se a vulnerabilidade for explorada? |
| **R**eproducibility | Quão fácil é reproduzir o ataque?                             |
| **E**xploitability  | Quão fácil é lançar o ataque?                                 |
| **A**ffected users  | Quantos usuários seriam afetados?                             |
| **D**iscoverability | Quão fácil é descobrir a vulnerabilidade?                     |

O agente usa um system prompt que descreve essas dimensões e pede consistência e realismo nas notas.

## Fluxo

1. **Entrada:** `threats: list[dict]` (lista de ameaças do STRIDE ou equivalente).
2. Se a lista for vazia, retorna `[]` imediatamente.
3. **Montagem:** As ameaças são serializadas em JSON e inseridas no `DREAD_USER_PROMPT`.
4. **Chamada:** `run_text_with_fallback()` com:
   - Ordem de conexões: Gemini → OpenAI → Ollama.
   - Mensagens system + user.
   - Validação `_validate_dread_result` (resultado deve ser uma lista).
   - Cache Redis (prefixo `"dread"`).
5. **Pós-processamento:** Para cada ameaça retornada, `dread_score` é limitado ao intervalo [1, 10] com `max(1, min(10, t["dread_score"]))`.
6. **Saída:** Lista de ameaças com scores; em caso de falha do LLM, retorna a lista original sem scores.

## Prompts

- **System:** Define o analista especialista em DREAD e as 5 dimensões (Damage, Reproducibility, Exploitability, Affected Users, Discoverability).
- **User:** Contém a lista de ameaças em JSON e pede que o modelo retorne a mesma lista com `dread_score` e `dread_details` adicionados. Retorno deve ser **apenas** uma lista JSON.

## Fallback

Se a chamada ao LLM falhar ou a validação falhar:

- O agente retorna a **lista original de ameaças** sem os campos DREAD.
- O pipeline continua; apenas as pontuações de risco ficam ausentes.

## Cache

- O resultado da pontuação é cacheado em Redis com prefixo `"dread"`.
- A chave é derivada das mensagens e configurações em `run_text_with_fallback`.
- Evita reprocessar o mesmo conjunto de ameaças.

## Ordem de conexões LLM

1. **Gemini**
2. **OpenAI**
3. **Ollama**

## Integração no pipeline

O DREAD Agent é invocado **depois** do STRIDE. Ele recebe a lista de ameaças STRIDE e devolve a mesma lista enriquecida com scores DREAD, permitindo priorização por risco (por exemplo, ordenar por `dread_score`).
