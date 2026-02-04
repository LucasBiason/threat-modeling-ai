# Architecture — Threat Modeling AI

## Fluxo de alto nível

1. **Entrada:** Usuário envia diagrama (imagem) via frontend.
2. **API:** POST `/api/v1/threat-model/analyze` recebe o arquivo (multipart/form-data) e opcionalmente `confidence`, `iou`.
3. **Pipeline:**
   - Se `USE_DUMMY_PIPELINE=true`: DummyPipeline (dados fixos) — apenas para testes unitários.
   - Caso contrário:
     - **Stage 1 — DiagramAgent:** LLM vision (Gemini/OpenAI/Ollama) extrai componentes e conexões; fallback sequencial se um provider falhar.
     - **Stage 2 — StrideAgent:** RAG sobre `docs/knowledge-base/`; LLM identifica ameaças STRIDE por componente/conexão; fallback multi-LLM.
     - **Stage 3 — DreadAgent:** LLM aplica DREAD às ameaças; fallback multi-LLM.
4. **Relatório:** Retorna `model_used`, `components`, `connections`, `threats` (com dread_score), `risk_score` (0–10), `risk_level`, `processing_time`.

## Componentes

- **Frontend:** Upload, sidebar/drawer (Confidence, IoU), botão Analisar, preview, overlay de scan, dashboard com Risk Score e cards STRIDE em accordion (severidade, mitigação). Referência: vídeo 1000088277.mp4.
- **Backend API:** Orquestra pipeline (Dummy ou agents); expõe POST `/api/v1/threat-model/analyze`; health em `/health`, `/health/ready`, `/health/live`.
- **DiagramAgent:** LLM vision com fallback (Gemini → OpenAI → Ollama); extrai componentes e conexões.
- **StrideAgent:** RAG (ChromaDB + docs/knowledge-base) + LLM; identifica ameaças STRIDE.
- **DreadAgent:** LLM; pontua ameaças com DREAD.
- **RAG:** TextLoader sobre `.md` em `docs/knowledge-base/`; chunk_size 800, overlap 80; embeddings Google; ChromaDB.
- **YOLO (futuro):** Treino via `notebooks/train_yolo.py`; modelos em `outputs/mvp_roboflow/` e `outputs/mvp_kaggle/`. Integração híbrida prevista.

## Decisões

- Pipeline pluggável (Dummy, LLM, futuramente YOLO+LLM).
- API-first; frontend consome API.
- Multi-LLM com fallback sequencial (try → validate → next provider).
- RAG para enriquecer STRIDE; sem dependência de `unstructured`.
- Config em `configs/.env`; Docker monta `docs/knowledge-base` em `/kb`.
