#!/usr/bin/env bash
# =============================================================================
# Threat Modeling AI - Cria .venv e registra kernel Jupyter
# Execute na raiz do projeto: ./notebooks/scripts/setup_venv_kernel.sh
# =============================================================================

set -e
cd "$(dirname "$0")/../.."
PROJECT_ROOT="$(pwd)"

echo "==> Raiz do projeto: $PROJECT_ROOT"

if [ -d ".venv" ]; then
  echo "==> .venv já existe. Atualizando dependências..."
else
  echo "==> Criando .venv..."
  python3 -m venv .venv
fi

echo "==> Atualizando pip..."
.venv/bin/pip install --upgrade pip -q

echo "==> Instalando dependências dos notebooks (notebooks/requirements.txt)..."
.venv/bin/pip install -r notebooks/requirements.txt -q

echo "==> Registrando kernel Jupyter 'Python (threat-modeling-ai)'..."
.venv/bin/python -m ipykernel install --user --name threat-modeling-ai --display-name "Python (threat-modeling-ai)"

echo ""
echo "=== Concluído ==="
echo "  - Ambiente: .venv/"
echo "  - Kernel: Python (threat-modeling-ai)"
echo "  - Ative com: source .venv/bin/activate"
echo "  - Para baixar datasets: make download-roboflow ou make download-kaggle"
