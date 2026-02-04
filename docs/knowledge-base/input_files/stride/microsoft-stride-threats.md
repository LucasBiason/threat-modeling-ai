# Microsoft STRIDE Threat Model

**Fonte:** Microsoft Azure - Threat Modeling Tool  
**URL:** https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats

## Sobre o Microsoft Threat Modeling Tool

O Threat Modeling Tool é um elemento central do Microsoft Security Development Lifecycle (SDL). Permite que arquitetos de software identifiquem e mitiguem potenciais problemas de segurança cedo, quando são relativamente fáceis e econômicos de resolver, reduzindo o custo total de desenvolvimento. O tool foi desenhado para não-especialistas em segurança.

## O Modelo STRIDE da Microsoft

A Microsoft usa o modelo STRIDE para categorizar diferentes tipos de ameaças e simplificar conversas de segurança.

### Spoofing
Envolve acessar ilegalmente e usar informações de autenticação de outro usuário, como nome de usuário e senha. O atacante finge ser outra entidade.

### Tampering
Envolve a modificação maliciosa de dados. Exemplos incluem alterações não autorizadas em dados persistentes (ex: banco de dados) e alteração de dados em trânsito entre dois computadores em uma rede aberta como a Internet.

### Repudiation
Associado a usuários que negam ter realizado uma ação sem que outras partes tenham como provar o contrário. Exemplo: usuário realiza operação ilegal em sistema que não tem capacidade de rastrear operações proibidas.

**Non-Repudiation:** Capacidade do sistema de contra-atacar ameaças de repúdio. Exemplo: usuário que compra item assina no recebimento; o vendedor usa o recibo como evidência.

### Information Disclosure
Envolve a exposição de informações a indivíduos que não deveriam ter acesso. Exemplos: capacidade de usuários lerem arquivo ao qual não foram concedidos direitos; capacidade de intruso ler dados em trânsito entre dois computadores.

### Denial of Service
Ataques DoS negam serviço a usuários válidos - por exemplo, tornando servidor web temporariamente indisponível. É necessário proteger contra certos tipos de ameaças DoS para melhorar disponibilidade e confiabilidade do sistema.

### Elevation of Privilege
Um usuário não privilegiado ganha acesso privilegiado e assim tem acesso suficiente para comprometer ou destruir o sistema inteiro. Inclui situações em que o atacante penetrou todas as defesas e se tornou parte do sistema confiável.

## Próximos Passos

Consulte **Threat Modeling Tool Mitigations** para aprender diferentes formas de mitigar essas ameaças com Azure.

## Referências

- Microsoft Security Development Lifecycle
- Microsoft Threat Modeling
- Training: Use a framework to identify threats and find ways to reduce or eliminate risk
