# Frontend UI/UX — Cloud Architecture Security Analyzer

O frontend da aplicação segue o **comportamento e o design** demonstrados no vídeo enviado no grupo do hackathon (1000088277.mp4) e na implementação de referência em React (componente SecurityAnalyzer). Usar este documento como spec para o frontend do Cloud Architecture Security Analyzer.

## Comportamento (fluxo do usuário)

- **Upload:** Área de drag-and-drop (ou clique para buscar) para diagrama de arquitetura; suporte PNG, JPG, WEBP (ex.: máx 200 MB).
- **Configuração:** Sidebar (desktop) ou drawer/gaveta (mobile) com parâmetros do modelo: **Confidence** (Confiança) e **IoU** (Sobreposição) em sliders; breve descrição do "YOLOv8 Engine" (modelo fine-tuned para diagramas AWS/Azure e detecção STRIDE).
- **Análise:** Botão "Analisar Riscos" dispara o processamento; estado de loading (ex.: "Processando IA...") com overlay de "scan" na preview da imagem.
- **Resultados:** Dashboard com **Risk Score** (0–10) e nível (CRITICAL/HIGH/MEDIUM/LOW); lista de **detecções STRIDE** em cards expansíveis (accordion): componente, ameaça, severidade (HIGH/MEDIUM/LOW), código STRIDE (S, T, R, I, D, E), descrição da vulnerabilidade e **ação recomendada (mitigação)**. Botão "Exportar PDF" (ou equivalente) para o relatório.

## Design system (referência)

- **Estética:** Glassmorphism (fundos translúcidos, backdrop-blur), gradientes sutis (indigo/purple), sombras coloridas; design system próprio (estilo "Cyberpunk/SaaS Moderno" ou "Mobile-First" de alta fidelidade).
- **Cores:** Fundo principal escuro (ex.: slate-950); cartões em slate-900 com bordas slate-800; ações com gradiente indigo→purple; **cores semânticas para severidade:** Vermelho (CRITICAL/HIGH), Laranja (MEDIUM), Amarelo (LOW); mitigação em destaque (ex.: emerald/green).
- **Responsividade:** Mobile: menu lateral vira **Drawer** acessível por botão hambúrguer; grids em coluna única; header fixo com logo "CloudSec AI" (ou nome do produto). Desktop: sidebar fixa, dashboard em grid amplo.
- **UX:** Área de upload com feedback visual (hover, borda tracejada); cards de vulnerabilidade com badges de severidade e accordion para expandir descrição + mitigação; animações suaves de transição e loading; hit areas generosas para toque (acessibilidade).

## Implementação de referência (React)

- **Stack:** React, Tailwind CSS, ícones (ex.: lucide-react). Componente principal tipo `SecurityAnalyzer`: estado (file, analyzing, results, sidebarOpen, confThreshold, iouThreshold, expandedItems); handlers para file change, analyze (simulado ou chamada à API POST /analyze), toggle accordion e fechar drawer no resize.
- **Blocos principais:** (1) Mobile header + botão menu; (2) Sidebar/Drawer com sliders Confidence e IoU e descrição do YOLOv8 Engine; (3) Overlay para fechar drawer no mobile; (4) Área de upload (drag-and-drop visual); (5) Preview da imagem + overlay de "scan" durante análise; (6) Botão "Analisar Riscos" e, após resultado, card de Risk Score; (7) Grid de detecções em accordion (componente, ameaça, severity badge, código STRIDE, descrição, mitigação). O backend real substitui o MOCK_RESULTS por resposta da API (POST /analyze).
- **Referência:** Vídeo 1000088277.mp4; código de referência (componente SecurityAnalyzer) pode ser incluído no repositório ou linkado aqui quando disponível.
