# Postman Collections – Threat Modeling AI

- **Threat Modeling AI.postman_collection.json** – Collection com todos os endpoints do orquestrador (Threat Modeling API) e do Threat Analyzer.
- **Threat Modeling AI - Local.postman_environment.json** – Environment local com `api_url` (porta 8000) e `analyzer_url` (porta 8001).

## Uso

1. Importe a collection e o environment no Postman.
2. Selecione o environment **Threat Modeling AI - Local**.
3. Suba a stack com `make run` (ou `docker compose up`) para ter as APIs em `localhost:8000` e `localhost:8001`.

Cada request inclui descrição, parâmetros documentados e exemplos de resposta (sucesso e erro quando há validações). Os exemplos foram montados a partir do contrato da API; você pode rodar os comandos **curl** descritos em cada request para obter respostas atuais e atualizar os exemplos no Postman (Save Response > Save as example).

## Endpoints

| Serviço             | Base               | Principais rotas                                                                                                                  |
| ------------------- | ------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| Threat Modeling API | `{{api_url}}`      | Health, `POST/GET /api/v1/analyses`, `GET /api/v1/analyses/:id`, image, logs, `GET /api/v1/notifications/unread`, `POST .../read` |
| Threat Analyzer     | `{{analyzer_url}}` | Health, `POST /api/v1/threat-model/analyze` (multipart: file, confidence, iou)                                                    |
