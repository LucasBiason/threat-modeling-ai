# ADR-0002 — API-first para o Cloud Architecture Security Analyzer

**Status:** Accepted  
**Data:** 2026-01-27

## Contexto

O frontend (upload de diagrama, resultados STRIDE) e possíveis integrações (chatbot, export PDF) precisam de um contrato estável. A documentação existente foi pensada para fluxo mais monolítico; o grupo do hackathon definiu uso de API para análise.

## Decisão

Adotar abordagem **API-first**: expor um contrato REST (ex.: POST /analyze para upload do diagrama e retorno de componentes, grafo, ameaças STRIDE, scores DREAD, relatório). O frontend consome essa API em vez de lógica local. Documentação (OpenAPI/Swagger) deve refletir o contrato. Opcional: POST /chat ou WebSocket para perguntas do usuário com guardrails.

## Alternativas consideradas

- **Frontend acoplado ao backend (Streamlit/script):** Mais simples para MVP, mas dificulta evolução e integração (ex.: mobile, Telegram).
- **API-first:** Contrato claro; frontend (React, vídeo 1000088277.mp4) pode ser desenvolvido em paralelo; facilita testes e integração.

## Consequências

- **Positivas:** Contrato explícito; frontend pode ser trocado ou multiplicado (web, mobile); documentação alinhada ao comportamento real.
- **Negativas:** Necessidade de manter API e documentação; upload de arquivo e tempo de análise exigem tratamento de timeout/feedback (ex.: loading no frontend).

## Referências

- docs/specs/20-design/api-contracts.md.
- docs/specs/30-features/frontend-ui-ux.md (comportamento do frontend).
