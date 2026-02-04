# Problem Statement — Threat Modeling AI

## Qual problema real estamos resolvendo

- **Objetivo:** Identificar os componentes no diagrama de arquitetura e gerar a análise de ameaças STRIDE com priorização DREAD.
- **Decisão de design:** Pipeline pluggável — DummyPipeline para testes; pipeline LLM (DiagramAgent → StrideAgent → DreadAgent) com fallback multi-provider (Gemini → OpenAI → Ollama); futuramente YOLO + fallback LLM para abordagem híbrida.
- **Não descartar:** O trabalho com YOLO (treino via `notebooks/train_yolo.py`) deve ser preservado; notebooks 00 e 01 para Roboflow e Kaggle; modelos em `outputs/mvp_roboflow/` e `outputs/mvp_kaggle/`.
- **Entrega:** Pipeline funcional com API, frontend e RAG. Prioridade: specs alinhadas, pipeline Dummy/LLM estável, integração YOLO quando modelo avaliado.
