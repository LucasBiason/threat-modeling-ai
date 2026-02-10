# Seleção e Validação de LLMs — Principal e Reservas

**Projeto:** Threat Modeling AI  
**Data:** 2026-02-08

---

## 1. Objetivo

Definir e validar qual LLM usar como **principal**, qual como **primeira reserva** e qual como **segunda reserva** no pipeline de análise de diagramas (DiagramAgent) e nos agentes de texto (StrideAgent, DreadAgent), para fechar o projeto até quinta-feira.

---

## 2. Ordem atual no código

Em `threat-analyzer/app/threat_analysis/agents/diagram/agent.py`:

```python
CONNECTION_ORDER = [GeminiConnection, OpenAIConnection, OllamaConnection]
```

Ou seja:

| Posição | Conexão | Papel | Modelo (config) |
|---------|---------|--------|------------------|
| 1 | **Gemini** | Principal | `primary_model` (default: gemini-1.5-pro) |
| 2 | **OpenAI** | Reserva 1 | `fallback_model` (default: gpt-4o) |
| 3 | **Ollama** | Reserva 2 | `ollama_model` (default: qwen2-vl) |

Config em `threat-analyzer/app/core/config.py` e variáveis de ambiente (ex.: `GOOGLE_API_KEY`, `OPENAI_API_KEY`, `OLLAMA_BASE_URL`).

---

## 3. Critérios de validação

Para **confirmar ou ajustar** principal e reservas, validar:

1. **Disponibilidade:** API key configurada (Gemini, OpenAI) ou Ollama rodando localmente.
2. **Visão (diagramas):** Resposta JSON válida com `components` e `connections` para imagens de teste (`notebooks/assets/diagram01.png`, `diagram02.png`).
3. **Tempo de resposta:** Latência aceitável (ex.: < 30s por análise de diagrama).
4. **Qualidade:** Componentes e conexões coerentes com o diagrama; sem erros de parsing.
5. **Custo (se aplicável):** Preferir ordem que minimize custo quando qualidade for equivalente (ex.: Gemini primeiro, OpenAI só em fallback).

---

## 4. Como testar

### 4.1 Notebook 02 (recomendado para validação manual)

- **Arquivo:** `notebooks/02-integracao-llm-fallback.ipynb`
- **O que faz:** Executa Gemini, OpenAI e Qwen (Ollama) nas mesmas imagens e permite comparar saídas.
- **Pré-requisitos:** `.env` com `GEMINI_API_KEY`/`GOOGLE_API_KEY` e `OPENAI_API_KEY`; Ollama rodando (`make ollama-up`) e modelo vision puxado (`make ollama-pull`).

### 4.2 Backend (threat-analyzer)

- Subir o backend com LLM real (não dummy):
  - `USE_DUMMY_PIPELINE=false` (default)
  - `configs/.env` com chaves definidas
- Enviar POST para o endpoint de análise (via Postman ou frontend) com uma imagem de diagrama.
- Verificar nos logs qual engine foi usada (“Success with Gemini…”, “Success with OpenAI…”, etc.) e se o JSON de resposta está correto.

### 4.3 Postman

- Coleção em `docs/Postman Collections/Threat Modeling AI.postman_collection.json`
- Environment: `Threat Modeling AI - Local.postman_environment.json`
- Chamar o endpoint de análise (threat-analyzer ou via threat-modeling-api conforme fluxo) e validar status e corpo da resposta.

### 4.4 Testes automatizados

- Testes de fallback em `threat-analyzer/tests/threat_analysis/llm/test_fallback.py` (mocks das conexões).
- Para teste de integração com LLM real, usar ambiente com chaves configuradas e validar que pelo menos um provider retorna sucesso.

---

## 5. Checklist de validação (até quinta)

- [ ] **Principal (Gemini):** Configurado, testado no notebook 02 e em uma análise real via API; resposta válida e tempo aceitável.
- [ ] **Reserva 1 (OpenAI):** Configurado; testado quando Gemini falha ou desligado; resposta válida.
- [ ] **Reserva 2 (Ollama):** Ollama no ar, modelo vision (qwen2.5-vl ou equivalente) baixado; testado quando OpenAI falha ou não configurado; resposta válida.
- [ ] **Ordem documentada:** Confirmar em README ou em docs que a ordem é Gemini → OpenAI → Ollama e que está alinhada com o código.
- [ ] **Config e .env.example:** Garantir que `configs/.env.example` (e README) descrevem as variáveis necessárias para as três engines.

---

## 6. Referências

- `threat-analyzer/app/threat_analysis/llm/fallback.py` — lógica de fallback
- `threat-analyzer/app/threat_analysis/agents/diagram/agent.py` — CONNECTION_ORDER
- `threat-analyzer/app/core/config.py` — primary_model, fallback_model, ollama_model
- `notebooks/02-integracao-llm-fallback.ipynb` — comparativo Gemini vs OpenAI vs Qwen
- ADR-0001 — Arquitetura híbrida YOLO + LLM
- open-questions.md — OQ-003 (Gemini+OpenAI+Ollama resolvido)
