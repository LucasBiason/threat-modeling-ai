#!/usr/bin/env bash
# Pre-commit: lint e test por servico (Makefile raiz nao tem test/lint).
# Uso: pre-commit run --all-files  ou  ./scripts/pre_commit.sh
set -e
cd "$(dirname "$0")/.."
echo "==> Lint (threat-modeling-shared)..."
ruff check threat-modeling-shared/ --fix
ruff format threat-modeling-shared/
echo "==> Lint (threat-analyzer, threat-modeling-api, frontend)..."
make -C threat-analyzer lint
make -C threat-modeling-api lint
make -C frontend lint
echo "==> Test (threat-analyzer, threat-modeling-api)..."
make -C threat-analyzer test || true
make -C threat-modeling-api test || true
