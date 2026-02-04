.DEFAULT_GOAL := help

# =============================================================================
# Threat Modeling AI - Makefile
# =============================================================================

help:
	@echo "=============================================="
	@echo "  Threat Modeling AI - Comandos Disponíveis"
	@echo "=============================================="
	@echo ""
	@echo "SETUP:"
	@echo "  make setup              - Setup completo (venv + deps)"
	@echo "  make setup-venv         - Criar venv e instalar kernel Jupyter"
	@echo "  make setup-backend      - Instalar deps do backend"
	@echo "  make setup-frontend     - Instalar deps do frontend"
	@echo ""
	@echo "DATASETS:"
	@echo "  make download-roboflow  - Baixar dataset Roboflow (requer ROBOFLOW_API_KEY)"
	@echo "  make download-kaggle    - Baixar dataset Kaggle (~33GB, requer kaggle CLI)"
	@echo "  make verify-roboflow    - Verificar integridade do dataset Roboflow"
	@echo "  make verify-kaggle      - Verificar integridade do dataset Kaggle"
	@echo "  make convert-voc-yolo   - Converter VOC para YOLO (Kaggle raw/)"
	@echo ""
	@echo 	@echo "RUN:"
	@echo "  make run                - Rodar com docker-compose"
	@echo "  make ollama-up          - Subir só Ollama (comparativo LLM)"
	@echo "  make ollama-pull        - Baixar modelos vision (qwen2.5-vl, llava, deepseek-vl)"
	@echo "  make run-backend        - Rodar apenas backend (dev)"
	@echo "  make run-frontend       - Rodar apenas frontend (dev)"
	@echo ""
	@echo "TEST/LINT:"
	@echo "  make test               - Rodar testes"
	@echo "  make lint               - Rodar linters (ruff)"
	@echo ""

# -----------------------------------------------------------------------------
# SETUP
# -----------------------------------------------------------------------------

setup: setup-venv setup-backend setup-frontend
	@echo "✅ Setup completo!"

setup-venv:
	@echo "==> Criando venv e kernel Jupyter..."
	./scripts/setup_venv_kernel.sh

setup-backend:
	@echo "==> Instalando dependências do backend..."
	pip install -r backend/requirements.txt

setup-frontend:
	@echo "==> Instalando dependências do frontend..."
	cd frontend && npm install

# -----------------------------------------------------------------------------
# DATASETS
# -----------------------------------------------------------------------------

download-roboflow:
	@echo "==> Baixando dataset Roboflow..."
	python -m scripts.download.dataset_roboflow

download-kaggle:
	@echo "==> Baixando dataset Kaggle (pode demorar)..."
	python -m scripts.download.dataset_kaggle

verify-roboflow:
	@echo "==> Verificando dataset Roboflow..."
	python scripts/download/verify_dataset_roboflow.py

verify-kaggle:
	@echo "==> Verificando dataset Kaggle..."
	python scripts/download/verify_dataset_kaggle.py

convert-voc-yolo:
	@echo "==> Convertendo VOC para YOLO..."
	python scripts/convert_voc_to_yolo.py

extract-kaggle-zip:
	@echo "Uso: make extract-kaggle-zip ZIP=/caminho/para/arquivo.zip"
	@test -n "$(ZIP)" || (echo "❌ Defina ZIP=/caminho/para/arquivo.zip" && exit 1)
	python -m scripts.download.dataset_kaggle "$(ZIP)"

# -----------------------------------------------------------------------------
# RUN
# -----------------------------------------------------------------------------

run:
	docker-compose up --build

ollama-up:
	@echo "==> Subindo Ollama (só esse serviço)..."
	docker compose -f docker-compose.ollama.yml up -d
	@echo "Ollama em http://localhost:11434"
	@echo "Para baixar modelos: make ollama-pull"

ollama-pull:
	@echo "==> Baixando modelos vision (requer Ollama rodando)..."
	@docker compose -f docker-compose.ollama.yml exec ollama ollama pull qwen2.5vl || true
	@docker compose -f docker-compose.ollama.yml exec ollama ollama pull llava || true
	@docker compose -f docker-compose.ollama.yml exec ollama ollama pull deepseek-ocr || true
	@echo "Modelos disponíveis:"
	@docker compose -f docker-compose.ollama.yml exec ollama ollama list

run-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm run dev

# -----------------------------------------------------------------------------
# TEST/LINT
# -----------------------------------------------------------------------------

test:
	pytest backend/tests -v

lint:
	ruff check backend/ --fix
	ruff format backend/

# -----------------------------------------------------------------------------
# CLEAN
# -----------------------------------------------------------------------------

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf notebooks/.langchain_cache.db 2>/dev/null || true

.PHONY: help setup setup-venv setup-backend setup-frontend \
        download-roboflow download-kaggle verify-roboflow verify-kaggle \
        convert-voc-yolo extract-kaggle-zip \
        run run-backend run-frontend ollama-up ollama-pull test lint clean
