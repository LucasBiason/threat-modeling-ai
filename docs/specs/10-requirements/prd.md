# PRD — Threat Modeling AI

## Visão

Sistema que recebe um diagrama de arquitetura (imagem), identifica componentes e conexões, e gera análise de ameaças STRIDE com priorização DREAD, entregando um relatório utilizável de forma assíncrona (upload → processamento em background → notificação e consulta).

## Escopo (in scope)

- Upload de diagrama (PNG, JPEG, WebP, GIF) via orquestrador (threat-modeling-api), com resposta imediata (201) e processamento em background.
- Detecção de componentes e conexões via pipeline LLM vision (DiagramAgent) no threat-analyzer, com fallback multi-provider (Gemini → OpenAI → Ollama). DummyPipeline para testes sem LLM.
- Análise STRIDE com RAG (base em knowledge-base) e pontuação DREAD (StrideAgent, DreadAgent).
- Orquestrador: POST /api/v1/analyses (upload), GET /analyses, GET /analyses/{id}, GET /analyses/{id}/image, GET /analyses/{id}/logs, GET /notifications/unread, POST /notifications/{id}/read. Celery para processamento em background.
- threat-analyzer: POST /api/v1/threat-model/analyze (imagem multipart) → JSON com components, connections, threats, risk_score, risk_level.
- Health: /health, /health/ready, /health/live em ambos os serviços.
- Frontend: upload assíncrono, listagem de análises, detalhe com polling e logs em tempo real, ícone de notificações, relatório STRIDE/DREAD em accordion.
- Guardrail de validação de diagrama de arquitetura antes do pipeline completo.
- Documentação e specs em docs/specs/ (estrutura Spec Driven).

## Escopo (out of scope para MVP)

- Integração YOLO no backend (pipeline atual é 100% LLM; notebooks de treino preservados).
- Chatbot com RAG (opcional para depois).
- Exportação PDF (opcional).

## Requisitos de alto nível

- Pipeline pluggável: DummyPipeline para testes; pipeline LLM (Diagram → STRIDE → DREAD) em produção.
- RAG STRIDE: base em knowledge-base (input_files → processamento Docling nos notebooks); ChromaDB no analyzer.
- API-first: frontend consome apenas threat-modeling-api; Postman em docs/Postman Collections/.
- Frontend conforme spec de UI/UX (design dark/glassmorphism, referência em 30-features).
- Multi-LLM com fallback: Gemini → OpenAI → Ollama; validação e retry em caso de falha.
