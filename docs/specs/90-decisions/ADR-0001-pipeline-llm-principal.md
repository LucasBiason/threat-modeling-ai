# ADR-0001 — Pipeline LLM como principal mecanismo de análise

**Status:** Aceito  
**Data:** 2026-02-09 (atualizado)

## Contexto

O projeto precisa identificar componentes em diagramas de arquitetura e gerar análise STRIDE/DREAD. Existe trabalho de treino YOLO nos notebooks (Roboflow/Kaggle) e a possibilidade de usar LLMs com visão (Gemini, OpenAI, Ollama) para interpretar diagramas.

## Decisão

- **Pipeline em produção:** Usar **pipeline LLM** (DiagramAgent → StrideAgent → DreadAgent) como mecanismo principal de análise no threat-analyzer. Fallback multi-provider: Gemini → OpenAI → Ollama.
- **YOLO:** Preservado nos notebooks (treino, datasets, modelos em `notebooks/models/`). Integração YOLO no backend (ou abordagem híbrida) fica para fase futura, fora do escopo do MVP atual.
- **DummyPipeline:** Mantido para testes unitários quando `USE_DUMMY_PIPELINE=true`.

## Consequências

- **Positivas:** Entrega estável com LLM; sem dependência de modelo YOLO avaliado em produção; flexibilidade de provedores.
- **Negativas:** Custo e latência de APIs de LLM; treino YOLO não utilizado no fluxo atual do backend.

## Referências

- [problem-statement.md](../00-context/problem-statement.md)
- [architecture.md](../20-design/architecture.md)
