# ADR-0003 — STRIDE com RAG e guardrails

**Status:** Accepted  
**Data:** 2026-01-27  
**Atualizado:** 2026-02-03

## Contexto

A análise STRIDE/DREAD é realizada por agents (StrideAgent, DreadAgent). Para enriquecer as respostas e reduzir alucinações, a base de conhecimento STRIDE/DREAD deve ser usada pelo LLM.

## Decisão

- **RAG (Retrieval Augmented Generation):** Base de conhecimento em `docs/knowledge-base/` (Markdown: stride-threats, dread-scoring, guias visuais, UK Gov, Microsoft, OWASP). TextLoader + RecursiveCharacterTextSplitter + ChromaDB; embeddings Google. Conteúdo capturado de material didático e estruturado por LLM.
- **StrideAgent:** Usa RAG para recuperar chunks relevantes; injeta no contexto do prompt do LLM.
- **Guardrails (chatbot futuro):** Limitar respostas ao tema modelagem de ameaças, STRIDE, DREAD e ao diagrama/relatório analisado.

RAG implementado no StrideAgent. Chatbot com guardrails opcional para após MVP.

## Alternativas consideradas

- **LLM livre:** Respostas inconsistentes ou fora do escopo.
- **RAG + guardrails:** Respostas ancoradas no material; menor risco de alucinação.

## Consequências

- **Positivas:** Respostas alinhadas a STRIDE/DREAD; melhor qualidade da análise.
- **Negativas:** Dependência de qualidade do material indexado; configuração de KNOWLEDGE_BASE_PATH.

## Referências

- docs/knowledge-base/README.md
- docs/knowledge-base/METODOLOGIA_CAPTACAO.md
