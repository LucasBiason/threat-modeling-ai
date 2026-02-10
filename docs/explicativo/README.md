# Documentação explicativa do projeto — Threat Modeling AI

Documentação técnica e de fluxo para **apresentação e explicação** do projeto. Base para demos, onboarding e entendimento do threat-analyzer e do pipeline de análise.

| Documento                                                              | Conteúdo                                                                                                                                                     |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [fluxo-basico-analise.md](fluxo-basico-analise.md)                     | Fluxo completo: construção da base RAG, subida da API, testes com script e curl (request/response), casos de sucesso e erro.                                 |
| [threat-model-service.md](threat-model-service.md)                     | Classe `ThreatModelService`: orquestração do pipeline (Diagram → STRIDE → DREAD), métodos, guardrail, agregação de risco, parsers e injeção de dependências. |
| [llm-module.md](llm-module.md)                                         | Módulo LLM: arquitetura de fallback entre múltiplos provedores (Gemini, OpenAI, Ollama), cache Redis, fluxos de visão/texto e motivo de cada decisão.        |
| [stride-agent.md](stride-agent.md)                                     | STRIDE Agent: identificação de ameaças STRIDE, uso de RAG, cache e integração no pipeline.                                                                   |
| [diagram-agent.md](diagram-agent.md)                                   | Diagram Agent: extração de componentes, conexões e trust boundaries a partir da imagem (vision LLM).                                                         |
| [dread-agent.md](dread-agent.md)                                       | DREAD Agent: pontuação de risco DREAD por ameaça e integração no pipeline.                                                                                   |
| [architecture-diagram-validator.md](architecture-diagram-validator.md) | Guardrail: validação de que a imagem é um diagrama de arquitetura antes do pipeline.                                                                         |

Specs, requisitos e ADRs ficam em [docs/specs/](../specs/).
