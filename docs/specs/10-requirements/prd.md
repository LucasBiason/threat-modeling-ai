# PRD — Threat Modeling AI

## Visão

Sistema que recebe um diagrama de arquitetura (imagem), identifica componentes e conexões, e gera análise de ameaças STRIDE com priorização DREAD, entregando um relatório utilizável.

## Escopo (in scope)

- Upload de diagrama (PNG, JPG, WEBP).
- Detecção de componentes via LLM vision (DiagramAgent) com fallback multi-provider (Gemini → OpenAI → Ollama). DummyPipeline para testes sem LLM.
- Análise STRIDE com RAG (base em `docs/knowledge-base/`) e DREAD scoring.
- API: POST `/api/v1/threat-model/analyze` → componentes, conexões, ameaças, risk_score, risk_level (JSON).
- Health: `/health`, `/health/ready`, `/health/live`.
- Frontend: upload, parâmetros (Confidence, IoU), análise, resultados (Risk Score, detecções STRIDE em accordion com severidade e mitigação).
- Treinamento YOLO via script (`notebooks/train_yolo.py`) para bases Roboflow e Kaggle; notebooks para testes.
- Documentação e specs em `docs/specs/` (00-context, 10-requirements, 20-design, 30-features, 90-decisions, 99-meta).

## Escopo (out of scope para MVP)

- Integração YOLO no backend (usar pipeline LLM ou Dummy).
- Chatbot com RAG (opcional para depois).
- Exportação PDF (opcional).

## Requisitos de alto nível

- Pipeline pluggável: DummyPipeline para testes; pipeline LLM (Diagram → STRIDE → DREAD) em produção.
- RAG STRIDE: base em `docs/knowledge-base/`, TextLoader, ChromaDB.
- API-first: frontend consome API; Postman em `docs/Postman Collections/`.
- Frontend conforme spec (vídeo 1000088277.mp4, design dark/glassmorphism).
- Multi-LLM com fallback: Gemini → OpenAI → Ollama; validação e retry em caso de falha.
