# STRIDE Threat Modeling - Guia por Tipo de Componente

## O que é STRIDE?

STRIDE é um framework de modelagem de ameaças desenvolvido pela Microsoft que categoriza ameaças em 6 tipos:

| Categoria | Propriedade Violada | Descrição |
|-----------|---------------------|-----------|
| **S**poofing | Autenticação | Fingir ser outra entidade |
| **T**ampering | Integridade | Modificar dados sem autorização |
| **R**epudiation | Não-repúdio | Negar ter realizado uma ação |
| **I**nformation Disclosure | Confidencialidade | Expor dados a quem não deveria |
| **D**enial of Service | Disponibilidade | Tornar sistema indisponível |
| **E**levation of Privilege | Autorização | Obter permissões indevidas |

---

## Ameaças por Tipo de Componente

### 1. API Gateway / Load Balancer

| STRIDE | Ameaça | Mitigação |
|--------|--------|-----------|
| Spoofing | Requisições de origem falsificada | Validação de tokens, mTLS, API keys |
| Tampering | Modificação de headers/payload em trânsito | TLS 1.3, validação de integridade |
| Repudiation | Impossibilidade de rastrear requisições | Logging centralizado, request IDs |
| Info Disclosure | Vazamento de rotas internas, headers sensíveis | Remover headers internos, rate limiting |
| DoS | Sobrecarga por flood de requisições | WAF, rate limiting, auto-scaling |
| EoP | Bypass de autenticação no gateway | Validação em múltiplas camadas |

### 2. Web Server / Application Server

| STRIDE | Ameaça | Mitigação |
|--------|--------|-----------|
| Spoofing | Session hijacking, cookie theft | Secure cookies, HttpOnly, SameSite |
| Tampering | Injeção de código (XSS, SQLi) | Input validation, prepared statements |
| Repudiation | Ações de usuário não auditadas | Audit logging, timestamps |
| Info Disclosure | Stack traces, error messages detalhados | Custom error pages, sanitização |
| DoS | Requisições lentas (Slowloris) | Timeouts, connection limits |
| EoP | Vulnerabilidades no código (IDOR, broken access) | RBAC, validação de autorização |

### 3. Database (RDS, DynamoDB, SQL)

| STRIDE | Ameaça | Mitigação |
|--------|--------|-----------|
| Spoofing | Credenciais de DB comprometidas | IAM roles, rotação de secrets |
| Tampering | SQL injection, modificação direta | Prepared statements, least privilege |
| Repudiation | Alterações sem audit trail | DB audit logs, triggers de auditoria |
| Info Disclosure | Dados não criptografados, backups expostos | Encryption at rest/transit, VPC |
| DoS | Queries pesadas, connection exhaustion | Query optimization, connection pooling |
| EoP | Usuário DB com permissões excessivas | Princípio do menor privilégio |

### 4. Storage (S3, Blob, Object Storage)

| STRIDE | Ameaça | Mitigação |
|--------|--------|-----------|
| Spoofing | URLs pré-assinadas roubadas | Curta expiração, IP binding |
| Tampering | Modificação de objetos armazenados | Versionamento, MFA delete |
| Repudiation | Acesso a arquivos não rastreado | S3 access logs, CloudTrail |
| Info Disclosure | Bucket público, permissões incorretas | Block public access, bucket policies |
| DoS | Upload massivo, storage exhaustion | Quotas, lifecycle policies |
| EoP | Políticas IAM muito permissivas | Least privilege, resource-based policies |

### 5. Message Queue (SQS, EventBridge, Kafka)

| STRIDE | Ameaça | Mitigação |
|--------|--------|-----------|
| Spoofing | Mensagens de produtor não autenticado | Assinatura de mensagens, mTLS |
| Tampering | Modificação de mensagens na fila | Encryption, message signing |
| Repudiation | Processamento de mensagem não rastreável | Message IDs, dead letter queues |
| Info Disclosure | Mensagens com dados sensíveis em claro | Encryption in transit e at rest |
| DoS | Flood de mensagens, consumer lag | Rate limiting, auto-scaling consumers |
| EoP | Acesso não autorizado à fila | IAM policies, VPC endpoints |

