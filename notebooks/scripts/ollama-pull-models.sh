#!/bin/bash
# Pull dos modelos vision para comparativo (notebook 02 - integração LLM)
# Requer Ollama rodando: make ollama-up ou make run
# Via Make: make ollama-pull (executa dentro do container)

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
