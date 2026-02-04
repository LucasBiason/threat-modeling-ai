# Threat Modeling AI - Modelagem de Ameaças Automatizada

**Desafio Técnico:** Sistema de modelagem de ameaças automatizada usando Computer Vision, Graph Theory e STRIDE/DREAD.

**Notion (Estudos):** O card deste projeto está no database Studies. Atualizações via script `notion-automation-suite/scripts/update_study_cards_ml_spam_and_threat_modeling.py` (busca por título "Threat Modeling AI") ou `Trabalho/Astracode/Scripts/atualizar_cards_projetos_finalizados_notion.py`. Documentação completa do contexto (para o card e referência): `docs/CONTEXTO_PROJETO_NOTION.md`.

## Visão Geral

Este projeto implementa um sistema completo de análise de ameaças em diagramas de arquitetura usando:
- **YOLO** para detecção de componentes
- **OpenCV** para detecção de boundaries e conexões
- **NetworkX** para construção de grafo arquitetural
- **STRIDE** para análise de ameaças
- **DREAD** para priorização de riscos

## Escopo atual

- **Agora:** apenas **dataset real** (ex.: Roboflow AWS/Azure System Diagrams) e **treinamento** do modelo YOLO.
- **Diagramas sintéticos** (geração para testes): isolados para **outro momento**.
- **Diagramas reais** (captados na internet): no futuro, pasta específica → passar numa **LLM** para insights → usar o **relatório** como base para avaliar o quanto o projeto se aproxima do correto. Ver `rascunho/Documentacao/DIAGRAMAS_SINTETICOS_E_REAIS.md`.

## Estrutura do Projeto

```
threat-modeling-ai/
├── notebooks/              # Notebooks (análise base, treino, detecção)
├── dataset/                # Dataset (real: train/val/test ou export Roboflow)
├── model/                  # Treinamento e inferência YOLO
├── vision/                 # Detecção de boundaries e conexões
├── graph/                  # Construção de grafo arquitetural
├── stride_engine/          # Engine STRIDE e DREAD
├── Documentacao/           # Docs (datasets, diagramas sintéticos/reais)
├── rascunho/               # Código e docs em migração para a raiz
└── ...
```

## Como Usar

### 1. Setup completo (ambiente + dataset)

Na raiz do projeto:

```bash
make setup-notebooks
```

Isso executa:
1. **scripts/setup_venv_kernel.sh** – cria `.venv`, instala dependências e registra o kernel Jupyter **"Python (threat-modeling-ai)"**.
2. **scripts/download_dataset.py** – baixa o dataset AWS and Azure System Diagrams (Roboflow) em formato YOLOv8 para `dataset/` na raiz (requer `configs/.env` com `ROBOFLOW_API_KEY`).

### 2. Apenas ambiente (.venv + kernel)

```bash
make setup-venv
# ou
./scripts/setup_venv_kernel.sh
```

Ative com: `source .venv/bin/activate`. No Jupyter/Lab, selecione o kernel **"Python (threat-modeling-ai)"**.

### 3. Apenas download do dataset

```bash
make download-dataset
# ou (com .venv ativo)
python scripts/download_dataset.py
```

Requer `configs/.env` com `ROBOFLOW_API_KEY`. O dataset vai para **`dataset/`** na raiz do projeto (uma única pasta).

### 4. Treinar o modelo YOLO

O **treino é feito no notebook** (passo a passo didático). Abra `notebooks/00-analise-base-treino-componentes.ipynb` e execute as células na ordem; o **Passo 4** contém o treino (usa `dataset/data.yaml` e salva pesos em `runs/detect/train/weights/best.pt`). Os scripts na raiz são apenas para **download** e **validação** do dataset.

### 6. Executar Pipeline Completo

Quando migrarmos o código para a raiz:

```bash
python main.py --input diagram.png
```

Por enquanto o pipeline está em `rascunho/main.py`.

## Notebooks (por etapas)

- **`notebooks/00-analise-base-treino-componentes.ipynb`** – Análise da base de treino e **imagem → detecção de componentes e ligações** (componentes e conexões).
- **`rascunho/notebooks/`** – Notebooks de referência (dataset sintético, YOLO, STRIDE, DREAD, pipeline) em `rascunho/`.

## Tecnologias

- Python 3.10+
- YOLOv8 (Ultralytics)
- OpenCV
- NetworkX
- Streamlit
- OWASP pytm

## Licença

MIT

---

*Modelagem de ameaças automatizada em diagramas de arquitetura.*

