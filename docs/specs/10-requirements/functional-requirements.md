# Requisitos funcionais — Threat Modeling AI

Requisitos observáveis e testáveis, sem detalhes de implementação.

---

## RF-01 — Upload de diagrama

- O sistema deve aceitar upload de uma imagem (PNG, JPEG, WebP ou GIF) como diagrama de arquitetura.
- O sistema deve responder imediatamente com identificador da análise e status (EM_ABERTO), sem aguardar o fim do processamento.
- O sistema deve rejeitar upload quando o tipo de arquivo não for permitido (resposta 4xx com mensagem clara).

## RF-02 — Processamento em background

- O sistema deve processar a análise em background (worker), atualizando status para PROCESSANDO e, ao final, ANALISADO ou FALHOU.
- O sistema deve permitir consultar o status e o resultado da análise por identificador.
- O sistema deve permitir consultar logs de processamento da análise por identificador.

## RF-03 — Análise STRIDE/DREAD

- O sistema deve extrair componentes e conexões do diagrama (via pipeline LLM).
- O sistema deve identificar ameaças STRIDE e atribuir pontuação DREAD a cada ameaça.
- O sistema deve retornar risk_score (0–10) e risk_level (LOW, MEDIUM, HIGH, CRITICAL) para a análise como um todo.
- O sistema deve rejeitar imagens que não forem consideradas diagramas de arquitetura (guardrail), com mensagem de erro adequada.

## RF-04 — Listagem e detalhe de análises

- O sistema deve listar análises com filtro opcional por status e paginação (limit/offset).
- O sistema deve retornar detalhe da análise por ID, incluindo resultado completo quando status for ANALISADO.
- O sistema deve servir a imagem do diagrama por ID da análise.

## RF-05 — Notificações

- O sistema deve listar notificações não lidas (com contagem).
- O sistema deve permitir marcar uma notificação como lida.
- O sistema deve criar notificação quando uma análise for concluída (ANALISADO ou FALHOU).

## RF-06 — Health

- O sistema (orquestrador e analyzer) deve expor endpoints de health (/health, /health/ready, /health/live).
- O orquestrador deve indicar estado do banco de dados quando aplicável; readiness deve retornar 503 se o banco estiver indisponível.

## RF-07 — Frontend

- O usuário deve poder enviar um diagrama (upload) e ser redirecionado para a página da análise.
- O usuário deve poder ver a lista de análises e o status de cada uma.
- O usuário deve poder ver o detalhe da análise (incluindo relatório STRIDE/DREAD quando concluída) e a imagem do diagrama.
- O usuário deve poder ver notificações não lidas e acessar a análise relacionada ao clicar na notificação.
