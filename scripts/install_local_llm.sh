#!/usr/bin/env bash
# Instala e configura Ollama local: sobe container, baixa modelos vision e verifica.
# Usa configuracao do docker-compose (configs/.env). Um unico comando.
# Uso: make install-local-llm  (a partir da raiz do projeto)

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_ENV="$PROJECT_ROOT/configs/.env"

if [ ! -f "$COMPOSE_ENV" ]; then
  echo "Erro: configs/.env nao encontrado. Copie de configs/.env.example e preencha."
  exit 1
fi

cd "$PROJECT_ROOT"
echo "==> Subindo Ollama (docker compose)..."
docker compose --env-file "$COMPOSE_ENV" up -d ollama

echo "==> Aguardando Ollama em http://localhost:11434 ..."
for i in 1 2 3 4 5 6 7 8 9 10; do
  if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "==> Ollama respondendo."
    break
  fi
  sleep 2
done

echo "==> Baixando modelos vision..."
docker compose --env-file "$COMPOSE_ENV" exec -T ollama ollama pull qwen2.5-vl || true
docker compose --env-file "$COMPOSE_ENV" exec -T ollama ollama pull llava || true
docker compose --env-file "$COMPOSE_ENV" exec -T ollama ollama pull deepseek-vl || true

echo "==> Modelos disponiveis:"
docker compose --env-file "$COMPOSE_ENV" exec -T ollama ollama list

echo "==> Verificando..."
if curl -s http://localhost:11434/api/tags | grep -q models; then
  echo "OK: Ollama instalado e funcional."
else
  echo "Aviso: verifique manualmente se os modelos estao listados."
fi
