# Model Evaluation Report — YOLO best.pt

**Objetivo:** Saber se o modelo YOLO está adequado e em que condições usar fallback para LLM (quando integração YOLO estiver ativa).

## Onde preencher

Após rodar a avaliação no notebook ou em script dedicado, preencha abaixo e atualize a data.

**Data da última avaliação:** _a preencher_

---

## 1. Modelo avaliado

| Campo | Valor |
|-------|--------|
| Caminho do weights | `notebooks/outputs/mvp_roboflow/weights/best.pt` (Roboflow) ou `notebooks/outputs/mvp_kaggle/weights/best.pt` (Kaggle) |
| Dataset de validação | Roboflow valid/test ou Kaggle valid/test |
| Métricas | mAP50, mAP50-95, Precision, Recall |

---

## 2. Resultados (exemplo)

| Métrica | Valor |
|---------|--------|
| mAP50 | _a preencher_ |
| mAP50-95 | _a preencher_ |
| Precision (média) | _a preencher_ |
| Recall (média) | _a preencher_ |

---

## 3. Teste qualitativo

- **Diagramas testados:** _quantidade e tipos_
- **Onde o modelo falha:** componentes não reconhecidos, setas, "groups", confiança muito baixa
- **Conclusão:** best.pt adequado para _X_; para _Y_ usar fallback LLM

---

## 4. Decisão para pipeline

- **Limiar de confiança para fallback:** _ex.: 0.3 ou 0.5_
- **Qual best.pt usar como default:** mvp_roboflow ou mvp_kaggle
- **Quando disparar requisição ao LLM:** confiança média < limiar OU muitas detecções "unknown"

---

## Referência

- Notebooks: `notebooks/00-treinamento-roboflow.ipynb`, `notebooks/01-treinamento-kaggle.ipynb`
- Script de treino: `notebooks/train_yolo.py --dataset roboflow` ou `--dataset kaggle`
- Ultralytics: `model.val(data=...)` para métricas no val set