### 6. Lambda / Serverless Functions

| STRIDE | Ameaça | Mitigação |
|--------|--------|-----------|
| Spoofing | Invocação por trigger não autorizado | Resource policies, VPC |
| Tampering | Código da função modificado | Versioning, code signing |
| Repudiation | Execuções não logadas | CloudWatch Logs, X-Ray |
| Info Disclosure | Env vars com secrets expostas | Secrets Manager, parameter store |
| DoS | Invocações infinitas, cold start abuse | Concurrency limits, reserved capacity |
| EoP | IAM role da função muito permissiva | Least privilege execution role |

### 7. Container / Kubernetes (EKS, ECS)

| STRIDE | Ameaça | Mitigação |
|--------|--------|-----------|
| Spoofing | Pod impersonation, service mesh bypass | mTLS, network policies |
| Tampering | Container image maliciosa | Image signing, vulnerability scanning |
| Repudiation | Ações no cluster não auditadas | Audit logs, Falco |
| Info Disclosure | Secrets em ConfigMaps, env vars | External secrets, sealed secrets |
| DoS | Resource exhaustion, noisy neighbor | Resource quotas, limits |
| EoP | Privileged containers, host access | Pod security policies/standards |

### 8. User / Client

| STRIDE | Ameaça | Mitigação |
|--------|--------|-----------|
| Spoofing | Credenciais roubadas, phishing | MFA, passwordless auth |
| Tampering | Manipulação de requisições do cliente | Server-side validation |
| Repudiation | Usuário nega ter feito ação | Audit trail, digital signatures |
| Info Disclosure | Dados sensíveis no frontend | Minimize data exposure |
| DoS | Conta comprometida para ataques | Account lockout, anomaly detection |
| EoP | Privilege escalation via UI bugs | Input validation, RBAC |

### 9. External Service / Third-Party API

| STRIDE | Ameaça | Mitigação |
|--------|--------|-----------|
| Spoofing | Resposta de API falsificada | Certificate pinning, HTTPS |
| Tampering | Dados corrompidos em trânsito | TLS, response validation |
| Repudiation | Chamadas a APIs não logadas | Logging de todas as chamadas externas |
| Info Disclosure | Dados sensíveis enviados a terceiros | Data minimization, masking |
| DoS | API terceira indisponível | Circuit breaker, fallback |
| EoP | API key com permissões excessivas | Scoped API keys, rotation |

### 10. VPC / Network Boundary

| STRIDE | Ameaça | Mitigação |
|--------|--------|-----------|
| Spoofing | IP spoofing, ARP poisoning | VPC flow logs, security groups |
| Tampering | Man-in-the-middle dentro da VPC | mTLS, private subnets |
| Repudiation | Tráfego de rede não monitorado | VPC flow logs, traffic mirroring |
| Info Disclosure | Dados em trânsito não criptografados | TLS everywhere, VPN |
| DoS | DDoS, network flooding | AWS Shield, WAF, NACLs |
| EoP | Lateral movement após comprometimento | Microsegmentation, zero trust |

---

## Fluxo de Análise STRIDE

1. **Identificar componentes** do diagrama
2. **Para cada componente**, verificar as 6 categorias STRIDE
3. **Para cada conexão** entre componentes, analisar ameaças em trânsito
4. **Identificar trust boundaries** e ameaças na fronteira
5. **Priorizar** usando DREAD scoring

---

## Referências

- Microsoft STRIDE: https://docs.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats
- OWASP Threat Modeling: https://owasp.org/www-community/Threat_Modeling
- AWS Well-Architected Security Pillar
- NIST Cybersecurity Framework
