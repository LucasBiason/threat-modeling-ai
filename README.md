# Threat Modeling AI - Modelagem de Ameaças Automatizada

**Desafio Técnico:** Sistema de modelagem de ameaças automatizada usando Computer Vision, Graph Theory e STRIDE/DREAD.

## Visão Geral

Este projeto implementa um sistema completo de análise de ameaças em diagramas de arquitetura usando:

- **YOLO** para detecção de componentes (treino em datasets Roboflow/Kaggle)
- **LLM Vision** (Gemini → OpenAI → Ollama) para análise de diagramas com fallback multi-provider
- **NetworkX** para construção de grafo arquitetural
- **STRIDE** para análise de ameaças com RAG
- **DREAD** para priorização de riscos

## Escopo Atual

- **Backend:** threat-analyzer (análise STRIDE/DREAD) e threat-service (upload assíncrono, Celery, PostgreSQL)
- **Frontend:** threat-frontend — upload de diagramas, listagem de análises, detalhe com polling
- **Notebooks:** treino YOLO, download datasets, integração LLM, RAG (Docling + ChromaDB)
- **Datasets:** Roboflow (AWS/Azure System Diagrams) e Kaggle (formato VOC, conversão automática para YOLO)

## Estrutura do Projeto

```
threat-modeling-ai/
├── threat-analyzer/         # Servico de analise (STRIDE, DREAD, LLM)
├── threat-service/         # API principal (upload, Celery, PostgreSQL)
├── threat-frontend/        # UI React (Vite, Tailwind)
├── notebooks/               # Notebooks e scripts (treino, download, RAG)
│   ├── scripts/
│   │   ├── download/        # prepare_roboflow, prepare_kaggle (um comando por base)
│   │   ├── rag_processing/  # process_knowledge_base (input_files -> output_files + tar.gz)
│   │   └── train/           # train_yolo, paths (YOLO 11; best.pt onde e gerado)
│   ├── knowledge-base/      # Base RAG (input_files + output_files)
│   ├── models/              # yolo11n.pt e pesos por fonte
│   ├── dataset/             # Datasets (roboflow/, kaggle/) - gitignore
│   ├── outputs/             # Saidas de treino - gitignore
│   └── requirements.txt
├── configs/                 # .env unico (injetado via Docker)
├── private-context/         # Documentacao e planejamento (AGENTS.md, docs/)
├── scripts/                 # install_local_llm.sh
└── docker-compose.yml
```

## Como Usar

### 1. Setup (ambientes separados)

| Comando                | Descrição                                                                       |
| ---------------------- | ------------------------------------------------------------------------------- |
| `make setup`           | Setup completo (backend + frontend + notebooks)                                 |
| `make setup-backend`   | Só backend (threat-analyzer + threat-service em `.venv`)                        |
| `make setup-frontend`  | Só threat-frontend (`npm install` em threat-frontend/)                          |
| `make setup-notebooks` | Só notebooks (libs YOLO/Jupyter/RAG + kernel **"Python (threat-modeling-ai)"**) |

**Requirements por componente:**

- Backend: `threat-analyzer/requirements.txt` + `threat-service/requirements.txt`
- Frontend: `threat-frontend/package.json`
- Notebooks: `notebooks/requirements.txt`

### 2. Datasets

```bash
make download-roboflow   # Roboflow (requer ROBOFLOW_API_KEY em configs/.env)
make download-kaggle     # Kaggle ~33GB (requer kaggle CLI; inclui VOC→YOLO e verificação)
```

Datasets em `notebooks/dataset/roboflow/` e `notebooks/dataset/kaggle/`.

### 3. RAG (base de conhecimento)

A fonte é `notebooks/knowledge-base/input_files/`. O processamento gera `output_files/` (gitignore) e **copia para** `threat-analyzer/app/rag_data/` (pasta versionada com .gitkeep; conteúdo não commitado):

```bash
make process-rag-kb   # Converte PDF/DOCX/PNG → MD e popula app/rag_data do analyzer
```

O analyzer lê de `threat-analyzer/app/rag_data/`. Execute após adicionar documentos em `input_files/`.

### 4. Treinar YOLO

O treino **trava o kernel Jupyter** — execute no terminal:

```bash
make train-roboflow
# ou
make train-kaggle
# ou
python -m notebooks.scripts.train.train_yolo --dataset roboflow --epochs 200
```

Pesos ficam em `notebooks/outputs/<fonte>/weights/best.pt`; use esse caminho nos notebooks.

### 5. Rodar o sistema (apenas Docker)

Crie `configs/.env` a partir de `configs/.env.example` e defina as credenciais. Nunca commite `configs/.env`.

```bash
make run                 # Stack com logs no terminal
make run-detached        # Stack em background (producao)
make install-local-llm   # Sobe Ollama, baixa modelos vision e verifica (um comando)
```

### 6. Testes e lint (apenas nos Makefiles de cada servico)

```bash
make -C threat-analyzer test
make -C threat-analyzer lint
make -C threat-modeling-api test
make -C threat-modeling-api lint
make -C frontend lint
```

O Makefile na raiz nao tem alvos test/lint/clean.

**threat-modeling-api:** testes requerem PostgreSQL. Crie `createdb threat_modeling_test` ou defina `TEST_DATABASE_URL`.

### 7. Pre-commit

```bash
pip install pre-commit && pre-commit install
```

Em todo commit e executado `scripts/pre_commit.sh` (lint em threat-modeling-shared e nos tres servicos, testes em threat-analyzer e threat-modeling-api).

## Notebooks

| Notebook                           | Descrição                       |
| ---------------------------------- | ------------------------------- |
| `00-treinamento-roboflow.ipynb`    | Treino YOLO no dataset Roboflow |
| `01-treinamento-kaggle.ipynb`      | Treino YOLO no dataset Kaggle   |
| `02-integracao-llm-fallback.ipynb` | Integração LLM com fallback     |
| `03-docling-rag-prep.ipynb`        | Docling + RAG (ChromaDB)        |

Kernel Jupyter: **"Python (threat-modeling-ai)"** (após `make setup-notebooks`).

## Tecnologias

- **Backend:** FastAPI, Celery, Redis, PostgreSQL, LangChain, ChromaDB
- **Frontend:** React, Vite, Tailwind, Framer Motion
- **Notebooks:** Python 3.10+, YOLOv8 (Ultralytics), PyTorch, Jupyter, Docling
- **LLM:** Gemini, OpenAI, Ollama (vision)

## Licença

MIT

---

_Modelagem de ameaças automatizada em diagramas de arquitetura._
