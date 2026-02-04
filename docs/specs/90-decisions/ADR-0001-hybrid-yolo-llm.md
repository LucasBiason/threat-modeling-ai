# ADR-0001 — Arquitetura híbrida YOLO + LLM (fallback)

**Status:** Accepted  
**Data:** 2026-01-27  
**Atualizado:** 2026-02-03

**Estado atual:** MVP usa pipeline LLM (DiagramAgent → StrideAgent → DreadAgent) ou DummyPipeline. Híbrido YOLO+LLM previsto para próxima fase, quando best.pt estiver avaliado e integrado ao backend.

## Contexto

O projeto precisa identificar componentes em diagramas de arquitetura e gerar análise STRIDE. Existe modelo YOLO treinado (best.pt) e a possibilidade de usar APIs de LLM (OpenAI, Gemini) para interpretação de diagramas. O professor aceita qualquer método desde que o resultado seja "identificar componentes e gerar análise".

## Decisão

Adotar arquitetura **híbrida**: executar YOLO primeiro no diagrama; se a confiança média for baixa ou houver muitas detecções "unknown"/não reconhecidas, fazer requisição a um LLM (GPT ou Gemini) para completar componentes e relações; em seguida mesclar saída YOLO com saída LLM (prioridade YOLO quando confiança alta). Objetivo: aproveitar o trabalho já treinado (best.pt) e cobrir casos em que o modelo local falha.

## Alternativas consideradas

- **Apenas YOLO:** Risco de muitos "groups" não reconhecidos; não descarta o treino, mas entrega pode ficar incompleta.
- **Apenas LLM:** Desperdiça o best.pt; custo e latência maiores; menos controle sobre o que foi treinado.
- **Híbrido:** Mantém YOLO como primeira linha; LLM como fallback; decisão baseada em limiar de confiança (a definir em model-evaluation-report).

## Consequências

- **Positivas:** Reaproveita best.pt; cobre falhas do modelo local; resultado alinhado ao requisito do professor.
- **Negativas:** Dois caminhos de inferência (YOLO + LLM); necessidade de definir limiar e lógica de merge; custo de API quando fallback é acionado.

## Referências

- docs/specs/99-meta/open-questions.md (OQ-002 limiar, OQ-003 OpenAI vs Gemini).
- docs/specs/99-meta/model-evaluation-report.md (quando usar fallback).
