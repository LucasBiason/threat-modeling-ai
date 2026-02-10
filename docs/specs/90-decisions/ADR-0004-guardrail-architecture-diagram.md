# ADR-0004 — Guardrail de validação de diagrama de arquitetura

**Status:** Accepted  
**Data:** 2026-02-05

## Contexto

A análise STRIDE/DREAD espera diagramas de arquitetura (componentes, conexões, limites de confiança). Usuários podem enviar imagens inadequadas: fotos, diagramas de sequência UML, flowcharts genéricos, ilustrações. O pipeline LLM pode produzir resultados incoerentes ou desperdiçar recursos.

## Decisão

- **Guardrail de tipo:** Antes do pipeline completo, uma chamada LLM vision leve valida se a imagem é um diagrama de arquitetura válido.
- **Prompt dedicado:** Pergunta se a imagem mostra componentes de arquitetura (servidores, bancos de dados, conexões) e NÃO é diagrama de sequência, foto ou flowchart.
- **Resposta estruturada:** JSON `{is_architecture_diagram: bool, reason: str}`.
- **Rejeição:** Se `is_architecture_diagram` for false, retorna HTTP 400 com a `reason` do LLM.
- **Fallback:** Se a validação LLM falhar (erro de provider), permite prosseguir para evitar bloquear o fluxo.
- **Dummy pipeline:** Guardrail não é executado quando `use_dummy_pipeline=true` (testes unitários).

## Alternativas consideradas

- **Sem guardrail:** Desperdício de recursos e resultados ruins para inputs inválidos.
- **Heurísticas apenas:** Difícil detectar diagrama de sequência vs arquitetura sem LLM.
- **Bloquear em falha do guardrail:** Poderia bloquear usuários legítimos se LLM falhar.

## Consequências

- **Positivas:** Reduz análises inúteis; feedback claro ao usuário; economiza tempo de processamento.
- **Negativas:** Uma chamada LLM extra por análise; latência adicional (~2–10s).

## Referências

- [ADR-0003](ADR-0003-stride-rag-guardrails.md) — RAG e guardrails para STRIDE
- `threat-analyzer/app/threat_analysis/guardrails/architecture_diagram_validator.py`
