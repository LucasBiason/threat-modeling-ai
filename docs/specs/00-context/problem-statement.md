# Problem Statement — Threat Modeling AI

## Problema

Equipes de segurança e desenvolvimento precisam analisar diagramas de arquitetura (cloud, on-premises) para identificar ameaças de forma sistemática. Fazer isso manualmente com STRIDE/DREAD é trabalhoso e inconsistente. Não existe uma ferramenta única que receba o diagrama em imagem e devolva um relatório estruturado de ameaças com priorização.

## Objetivo

Oferecer um sistema que:

1. **Receba** uma imagem de diagrama de arquitetura (PNG, JPEG, WebP, GIF).
2. **Identifique** componentes e conexões no diagrama (via pipeline LLM vision).
3. **Gere** análise de ameaças STRIDE com pontuação DREAD.
4. **Entregue** um relatório utilizável (risk score, risk level, lista de ameaças com descrição e mitigação).

## Decisões de design (resumo)

- **Processamento assíncrono:** upload retorna imediatamente; análise roda em background (Celery); usuário acompanha por polling e notificações.
- **Pipeline LLM:** DiagramAgent (extração de componentes/conexões) → StrideAgent (ameaças STRIDE com RAG) → DreadAgent (pontuação DREAD). Fallback multi-provider: Gemini → OpenAI → Ollama.
- **Guardrail:** validação prévia (LLM vision) para rejeitar imagens que não sejam diagramas de arquitetura.
- **API-first:** frontend consome apenas a API do orquestrador; contrato estável para integrações futuras.

## Não descartar

- Trabalho de treino YOLO nos notebooks (Roboflow/Kaggle) e modelos em `notebooks/models/` — preservados para evolução futura; não fazem parte do fluxo atual do backend.
