# OWASP Threat Modeling

**Fonte:** OWASP Foundation  
**URL:** https://owasp.org/www-community/Threat_Modeling  
**Projeto Oficial:** https://owasp.org/www-project-threat-modeling/

## Visão Geral

Threat modeling trabalha para identificar, comunicar e entender ameaças e mitigações no contexto de proteger algo de valor.

Um threat model é uma representação estruturada de todas as informações que afetam a segurança de uma aplicação - essencialmente, uma visão da aplicação e seu ambiente através da lente da segurança.

## Onde Aplicar

Threat modeling pode ser aplicado a:
- Software e aplicações
- Sistemas e redes
- Sistemas distribuídos
- Dispositivos IoT
- Processos de negócio

## O que um Threat Model Inclui

- Descrição do assunto a ser modelado
- Premissas que podem ser verificadas ou desafiadas
- Ameaças potenciais ao sistema
- Ações para mitigar cada ameaça
- Forma de validar o modelo e as ameaças
- Verificação do sucesso das ações tomadas

## Objetivos do Threat Modeling

Threat modeling é uma família de atividades para melhorar a segurança:
1. **Identificando** ameaças
2. **Definindo** contra-medidas para prevenir ou mitigar efeitos
3. Uma ameaça pode ser **maliciosa** (ex: ataque DoS) ou **incidental** (ex: falha de storage)

## Threat Modeling ao Longo do Ciclo de Vida

- Melhor aplicado continuamente durante o desenvolvimento
- O processo é o mesmo em diferentes níveis de abstração
- Modelo de alto nível deve ser definido cedo (fase de conceito/planejamento)
- Refinado ao longo do ciclo de vida
- Novos vetores de ataque surgem quando detalhes são adicionados
- Atualizar o threat model após: nova feature, incidente de segurança, mudanças arquiteturais

## Framework de Quatro Perguntas (OWASP)

1. **O que estamos trabalhando?** (Escopo)
2. **O que pode dar errado?** (Identificar ameaças)
3. **O que vamos fazer a respeito?** (Mitigações)
4. **Fizemos um bom trabalho?** (Validação)

## Métodos para Identificar Ameaças

- Brainstorm simples
- STRIDE (Microsoft)
- Kill Chains
- Attack Trees

Não há uma forma "certa" - modelos estruturados existem para tornar o processo mais eficiente.

## Benefícios

- "Line of sight" claro que justifica esforços de segurança
- Decisões de segurança feitas racionalmente
- Produz argumento de assurance para explicar e defender a segurança da aplicação
- Argumento de assurance começa com claims de alto nível e justifica com sub-claims ou evidência

## Threat Modeling Manifesto (2020)

Praticantes, pesquisadores e autores criaram o Threat Modeling Manifesto para compartilhar conhecimento coletivo e inspirar adoção. Contém valores, princípios, padrões e anti-padrões.

## Referências

- OWASP Threat Modeling Process
- Microsoft Security Development Lifecycle
- Microsoft Threat Modeling
- Threat Modeling Manifesto: https://www.threatmodelingmanifesto.org/
