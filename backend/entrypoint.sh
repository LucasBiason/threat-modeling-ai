#!/usr/bin/env bash

set -ef

cli_help() {
  cli_name=${0##*/}
  echo "
$cli_name
Threat Modeling AI - Backend Entrypoint
Usage: $cli_name [command]

Commands:
  runserver   Start FastAPI server
  test        Run tests with coverage
  *           Help
"
  exit 1
}

case "$1" in
  test)
    coverage run -m pytest --cov=app --cov-report term-missing -v tests/ 2>/dev/null || pytest -v tests/ 2>/dev/null || python -m pytest -v
    ;;
  runserver)
    PORT=${PORT:-8000}
    echo "Starting Threat Modeling AI backend on port $PORT..."
    exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
    ;;
  *)
    cli_help
    ;;
esac
