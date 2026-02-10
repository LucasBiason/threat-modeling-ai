# Stack e bibliotecas — Threat Modeling AI

Documentação da stack e das principais libs por serviço. Atualizado conforme o projeto.

---

## Visão geral da stack

| Camada         | Tecnologia                        | Uso                                                                        |
| -------------- | --------------------------------- | -------------------------------------------------------------------------- |
| Frontend       | React 18 + Vite + TypeScript      | Interface: upload, listagem, detalhe, notificações, relatório STRIDE/DREAD |
| Orquestrador   | FastAPI + SQLAlchemy + Celery     | API REST, persistência, filas e processamento assíncrono                   |
| Analyzer       | FastAPI + LangChain               | Pipeline LLM (Diagram → STRIDE → DREAD), RAG, guardrails                   |
| Banco de dados | PostgreSQL 15                     | Análises, notificações, metadados                                          |
| Filas          | Redis 7 + Celery                  | Broker e backend de resultado do Celery                                    |
| LLMs           | Gemini, OpenAI, Ollama            | Fallback multi-provider no threat-analyzer                                 |
| RAG            | ChromaDB + TextLoader (LangChain) | Base de conhecimento STRIDE/DREAD no analyzer                              |

---

## threat-modeling-api (orquestrador)

| Lib        | Uso                                                           |
| ---------- | ------------------------------------------------------------- |
| FastAPI    | API REST, health, rotas de analyses e notifications           |
| SQLAlchemy | ORM, modelos Analysis e Notification                          |
| Celery     | Tarefas assíncronas (scan_pending_analyses, process_analysis) |
| Pydantic   | Validação de request/response                                 |
| PostgreSQL | Persistência (analyses, notifications)                        |
| Redis      | Broker e backend do Celery                                    |

---

## threat-analyzer (microserviço de análise)

| Lib                    | Uso                                                                     |
| ---------------------- | ----------------------------------------------------------------------- |
| FastAPI                | API REST, POST /api/v1/threat-model/analyze, health                     |
| LangChain              | Orquestração de chamadas LLM                                            |
| langchain-google-genai | Integração Gemini                                                       |
| langchain-openai       | Integração OpenAI                                                       |
| langchain-community    | TextLoader, ChromaDB                                                    |
| ChromaDB               | Vetorização e busca da base RAG                                         |
| Pydantic               | Schemas de request/response (AnalysisResponse, Component, Threat, etc.) |

Docling (conversão PDF/DOCX → Markdown para a base RAG) é usado nos notebooks de preparação da knowledge-base, não em runtime no analyzer.

---

## Frontend

| Lib          | Uso                |
| ------------ | ------------------ |
| React 18     | UI e estado        |
| Vite         | Build e dev server |
| TypeScript   | Tipagem            |
| Tailwind CSS | Estilização        |

---

## Infraestrutura (Docker Compose)

- **postgres:** imagem `postgres:15-alpine`, porta 5432.
- **redis:** imagem `redis:7-alpine`, porta 6379.
- **threat-analyzer:** build local, porta 8001:8000.
- **threat-modeling-api:** build local, porta 8000:8000, depende de postgres, redis e threat-analyzer.
- **celery-worker / celery-beat:** mesmo build do threat-modeling-api, comandos Celery.
- **frontend:** build local, porta 80, serve estático (nginx).
- **ollama:** opcional, imagem `ollama/ollama`, porta 11434, para LLM local.

Configuração única em `configs/.env`; injetada via Docker. Nunca commitar `configs/.env`.
