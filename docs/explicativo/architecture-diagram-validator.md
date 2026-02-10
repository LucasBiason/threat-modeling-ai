# Architecture Diagram Validator (Guardrail)

## Visão geral

O **Architecture Diagram Validator** é um **guardrail** que valida se a imagem enviada pelo usuário é de fato um **diagrama de arquitetura**. Ele evita que fotos, diagramas de sequência, fluxogramas ou imagens genéricas entrem no pipeline completo de análise (Diagram → STRIDE → DREAD), economizando custo e evitando respostas incoerentes.

**Arquivo:** `app/threat_analysis/guardrails/architecture_diagram_validator.py`

## Objetivo

- Receber o conteúdo bruto da imagem (`image_bytes`).
- Usar um modelo de visão (vision LLM) para classificar a imagem.
- Se for **diagrama de arquitetura**: não levanta exceção; o fluxo segue.
- Se **não** for: levantar **`ArchitectureDiagramValidationError`** com mensagem em português e detalhes (reason do LLM, resultado bruto).

## O que é considerado diagrama de arquitetura

O prompt do guardrail define que um diagrama de arquitetura deve mostrar:

- **Componentes de sistema:** Users, Servers, Databases, Gateways, Load Balancers, APIs, etc.
- **Conexões e fluxos de dados** entre componentes.
- **Trust boundaries:** VPCs, redes, subnets.

## O que não é aceito

- Diagramas de sequência (UML com atores e mensagens no tempo).
- Fotos ou screenshots de ambientes reais.
- Fluxogramas ou diagramas de processo.
- Ilustrações genéricas ou clipart.
- Texto puro ou documentos.

## Fluxo

1. **Entrada:** `image_bytes: bytes`, `settings: Settings`.
2. **Chamada:** `run_vision_with_fallback()` com:
   - Ordem: Gemini → OpenAI → Ollama.
   - Prompt fixo `GUARDRAIL_PROMPT`.
   - **Sem cache** (`cache_get=None`, `cache_set=None`) para que cada imagem seja reavaliada.
   - Validação `_validate_guardrail_result`: resultado deve ser um `dict` sem `"error"` e com a chave `"is_architecture_diagram"`.
3. Se a resposta contiver `"error"`: o guardrail **não** bloqueia; apenas registra warning e **permite** a imagem (fail-open para não travar o usuário em falhas de LLM).
4. Leitura de `is_architecture_diagram` (aceita `True` ou string `"true"`) e `reason`.
5. Se **não** for considerado diagrama de arquitetura:
   - Log de warning com a razão.
   - **Levanta** `ArchitectureDiagramValidationError(reason="Imagem não é um diagrama de arquitetura válido: {reason}", details={...})`.
6. Caso contrário: log de sucesso e retorno normal (`None`).

## Formato de resposta esperado do LLM

O LLM deve retornar **apenas** um JSON:

```json
{"is_architecture_diagram": true/false, "reason": "breve explicação em uma frase"}
```

O guardrail trata `is_architecture_diagram` como booleano ou string `"true"` (case insensitive).

## Exceção

- **Tipo:** `app.threat_analysis.exceptions.ArchitectureDiagramValidationError`
- **Quando:** Imagem classificada como não sendo diagrama de arquitetura.
- **Uso na API:** O handler em `app/main.py` mapeia essa exceção para resposta HTTP **400** com `detail` contendo a mensagem (ex.: "Imagem não é um diagrama de arquitetura válido: ...").

## Integração no pipeline

O guardrail é chamado **antes** do Diagram Agent, normalmente no endpoint que recebe o upload da imagem. Se não levantar exceção, a mesma imagem é repassada para o Diagram Agent; se levantar, a requisição é rejeitada com 400 e o pipeline de análise não é executado.
