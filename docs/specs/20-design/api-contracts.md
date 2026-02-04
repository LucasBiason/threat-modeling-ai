# API Contracts — Threat Modeling AI

## Base URL

`/api/v1/threat-model`

## POST /analyze

- **Request:** `multipart/form-data`
  - `file` (obrigatório): imagem do diagrama (PNG, JPG, WEBP).
  - `confidence` (opcional): float, threshold do modelo (0.1–0.9).
  - `iou` (opcional): float, IoU threshold (0.1–0.9).
- **Response:** JSON
  - `model_used`: string (ex.: "DummyPipeline" ou "gemini-1.5-pro").
  - `components`: lista de `{ id, type, name, bbox?, confidence? }`.
  - `connections`: lista de `{ from, to, protocol? }`.
  - `threats`: lista de `{ component_id, threat_type, description, mitigation, dread_score?, dread_details? }`.
  - `risk_score`: float (0–10).
  - `risk_level`: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL".
  - `processing_time`: float (segundos).
  - `threat_count`, `component_count`: computed.
- **Erros:**
  - 400: tipo de arquivo inválido.
  - 500: erro interno (ThreatModelingError).

## Health

- **GET /health**, **GET /health/ready**, **GET /health/live**
- **Response:** JSON com `status`, `system_name`, `timestamp`, etc.

## POST /chat (opcional, futuro)

- **Request:** JSON com `message` e opcional `report_id`.
- **Response:** JSON com `reply` (guardrails: tema STRIDE/DREAD e diagrama analisado).

## Referência

- Postman: `docs/Postman Collections/Threat Modeling AI.postman_collection.json`
- Environment: `Threat Modeling AI - Local.postman_environment.json` (base_url: http://localhost:8000)
