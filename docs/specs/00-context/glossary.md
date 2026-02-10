# Glossário — Threat Modeling AI

| Termo                                            | Definição                                                                                                                                     |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **STRIDE**                                       | Metodologia de classificação de ameaças: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege. |
| **DREAD**                                        | Modelo de priorização: Damage, Reproducibility, Exploitability, Affected users, Discoverability. Cada eixo 1–10; média compõe o risk score.   |
| **DiagramAgent**                                 | Agente LLM vision que extrai componentes e conexões a partir da imagem do diagrama.                                                           |
| **StrideAgent**                                  | Agente LLM que identifica ameaças STRIDE com suporte a RAG (base de conhecimento).                                                            |
| **DreadAgent**                                   | Agente LLM que aplica pontuação DREAD às ameaças identificadas.                                                                               |
| **RAG**                                          | Retrieval Augmented Generation — recuperação de trechos da base de conhecimento (STRIDE/DREAD) injetados no contexto do LLM.                  |
| **Guardrail**                                    | Validação prévia (ex.: imagem é diagrama de arquitetura?) para evitar processamento inválido.                                                 |
| **Orquestrador**                                 | threat-modeling-api: gerencia análises, filas e notificações; não executa o pipeline LLM.                                                     |
| **Analyzer**                                     | threat-analyzer: microserviço que executa o pipeline LLM e retorna o resultado da análise.                                                    |
| **EM_ABERTO / PROCESSANDO / ANALISADO / FALHOU** | Status do ciclo de vida de uma análise no orquestrador.                                                                                       |
