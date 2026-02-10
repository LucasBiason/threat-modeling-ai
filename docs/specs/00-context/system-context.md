# System Context — Threat Modeling AI

## Visão geral

O **Threat Modeling AI** é um sistema de análise de ameaças automatizada em diagramas de arquitetura (cloud, AWS, Azure, etc.). O usuário envia uma imagem do diagrama; o sistema identifica componentes e conexões e gera análise STRIDE com priorização DREAD, entregando um relatório de vulnerabilidades e mitigações.

## Componentes do sistema

| Componente                 | Responsabilidade                                                                                                                                                                                |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Usuário**                | Faz upload do diagrama, acompanha o processamento e consulta o relatório de ameaças.                                                                                                            |
| **Frontend**               | Interface web: upload, listagem de análises, detalhe com polling, notificações e exibição do relatório STRIDE/DREAD.                                                                            |
| **threat-modeling-api**    | Orquestrador: recebe upload (POST /api/v1/analyses), persiste análise e imagem, dispara processamento assíncrono via Celery, expõe listagem, detalhe, imagem, logs e notificações.              |
| **threat-analyzer**        | Microserviço de análise: recebe imagem via HTTP (POST /api/v1/threat-model/analyze), executa pipeline LLM (Diagram → STRIDE → DREAD), retorna JSON com componentes, conexões, ameaças e scores. |
| **Celery (worker + beat)** | Processamento em background: busca análises EM_ABERTO, chama o threat-analyzer, atualiza status e resultado, cria notificações.                                                                 |
| **PostgreSQL**             | Persistência de análises, notificações e metadados.                                                                                                                                             |
| **Redis**                  | Broker e backend do Celery.                                                                                                                                                                     |

## Atores externos

- **Usuário final:** interage com o frontend (upload e consulta).
- **Provedores de LLM:** Google Gemini, OpenAI, Ollama — utilizados pelo threat-analyzer quando o pipeline LLM está ativo.

## Integrações

- Frontend ↔ threat-modeling-api (REST).
- threat-modeling-api ↔ threat-analyzer (HTTP, interno).
- threat-modeling-api ↔ PostgreSQL e Redis.
- threat-analyzer ↔ ChromaDB (RAG) e APIs de LLM (Gemini, OpenAI, Ollama).

## O que está fora do escopo (contexto atual)

- Integração YOLO no backend (pipeline atual é 100% LLM; treino YOLO permanece nos notebooks para uso futuro).
- Chatbot com RAG (guardrails previstos para fase posterior).
- Exportação PDF (opcional).
