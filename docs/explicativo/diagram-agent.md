# Diagram Agent

## Visão geral

O **Diagram Agent** é o agente responsável por analisar imagens de diagramas de arquitetura usando modelos de visão (vision LLMs). Ele extrai componentes, conexões e limites de confiança do diagrama e devolve um JSON estruturado para uso pelos agentes STRIDE e DREAD.

**Arquivo:** `app/threat_analysis/agents/diagram/agent.py`

## Objetivo

- Receber uma imagem (bytes) de um diagrama de arquitetura.
- Identificar **componentes** (Users, Servers, Databases, Gateways, Load Balancers, etc.) com `id`, `type` e `name`.
- Identificar **conexões** e fluxos de dados entre componentes (`from`, `to`, `protocol`).
- Identificar **trust boundaries** (ex.: VPCs, subnets públicas/privadas, DMZs).
- Retornar um único objeto JSON válido para consumo pelo pipeline.

## Fluxo

1. **Entrada:** `image_bytes: bytes` (conteúdo bruto da imagem).
2. **Chamada:** `run_vision_with_fallback()` com:
   - Ordem de conexões: Gemini → OpenAI → Ollama.
   - Prompt fixo `DIAGRAM_PROMPT`.
   - Validação `_validate_diagram_result`.
   - Cache Redis (prefixo `"diagram"`).
3. **Validação:** O resultado deve ser um `dict` sem chave `"error"` e com `"components"` sendo uma lista.
4. **Saída:** Objeto com `model`, `components`, `connections`, `boundaries`; em caso de falha, fallback com um componente genérico.

## Prompt

O prompt instrui o modelo a:

- Analisar o diagrama.
- Listar componentes com `id` único, `type` (User, Server, Database, Gateway, LoadBalancer, Cache, Queue, API, Service) e `name`.
- Listar conexões com `from`, `to` e `protocol` (HTTPS, HTTP, TCP, etc.).
- Listar trust boundaries por nome.

O retorno deve ser **apenas** um JSON no formato:

```json
{
  "model": "model_name",
  "components": [
    { "id": "unique_id", "type": "ComponentType", "name": "Display Name" }
  ],
  "connections": [
    { "from": "source_id", "to": "target_id", "protocol": "HTTPS/HTTP/TCP/etc" }
  ],
  "boundaries": ["boundary name 1", "boundary name 2"]
}
```

## Fallback

Se a análise falhar (LLM retorna erro ou validação falha):

- É retornado um objeto de fallback com:
  - `model`: `"Fallback/Error"`.
  - Um único componente: `{"id": "unknown_1", "type": "Unknown", "name": "Unanalyzed Component"}`.
  - `connections` e `boundaries` vazios.

Assim o pipeline não quebra e os agentes seguintes ainda recebem uma estrutura mínima.

## Cache

- O resultado da análise é cacheado em Redis com prefixo `"diagram"`.
- A chave depende do conteúdo da imagem e das configurações usadas em `run_vision_with_fallback`.
- Reduz chamadas repetidas ao LLM para o mesmo diagrama.

## Ordem de conexões LLM

1. **Gemini** (vision)
2. **OpenAI** (vision)
3. **Ollama** (vision)

## Integração no pipeline

O Diagram Agent é invocado **antes** do STRIDE. A saída dele (componentes, conexões, boundaries) é usada como entrada do Stride Agent para geração de ameaças, e as ameaças podem ser depois pontuadas pelo Dread Agent.
