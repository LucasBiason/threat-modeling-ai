# Conducting a STRIDE-based Threat Analysis 2.0

**Fonte:** UK Government - Secure Connected Places Playbook (Department for Science, Innovation & Technology)

## O que é uma Análise de Ameaças?

Uma análise de ameaças é um processo estruturado e sistemático para revisar como um sistema, serviço ou processo pode ser atacado - intencionalmente por atacantes maliciosos ou não intencionalmente por causa de misconfiguração. O resultado é a identificação das vulnerabilidades do sistema e como elas podem ser exploradas.

Em ambientes conectados, é importante adotar uma "abordagem de sistemas" que considere as interações e relações entre os componentes do sistema ao longo de seu ciclo de vida.

## O que é STRIDE?

STRIDE é uma metodologia estruturada e iterativa para identificar e avaliar ameaças a um sistema. Fornece o mecanismo para avaliar ameaças cibernéticas em projetos de tecnologia.

- **Origem:** STRIDE surgiu na indústria para entender ameaças que surgem quando sistemas atravessam trust boundaries
- **Trust boundaries:** Lacunas entre entidades que operam sob políticas de segurança diferentes (entre organizações, fornecedores, provedores de hosting)
- **Advogado por:** National Cyber Security Centre (NCSC) nos Connected Places Cyber Security Principles

## STRIDE - As 6 Categorias

| Letra | Categoria | Propriedade Violada |
|-------|-----------|---------------------|
| **S** | Spoofing | Autenticação |
| **T** | Tampering | Integridade |
| **R** | Repudiation | Não-repúdio |
| **I** | Information Disclosure | Confidencialidade |
| **D** | Denial of Service | Disponibilidade |
| **E** | Elevation of Privilege | Autorização |

## Perguntas Estratégicas por Categoria

### Spoofing
- Como sabemos quem está nos enviando dados?
- Autenticamos usuários/dispositivos?
- Alguém pode fingir ser outra pessoa?
- Protegemos bem credenciais sensíveis nos sistemas?
- **Exemplo IoT:** Um sensor pode ser falsificado, fornecendo dados de entrada/saída falsos?

### Tampering
- Alguém pode modificar o que submete?
- A integridade dos dados é validada com hashes, MACs ou assinaturas digitais?
- Os inputs são validados antes do processamento?
- **Exemplo:** Um atacante pode explorar vulnerabilidades no processamento e adulterar o sistema?

### Repudiation
- Uma ação pode ser associada a uma identidade única?
- Alguém pode realizar uma ação e negar que foi ele?
- **Exemplo:** Com criptografia simétrica, não se prova quem enviou a leitura. Compare com assinatura digital que prova a origem.
- **Exemplo IoT:** Um criminoso pode solicitar desligar a iluminação e negar que fez a solicitação?

### Information Disclosure
- Outros podem acessar informações que não deveriam?
- Os dados são comunicados sem criptografia?
- A criptografia é fraca ou o manuseio de material criptográfico é pobre?
- O acesso é removido quando alguém muda de função ou deixa a organização?
- **Exemplo IoT:** Alguém próximo pode ver dados não criptografados e saber a quem se referem?

### Denial of Service
- Alguém pode afetar o sistema e degradar a capacidade de outros de usá-lo?
- Quão protegido está de DoS baseado em internet?
- Quão resiliente é a rede IoT a jamming de radiofrequência?
- Os inputs são validados para evitar que input malicioso torne a aplicação não responsiva?
- **Exemplo:** Um usuário pode fazer muitas reservas e negar acesso a outros?

### Elevation of Privilege
- Um usuário/processo não privilegiado pode obter acesso além de suas permissões?
- Podem acessar memória/storage compartilhado onde credenciais de admin podem estar?
- **Exemplo IoT:** Um cidadão pode impersonar um administrador pela interface e remover outros usuários?

## Mitigações por Categoria STRIDE

| Ameaça | Mitigação |
|--------|-----------|
| Spoofing | Autenticidade |
| Tampering | Integridade |
| Repudiation | Não-repúdio |
| Information Disclosure | Confidencialidade |
| Denial of Service | Disponibilidade |
| Elevation of Privilege | Autorização |

## Modelagem de Sistemas

- STRIDE concentra-se em modelar ameaças a sistemas
- A modelagem de sistemas é essencial antes da análise STRIDE
- UML e diagramas de fluxo de dados fornecem linguagem padronizada
- Um diagrama ad-hoc de caixas e linhas ainda é melhor que nada
- A modelagem auxilia na identificação de trust boundaries e controles

## Avaliação de Risco

Os outputs iniciais são abstratos - sem probabilidade ou impacto atribuídos. O próximo passo é conduzir um processo de avaliação de risco para entender probabilidade e impacto das ameaças identificadas.

## Glossário

- **Trust boundaries:** Lacunas entre entidades com políticas de segurança diferentes
- **Integrity:** Propriedade de que a informação não pode ser adulterada
- **Confidentiality:** Propriedade de que a informação não é divulgada a partes não autorizadas
- **Availability:** Propriedade de que a informação pode ser usada quando e onde necessária
- **Digital Signature:** Hash com chave que fornece garantias do autor
- **HMAC:** Hash com chave que garante que o autor teve acesso a uma chave compartilhada

## Referências

- Fonte: https://assets.publishing.service.gov.uk/media/65e732717bc3290adab8c234/Conducting_a_STRIDE-based_threat_analysis_2.0.pdf
- NCSC Connected Places Cyber Security Principles
- securitytxt.org para vulnerability disclosure (RFC9116)
