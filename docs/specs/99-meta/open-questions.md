# Open Questions — Threat Modeling AI

Perguntas em aberto que impactam requisitos ou design. Atualizado conforme o projeto.

| ID     | Pergunta                                                                                     | Status                                                      |
| ------ | -------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| OQ-001 | Qual best.pt (Roboflow vs Kaggle) usar como padrão quando houver integração YOLO no backend? | Aberta (fora do escopo MVP)                                 |
| OQ-002 | Limiar de confiança para eventual fallback LLM quando YOLO for integrado?                    | Aberta (fora do escopo MVP)                                 |
| OQ-003 | Escolha de provedores LLM em produção (apenas OpenAI, ou Gemini+OpenAI+Ollama)?              | **Resolvido:** Fallback sequencial Gemini → OpenAI → Ollama |

Quando uma pergunta for resolvida, atualizar status e registrar a decisão (ou ADR) na documentação.
