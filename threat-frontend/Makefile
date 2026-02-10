# threat-frontend — build, run, lint (Docker build from repo root)
ROOT := $(shell cd .. && pwd)
IMAGE_NAME ?= threat-modeling-ai-threat-frontend
TAG ?= latest
DOCKERFILE := $(CURDIR)/Dockerfile
CONTEXT ?= $(ROOT)

.PHONY: help build run lint clean

help: ## Listar comandos
	@echo "Comandos:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

## Docker
build: ## Build imagem (stage runtime)
	cd $(CONTEXT) && docker build -f threat-frontend/Dockerfile --target runtime -t $(IMAGE_NAME):$(TAG) .

run: build ## Rodar container (porta 80)
	docker run --rm -p 80:80 $(IMAGE_NAME):$(TAG)

## Local
lint: ## ESLint
	npm run lint

clean: ## Remover caches e dist
	rm -rf node_modules/.cache dist 2>/dev/null || true
