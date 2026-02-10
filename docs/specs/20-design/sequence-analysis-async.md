# Diagrama de sequência — Processamento assíncrono

Interação entre usuário, frontend, orquestrador, banco, Celery e threat-analyzer.

---

## Sequência principal

```mermaid
sequenceDiagram
    participant U as Usuário
    participant F as Frontend
    participant API as threat-modeling-api
    participant DB as PostgreSQL
    participant CB as Celery Beat
    participant CW as Celery Worker
    participant A as threat-analyzer

    U->>F: Upload imagem
    F->>API: POST /api/v1/analyses (multipart)
    API->>DB: INSERT analyses (status=EM_ABERTO)
    API->>F: 201 { id, code, status }
    F->>F: Redireciona para /analyses/{id}

    loop Polling (ex.: 5s)
        F->>API: GET /api/v1/analyses/{id}
        API->>DB: SELECT analyses
        API->>F: 200 { status, result?, ... }
    end

    Note over CB,CW: A cada 1 min (Beat)
    CB->>CW: Dispara scan_pending_analyses
    CW->>DB: SELECT * FROM analyses WHERE status='EM_ABERTO' LIMIT 1
    alt Existe análise pendente
        CW->>DB: UPDATE status=PROCESSANDO
        CW->>A: POST /api/v1/threat-model/analyze (imagem)
        A-->>CW: 200 { components, threats, risk_score, ... }
        CW->>DB: UPDATE result, status=ANALISADO, finished_at
        CW->>DB: INSERT notifications
    end

    F->>API: GET /api/v1/analyses/{id}
    API->>DB: SELECT
    API->>F: 200 { status=ANALISADO, result }
    F->>U: Exibe relatório STRIDE/DREAD
```

---

## Sequência: notificações

```mermaid
sequenceDiagram
    participant U as Usuário
    participant F as Frontend
    participant API as threat-modeling-api
    participant DB as PostgreSQL

    Note over F: Worker já criou notificação
    U->>F: Abre ícone de alertas
    F->>API: GET /api/v1/notifications/unread
    API->>DB: SELECT notifications WHERE is_read=false
    API->>F: 200 { unread_count, notifications[] }
    F->>U: Lista notificações

    U->>F: Clica em uma notificação
    F->>API: POST /api/v1/notifications/{id}/read
    API->>DB: UPDATE notifications SET is_read=true
    API->>F: 204 No Content
    F->>API: GET /api/v1/analyses/{analysis_id}
    F->>U: Exibe página da análise
```
