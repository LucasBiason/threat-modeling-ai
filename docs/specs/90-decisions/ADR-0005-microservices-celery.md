# ADR-0005: Microserviços e Processamento Assíncrono com Celery

## Status

Aceito.

## Contexto

O sistema original processava análises de forma **síncrona**: o frontend enviava a imagem e aguardava a resposta completa (Diagram → STRIDE → DREAD), o que podia levar vários minutos com LLMs. Isso gerava timeouts e má experiência de uso. O padrão do KPI Rede Comunita usa upload assíncrono: arquivo salvo, status PENDING → PROCESSING → COMPLETED, e notificações quando concluído.

## Decisão

1. **Split em microserviços**
   - **threat-modeling-api:** Orquestrador (FastAPI + SQLAlchemy + Celery) — armazena análises, imagens, status, logs e notificações; expõe endpoints de upload, listagem, detalhe e notificações.
   - **threat-analyzer:** Microserviço analisador (backend atual) — recebe imagem via HTTP, executa pipeline LLM, retorna JSON. Mantém apenas a lógica de análise.

2. **Processamento assíncrono com Celery**
   - Celery Beat dispara a cada 1 minuto a task `scan_pending_analyses`.
   - A task busca análises com status `EM_ABERTO`, atualiza para `PROCESSANDO`, e envia `process_analysis` para o worker.
   - O worker chama o threat-analyzer via HTTP, salva o resultado, atualiza status para `ANALISADO`, cria notificação.
   - Redis como broker e backend.

3. **Fluxo do usuário**
   - Upload → 201 imediato com `id`, `code`, `status: EM_ABERTO`.
   - Frontend redireciona para `/analyses/{id}` e faz polling.
   - Logs em tempo real via GET `/analyses/{id}/logs`.
   - Ícone de alertas mostra notificações não lidas; clique leva à análise concluída.

## Consequências

- **Positivas:** Sem timeouts; experiência fluida; escalabilidade do worker; isolamento do pipeline LLM.
- **Negativas:** Mais componentes (PostgreSQL, Redis, Celery); complexidade operacional maior.
- **Mitigações:** Docker Compose para ambiente local; documentação de runbooks.
