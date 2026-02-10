# STRIDE Agent

## Visão geral

O **STRIDE Agent** é o agente responsável por identificar ameaças no modelo **STRIDE** a partir dos dados do diagrama de arquitetura (componentes, conexões, trust boundaries). Opcionalmente usa **RAG** (base de conhecimento em `app/rag_data`) para enriquecer o contexto do LLM. O retriever RAG é obtido via **RAGService** (propriedade com cache) e pode ser aquecido no **startup** da aplicação.

**Arquivo:** `app/threat_analysis/agents/stride/agent.py`

## Objetivo

- Receber o resultado do Diagram Agent (objeto com `components`, `connections`, `boundaries`).
- Opcionalmente recuperar contexto relevante da base RAG (arquivos `.md` em `app/rag_data`).
- Gerar uma lista de ameaças STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) com descrição e mitigação.
- Retornar uma lista de objetos com `component_id`, `threat_type`, `description`, `mitigation`.

## Categorias STRIDE

| Sigla | Categoria              | Descrição                                    |
| ----- | ---------------------- | -------------------------------------------- |
| **S** | Spoofing               | Fingir ser outra entidade                    |
| **T** | Tampering              | Modificar dados ou código sem autorização    |
| **R** | Repudiation            | Negar ter realizado uma ação                 |
| **I** | Information Disclosure | Expor informações a quem não deve ter acesso |
| **D** | Denial of Service      | Tornar o sistema indisponível                |
| **E** | Elevation of Privilege | Obter acesso ou capacidades não autorizados  |

## Base RAG e RAGService

- A base de conhecimento RAG fica em **`app/rag_data`** (path configurável por `settings.knowledge_base_path`).
- O **RAGService** (`app/services/rag_service.py`) constrói o retriever com persistência Chroma em disco (`rag_data/chroma_db`) e expõe `get_retriever()` com cache por processo.
- O StrideAgent usa uma **propriedade** `_retriever` que delega ao `RAGService.get_retriever()`, evitando construção a cada requisição.
- Apenas arquivos **`.md`** são carregados; documentos são fragmentados com `RecursiveCharacterTextSplitter` e indexados com Chroma e embeddings Google. O retriever busca trechos relevantes antes de montar o prompt do STRIDE.

## Cache do RAG e warm no startup

- O retriever RAG **não** é construído a cada requisição: o **RAGService** mantém cache em memória por processo e, quando possível, carrega o vectorstore do disco (Chroma persist).
- O **StrideAgent** acessa o retriever via a propriedade `_retriever`, que chama `self._rag_service.get_retriever()`.
- No **startup** da aplicação FastAPI, o **lifespan** (`_lifespan` em `app/main.py`) chama `RAGService(_settings).get_retriever()` para **aquecer** o cache na subida.

## Fluxo de análise

1. **Entrada:** `diagram_data: dict` com `components`, `connections`, `boundaries`.
2. Se houver retriever (via `self._retriever`), busca documentos relevantes com a query fixa: _"What are typical STRIDE threats for web applications and microservices?"_ e concatena até 3 trechos em `context` no system prompt.
3. **System prompt:** Inclui as categorias STRIDE e o `{context}` (vazio se sem RAG).
4. **User prompt:** Formata componentes, conexões e boundaries em texto e pede uma lista JSON de ameaças com `component_id`, `threat_type`, `description`, `mitigation`.
5. **Chamada:** `run_text_with_fallback()` com Gemini → OpenAI → Ollama, cache Redis (prefixo `"stride"`) e validação `_validate_stride_result` (resultado deve ser lista).
6. **Saída:** Lista de ameaças; em caso de falha, retorna `[]`.

## Fallback

- Se o RAG não estiver disponível (path inexistente ou erro), o agente segue **sem** contexto RAG.
- Se a chamada ao LLM falhar, retorna lista vazia `[]`.

## Cache LLM

- O resultado da análise STRIDE é cacheado em Redis com prefixo `"stride"`.
- O retriever RAG é cacheado pelo RAGService (por processo; Chroma em disco quando disponível).

## Ordem de conexões LLM

1. **Gemini**
2. **OpenAI**
3. **Ollama**

## Integração no pipeline

O STRIDE Agent é invocado **depois** do Diagram Agent e **antes** do DREAD. Recebe o JSON do diagrama e produz a lista de ameaças que o DREAD Agent pontua.
