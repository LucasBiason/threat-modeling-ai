# System Context — Threat Modeling AI

## Onde estamos

O **Threat Modeling AI** (Cloud Architecture Security Analyzer) é um sistema de análise de segurança automatizada em diagramas de arquitetura (AWS, Azure, etc.). O sistema identifica componentes no diagrama e gera análise de ameaças baseada em STRIDE com priorização DREAD.

## Componentes e integrações

- **Usuário:** Faz upload do diagrama e consulta o relatório de vulnerabilidades.
- **Frontend:** Interface web (upload, parâmetros Confidence/IoU, análise, resultados STRIDE em accordion). Design: dark/glassmorphism, referência vídeo 1000088277.mp4.
- **API (backend):** POST `/api/v1/threat-model/analyze` recebe diagrama; orquestra pipeline (Dummy ou DiagramAgent → StrideAgent → DreadAgent); retorna componentes, conexões, ameaças, scores DREAD.
- **Pipeline:** Diagram → STRIDE → DREAD com LLM. `DummyPipeline` só quando `USE_DUMMY_PIPELINE=true` (testes unitários).
- **DiagramAgent:** LLM vision para extrair componentes e conexões do diagrama (Gemini/OpenAI/Ollama com fallback).
- **StrideAgent:** Análise STRIDE com RAG (base em `docs/knowledge-base/`), fallback multi-LLM.
- **DreadAgent:** Pontuação DREAD das ameaças, fallback multi-LLM.
- **RAG:** Base de conhecimento em `docs/knowledge-base/` (stride-threats, dread-scoring, guias visuais, UK Gov, Microsoft, OWASP). TextLoader + ChromaDB.
- **YOLO:** Treino fora do backend via `notebooks/train_yolo.py`; pesos em `outputs/mvp_roboflow/` ou `outputs/mvp_kaggle/`. Integração híbrida (YOLO + fallback LLM) prevista para próxima etapa.
- **Health:** `/health`, `/health/ready`, `/health/live`.

## Atores externos

- Usuário final (upload e consulta).
- Provedores de LLM (Google Gemini, OpenAI, Ollama) quando pipeline LLM está ativo.
