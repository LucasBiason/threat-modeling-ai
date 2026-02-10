# Model Evaluation Report — YOLO best.pt

**Objetivo:** Saber se o modelo YOLO está adequado e em que condições usar fallback para LLM (quando integração YOLO estiver ativa).

**Data da última avaliação:** 2026-02-08

---

## 1. Modelo avaliado

| Campo | Valor |
|-------|--------|
| Caminho do weights | `notebooks/outputs/mvp_roboflow/weights/best.pt` (Roboflow) ou `notebooks/outputs/mvp_kaggle/weights/best.pt` (Kaggle) |
| Dataset de validação | Roboflow valid/test ou Kaggle valid/test |
| Métricas | mAP50, mAP50-95, Precision, Recall |

---

## 2. Resultados

| Métrica | Valor |
|---------|--------|
| mAP50 | Não preenchido (treino aquém; ver conclusão) |
| mAP50-95 | Não preenchido |
| Precision (média) | Não preenchido |
| Recall (média) | Não preenchido |

*Métricas podem ser preenchidas quando houver rodada formal de validação no notebook (e.g. `model.val(data=...)` no 00 ou 01).*

---

## 3. Teste qualitativo e conclusão dos notebooks

- **Notebooks de treino:** `00-treinamento-roboflow.ipynb`, `01-treinamento-kaggle.ipynb`
- **Problemas observados:**
  - Treinamento YOLO **ficou aquém do desejado** devido à qualidade/consistência das bases (Roboflow 203 classes, Kaggle VOC→YOLO) e ao tempo elevado de treino (especialmente Kaggle ~33 GB).
  - Componentes genéricos (“groups”), setas e confiança baixa em diagramas variados.
- **Conclusão:** Para o prazo do Hackathon (entrega até quinta), o **pipeline em produção usa LLM como principal** para análise de diagramas. O best.pt não é usado como primeira linha no pipeline atual; quando integração YOLO for reativada no futuro, usar fallback LLM quando confiança média < limiar.

Ver: `justificativa-uso-llm.md`.

---

## 4. Decisão para pipeline (atual)

- **Pipeline em uso:** 100% LLM (DiagramAgent → StrideAgent → DreadAgent). Ordem de fallback: **Gemini → OpenAI → Ollama** (ver `threat-analyzer/app/threat_analysis/agents/diagram/agent.py`, `CONNECTION_ORDER`).
- **Limiar de confiança para fallback (futuro, quando YOLO integrado):** a definir (ex.: 0.3 ou 0.5) em nova rodada de avaliação.
- **Qual best.pt usar como default (futuro):** mvp_roboflow ou mvp_kaggle — a definir quando híbrido for reativado.
- **Quando disparar requisição ao LLM (futuro):** confiança média < limiar OU muitas detecções "unknown".

---

## Referência

- Notebooks: `notebooks/00-treinamento-roboflow.ipynb`, `notebooks/01-treinamento-kaggle.ipynb`
- Script de treino: `notebooks/scripts/train/train_yolo.py --dataset roboflow` ou `--dataset kaggle`
- Ultralytics: `model.val(data=...)` para métricas no val set
- Justificativa uso LLM: `docs/specs/99-meta/justificativa-uso-llm.md`
- Validação LLMs: `docs/specs/99-meta/llm-selecao-validacao.md`