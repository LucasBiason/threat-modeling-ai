# Frontend UI/UX — Threat Modeling AI

Especificação de comportamento e design do frontend. Fluxo atual: **upload assíncrono** (orquestrador); sem envio de parâmetros Confidence/IoU no upload (reservados para uso futuro no analyzer).

---

## Comportamento (fluxo do usuário)

- **Upload:** Área de drag-and-drop ou clique para selecionar arquivo (PNG, JPG, WebP, GIF). Ao enviar, POST /api/v1/analyses; resposta 201 com id e code; redirecionamento para a página da análise (/analyses/:id).
- **Página da análise:** Exibição do status (EM_ABERTO, PROCESSANDO, ANALISADO, FALHOU). Polling em GET /api/v1/analyses/:id (ex.: a cada 5s) até status final. Durante PROCESSANDO, opção de exibir GET /analyses/:id/logs. Quando ANALISADO, exibir relatório completo; quando FALHOU, exibir mensagem de erro.
- **Listagem:** Página com lista de análises (GET /api/v1/analyses), com filtro por status e acesso ao detalhe.
- **Notificações:** Ícone de alertas com contagem de não lidas (GET /api/v1/notifications/unread). Dropdown ou lista com notificações; ao clicar, marcar como lida (POST /notifications/:id/read) e navegar para a análise correspondente.
- **Relatório:** Exibição de risk score (0–10), risk level (CRITICAL/HIGH/MEDIUM/LOW), e lista de ameaças STRIDE em cards expansíveis (accordion): componente, tipo de ameaça, severidade, descrição, mitigação. Imagem do diagrama disponível (GET /analyses/:id/image ou via URL no detalhe).

---

## Design system (referência)

- **Estética:** Glassmorphism (fundos translúcidos, backdrop-blur), gradientes sutis (indigo/purple), sombras; estilo moderno/escuro.
- **Cores:** Fundo escuro (ex.: slate-950); cartões em slate-900 com bordas slate-800; ações com gradiente indigo→purple; **severidade:** vermelho (CRITICAL/HIGH), laranja (MEDIUM), amarelo (LOW); mitigação em destaque (ex.: emerald/green).
- **Responsividade:** Mobile: menu/drawer (hambúrguer); desktop: sidebar fixa. Header com logo/nome do produto.
- **UX:** Área de upload com feedback visual; cards de ameaça com badges de severidade e accordion; animações suaves; hit areas generosas para toque.

---

## Stack e referência

- React 18, Vite, TypeScript, Tailwind CSS.
- Consumo exclusivo da API do orquestrador (threat-modeling-api); nenhuma chamada direta ao threat-analyzer.
- Referência de comportamento e layout: conforme definido no desafio (vídeo e mockups quando disponíveis).
