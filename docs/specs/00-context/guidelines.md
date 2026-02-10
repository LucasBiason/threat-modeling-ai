# Guidelines — Threat Modeling AI

Padrões de documentação, código e estrutura do projeto.

---

## Código

- **Python:** Ruff (lint e format), type hints, docstrings em APIs e lógica não óbvia.
- **TypeScript/React:** ESLint e convenções do projeto; componentes funcionais com hooks.

## Documentação

- Comentários apenas onde a lógica não for óbvia.
- Docstrings em funções e classes públicas.
- README na raiz e por serviço (como subir e executar).

## Estrutura de pastas

- **threat-modeling-api:** `app/<entidade>/` com controllers, routers, repositories, validators (padrão em camadas).
- **threat-analyzer:** `app/threat_analysis/` com agents, llm, pipeline, guardrails.
- **Testes:** espelhar `app/` — `tests/<pasta>/test_<modulo>.py` (ver 99-meta/test-conventions.md).

## Especificações (Spec Driven)

- **00-context:** contexto do sistema, problema, glossário, stack, guidelines.
- **10-requirements:** PRD e requisitos funcionais.
- **20-design:** arquitetura, contratos de API, modelo de dados, fluxos e sequências.
- **30-features:** specs por feature (ex.: frontend UI/UX).
- **90-decisions:** ADRs com contexto, decisão, alternativas e consequências.
- **99-meta:** perguntas abertas, convenções de teste, premissas e riscos.

## Configuração e secrets

- Variáveis de ambiente em `configs/.env` (gitignore).
- Exemplo: `configs/.env.example` sem valores sensíveis.
