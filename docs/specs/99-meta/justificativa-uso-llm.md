# Justificativa: Uso de LLM como Principal para Análise de Diagramas

**Projeto:** Threat Modeling AI (Hackathon FIAP)  
**Data:** 2026-02-08  
**Status:** Aprovado

---

## 1. Objetivo deste documento

Justificar formalmente a decisão de utilizar **LLMs (Large Language Models) com visão** como principal mecanismo de análise de diagramas de arquitetura no projeto, em vez de depender do modelo YOLO treinado, considerando prazo, qualidade do treinamento e características dos datasets.

---

## 2. Contexto do treinamento YOLO

### 2.1 Datasets utilizados

- **Roboflow:** AWS and Azure System Diagrams, formato YOLOv8, ~4.418 imagens (train), 203 classes (componentes e setas). Tamanho ~61 MB.
- **Kaggle:** Dataset maior (~33 GB), formato VOC com conversão automática para YOLO.

### 2.2 Problemas observados

- **Qualidade e consistência das bases:** Anotações e variedade de estilos de diagrama impactam a generalização do modelo. O treinamento ficou **aquém do desejado** para reconhecer de forma estável componentes e conexões em diagramas variados.
- **Tempo de treinamento:** Treinos completos (Roboflow e sobretudo Kaggle) demandam tempo significativo (horas a dias), incompatível com a janela de entrega do Hackathon (semana até quinta).
- **Métricas e comportamento:** Mesmo após treino, o modelo YOLO apresentou:
  - Confiança média baixa em vários casos.
  - Dificuldade com componentes genéricos (“groups”) e setas.
  - Necessidade de ajustes finos (limiar, pós-processamento) que consumiriam mais tempo de validação.

---

## 3. Por que LLM como principal

### 3.1 Desempenho no tempo disponível

- **LLMs com visão** (Gemini, GPT-4o, modelos vision via Ollama) já entregam análise estruturada (componentes, conexões, boundaries) a partir da imagem, sem etapa de treinamento.
- A **integração está implementada** no threat-analyzer (DiagramAgent com fallback Gemini → OpenAI → Ollama), permitindo fechar o fluxo end-to-end e focar em testes e documentação.
- O tempo restante pode ser dedicado a **testar e validar** qual LLM principal e quais reservas usar, em vez de tentar melhorar um treino YOLO incerto.

### 3.2 Alinhamento com o requisito aceito

O professor aceita **qualquer método** desde que o resultado seja “identificar componentes e gerar análise STRIDE”. O uso de LLM atende a esse requisito e permite entregar um sistema funcional e documentado no prazo.

### 3.3 Arquitetura híbrida (futuro)

A **ADR-0001** mantém a opção de arquitetura híbrida (YOLO primeiro, LLM como fallback quando confiança baixa). A decisão atual é:

- **Agora:** Pipeline 100% LLM (DiagramAgent → StrideAgent → DreadAgent) para garantir entrega e qualidade.
- **Futuro (pós-Hackathon):** Quando houver best.pt avaliado e limiar definido, o YOLO pode ser reincorporado como primeira etapa com fallback LLM.

---

## 4. Conclusão

- O **treinamento YOLO** ficou aquém do desejado devido à natureza dos datasets e ao tempo necessário para treino e tuning.
- Usar **LLM como principal** oferece melhor **desempenho no tempo disponível**, entrega funcional e permite **validar e documentar** o fluxo (backend, frontend, escolha de LLM principal e reservas) até a data limite (quinta-feira).
- Esta justificativa serve de base para a **avaliação dos notebooks** (model-evaluation-report) e para a **seleção/validação das LLMs** (principal + duas reservas) documentada em llm-selecao-validacao.md.

---

## Referências

- ADR-0001 — Arquitetura híbrida YOLO + LLM (fallback)
- model-evaluation-report.md — Avaliação do modelo YOLO e decisão de pipeline
- llm-selecao-validacao.md — Critérios e processo de validação das LLMs
