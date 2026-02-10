# Especificações — Threat Modeling AI (Spec Driven)

Documentação de especificações seguindo a metodologia **Spec Driven**: contexto → requisitos → aceite → restrições → design → validação.

---

## Estrutura

| Pasta               | Conteúdo                                                                                             |
| ------------------- | ---------------------------------------------------------------------------------------------------- |
| **00-context**      | Contexto do sistema, problema, glossário, stack e guidelines.                                        |
| **10-requirements** | PRD e requisitos funcionais.                                                                         |
| **20-design**       | Arquitetura, contratos de API, modelo de dados (DBML/dbdiagram.io), fluxos e diagramas de sequência. |
| **30-features**     | Especificações por feature (ex.: frontend UI/UX).                                                    |
| **90-decisions**    | ADRs (Architecture Decision Records).                                                                |
| **99-meta**         | Perguntas abertas, premissas, convenções de teste.                                                   |

---

## Diagramas

- **Arquitetura e fluxos:** Mermaid (flowchart, sequenceDiagram) nos arquivos em `20-design/`.
- **Banco de dados:** DBML (compatível com [dbdiagram.io](https://dbdiagram.io)) em `20-design/data-model.md`; alternativa em Mermaid erDiagram no mesmo arquivo.

---

## Navegação rápida

- Visão do sistema: [00-context/system-context.md](00-context/system-context.md)
- Problema e objetivo: [00-context/problem-statement.md](00-context/problem-statement.md)
- Arquitetura e pipeline: [20-design/architecture.md](20-design/architecture.md)
- Modelo de dados: [20-design/data-model.md](20-design/data-model.md)
- Contratos de API: [20-design/api-contracts.md](20-design/api-contracts.md)
- Decisões: [90-decisions/README.md](90-decisions/README.md)
