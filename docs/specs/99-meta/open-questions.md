# Open Questions — Threat Modeling AI

| ID     | Pergunta | Status |
|--------|----------|--------|
| OQ-001 | Qual best.pt usar como padrão: Roboflow (`outputs/mvp_roboflow/`) ou Kaggle (`outputs/mvp_kaggle/`)? | Open |
| OQ-002 | Qual limiar de confiança abaixo do qual disparar fallback LLM (quando YOLO integrado)? | Open |
| OQ-003 | Escolha final: apenas OpenAI, ou Gemini+OpenAI em combo com fallback? | **Resolvido:** Gemini → OpenAI → Ollama (fallback sequencial) |
