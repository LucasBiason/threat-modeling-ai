# Contratos de API — Threat Modeling AI

Resumo dos endpoints e contratos. Coleção Postman completa em `docs/Postman Collections/`.

---

## threat-modeling-api (orquestrador)

Base: `http://localhost:8000` (local). Prefixo das rotas de negócio: `/api/v1`.

### Analyses

| Método | Rota                        | Descrição                                                                                                                       |
| ------ | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| POST   | /api/v1/analyses            | Cria análise (body: multipart, campo `file` obrigatório). Retorna 201 com id, code, status EM_ABERTO, created_at, image_url.    |
| GET    | /api/v1/analyses            | Lista análises. Query: status_filter (EM_ABERTO \| PROCESSANDO \| ANALISADO \| FALHOU), limit (default 50), offset (default 0). |
| GET    | /api/v1/analyses/{id}       | Detalhe da análise; inclui result quando status = ANALISADO. 404 se não existir.                                                |
| GET    | /api/v1/analyses/{id}/image | Retorna a imagem do diagrama (Content-Type conforme extensão). 404 se imagem não existir.                                       |
| GET    | /api/v1/analyses/{id}/logs  | Retorna { logs } (JSON). 404 se análise não existir.                                                                            |

### Notifications

| Método | Rota                            | Descrição                                                                                        |
| ------ | ------------------------------- | ------------------------------------------------------------------------------------------------ |
| GET    | /api/v1/notifications/unread    | Lista notificações não lidas. Query: limit (default 20). Retorna unread_count e notifications[]. |
| POST   | /api/v1/notifications/{id}/read | Marca notificação como lida. 204 sem body. 404 se não existir.                                   |

### Health

| Método | Rota                                              | Descrição                                                                                          |
| ------ | ------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| GET    | /, /health, /health/, /health/ready, /health/live | Status do serviço; ready inclui checagem de banco; live não. Ready retorna 503 se DB indisponível. |

---

## threat-analyzer (microserviço de análise)

Base: `http://localhost:8001` (local). Prefixo da rota de análise: `/api/v1/threat-model`.

### POST /api/v1/threat-model/analyze

- **Request:** multipart/form-data
  - `file` (obrigatório): imagem (PNG, JPEG, WebP, GIF). Tipos permitidos: image/jpeg, image/png, image/webp, image/gif.
  - `confidence` (opcional): float, threshold futuro (ex.: YOLO).
  - `iou` (opcional): float, IoU threshold futuro.
- **Response (200):** JSON
  - model_used, components[], connections[], threats[], risk_score (0–10), risk_level (LOW|MEDIUM|HIGH|CRITICAL), processing_time, threat_count, component_count.
- **Erros:**
  - 400: tipo de arquivo inválido ou guardrail rejeitou (não é diagrama de arquitetura).
  - 500: ThreatModelingError (detalhe em body).

### Health

- GET /, /health, /health/ready, /health/live — mesmo padrão do orquestrador; analyzer não verifica banco.

---

## Referência

- Postman: `docs/Postman Collections/Threat Modeling AI.postman_collection.json`
- Environment local: `api_url` = http://localhost:8000, `analyzer_url` = http://localhost:8001
