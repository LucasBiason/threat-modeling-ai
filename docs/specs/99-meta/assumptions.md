# Premissas — Threat Modeling AI

Premissas explícitas usadas nas especificações e no desenho.

---

- **A1.** O usuário envia imagens de diagramas de arquitetura (cloud, sistemas); imagens inadequadas (fotos, diagramas de sequência, flowcharts genéricos) podem ser rejeitadas pelo guardrail.
- **A2.** O processamento pode levar de dezenas de segundos a alguns minutos; o fluxo é assíncrono (upload → resposta imediata → processamento em background → notificação/consulta).
- **A3.** Provedores de LLM (Gemini, OpenAI, Ollama) podem estar disponíveis ou configurados; o analyzer implementa fallback sequencial.
- **A4.** A base RAG (knowledge-base) é preparada offline (notebooks) e disponibilizada ao threat-analyzer em runtime (ex.: volume ou cópia em rag_data).
- **A5.** Ambiente local e produção usam Docker Compose (ou equivalente); configuração via `configs/.env`; secrets nunca commitados.
- **A6.** Frontend consome apenas a API do orquestrador; não há chamada direta do browser ao threat-analyzer.
- **A7.** Uma análise gera no máximo uma notificação de conclusão (em geral); o modelo de dados permite várias notificações por análise para evolução futura.
