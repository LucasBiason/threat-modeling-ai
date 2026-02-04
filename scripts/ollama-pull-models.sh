#!/bin/bash
# Pull dos modelos vision para comparativo no notebook 02
# Requer Ollama rodando (docker compose -f docker-compose.ollama.yml up -d)

set -e
OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"

echo "Aguardando Ollama em $OLLAMA_HOST ..."
until curl -s "$OLLAMA_HOST/api/tags" >/dev/null 2>&1; do
  sleep 2
done
echo "Ollama OK. Baixando modelos..."

for model in qwen2.5-vl llava deepseek-vl; do
  echo "=== Pull $model ==="
  ollama pull "$model" || echo "Aviso: $model pode não existir, tentando próximo..."
done

echo "Pronto. Modelos disponíveis:"
ollama list
