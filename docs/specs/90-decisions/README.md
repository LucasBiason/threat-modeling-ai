# 90 — Decisions (ADRs)

Architecture Decision Records atuais:

| ADR                                                                                      | Título                                                         |
| ---------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| [ADR-0001-pipeline-llm-principal.md](ADR-0001-pipeline-llm-principal.md)                 | Pipeline LLM como principal; YOLO preservado para fase futura. |
| [ADR-0002-api-first.md](ADR-0002-api-first.md)                                           | API-first (contrato REST estável; frontend consome API).       |
| [ADR-0003-stride-rag-guardrails.md](ADR-0003-stride-rag-guardrails.md)                   | STRIDE com RAG e guardrails.                                   |
| [ADR-0004-guardrail-architecture-diagram.md](ADR-0004-guardrail-architecture-diagram.md) | Guardrail de validação de diagrama de arquitetura.             |
| [ADR-0005-microservices-celery.md](ADR-0005-microservices-celery.md)                     | Microserviços e processamento assíncrono com Celery.           |

Decisões obsoletas (ex.: híbrido YOLO+LLM como entrega atual) foram removidas ou substituídas pelo estado atual do projeto.
