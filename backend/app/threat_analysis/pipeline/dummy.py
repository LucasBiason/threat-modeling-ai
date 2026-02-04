"""Dummy pipeline - retorna dados fixos (AWS SEI) para testes unitários do serviço.

Use USE_DUMMY_PIPELINE=true apenas em testes. Em produção, o pipeline usa LLM (Diagram, STRIDE, DREAD).
"""

from app.core.logging import get_logger
from app.threat_analysis.schemas import RiskLevel

logger = get_logger("pipeline.dummy")

# AWS SEI architecture - based on diagram01.png analysis
DUMMY_COMPONENTS = [
    {"id": "user_1", "type": "User", "name": "Usuários SEI", "description": None},
    {"id": "shield_1", "type": "Service", "name": "AWS Shield", "description": None},
    {"id": "cloudfront_1", "type": "Service", "name": "CloudFront", "description": None},
    {"id": "waf_1", "type": "Service", "name": "WAF", "description": None},
    {"id": "alb_1", "type": "LoadBalancer", "name": "ALB", "description": None},
    {"id": "sei_ec2_1", "type": "Server", "name": "SEI/SIP EC2", "description": None},
    {"id": "rds_primary", "type": "Database", "name": "RDS Primary", "description": None},
    {"id": "rds_secondary", "type": "Database", "name": "RDS Secondary", "description": None},
    {"id": "elasticache_1", "type": "Cache", "name": "ElastiCache", "description": None},
    {"id": "solr_1", "type": "Service", "name": "Solr", "description": None},
    {"id": "efs_1", "type": "Storage", "name": "EFS", "description": None},
    {"id": "cloudtrail_1", "type": "Service", "name": "CloudTrail", "description": None},
    {"id": "kms_1", "type": "Service", "name": "KMS", "description": None},
    {"id": "backup_1", "type": "Service", "name": "Backup", "description": None},
    {"id": "cloudwatch_1", "type": "Service", "name": "CloudWatch", "description": None},
    {"id": "ses_1", "type": "Service", "name": "SES", "description": None},
]

DUMMY_CONNECTIONS = [
    {"from": "user_1", "to": "shield_1", "protocol": "HTTPS", "description": None, "encrypted": True},
    {"from": "shield_1", "to": "cloudfront_1", "protocol": "HTTPS", "description": None, "encrypted": True},
    {"from": "cloudfront_1", "to": "waf_1", "protocol": "HTTPS", "description": None, "encrypted": True},
    {"from": "waf_1", "to": "alb_1", "protocol": "HTTPS", "description": None, "encrypted": True},
    {"from": "alb_1", "to": "sei_ec2_1", "protocol": "HTTP", "description": None, "encrypted": False},
    {"from": "sei_ec2_1", "to": "rds_primary", "protocol": "TCP", "description": None, "encrypted": True},
    {"from": "rds_primary", "to": "rds_secondary", "protocol": "TCP", "description": "Replication", "encrypted": True},
    {"from": "sei_ec2_1", "to": "elasticache_1", "protocol": "TCP", "description": None, "encrypted": False},
    {"from": "sei_ec2_1", "to": "solr_1", "protocol": "HTTP", "description": None, "encrypted": False},
    {"from": "sei_ec2_1", "to": "efs_1", "protocol": "NFS", "description": None, "encrypted": True},
]

DUMMY_THREATS = [
    {
        "component_id": "waf_1",
        "threat_type": "Denial of Service",
        "description": "DoS attacks targeting the WAF",
        "mitigation": "Mitigado por AWS Shield e WAF. Rate limiting e regras de mitigação configuradas.",
        "dread_score": 4.2,
        "dread_details": {"damage": 6, "reproducibility": 4, "exploitability": 5, "affected_users": 4, "discoverability": 2},
    },
    {
        "component_id": "rds_primary",
        "threat_type": "Information Disclosure",
        "description": "Vazamento de dados sensíveis do banco",
        "mitigation": "Risco médio. KMS para criptografia em repouso. Recomenda-se revisar IAM e políticas de acesso.",
        "dread_score": 6.4,
        "dread_details": {"damage": 8, "reproducibility": 5, "exploitability": 6, "affected_users": 7, "discoverability": 6},
    },
    {
        "component_id": "user_1",
        "threat_type": "Spoofing",
        "description": "Spoofing no fluxo User -> Shield",
        "mitigation": "Risco alto. Falta Cognito ou autenticação centralizada. Implementar AWS Cognito.",
        "dread_score": 7.2,
        "dread_details": {"damage": 8, "reproducibility": 7, "exploitability": 7, "affected_users": 7, "discoverability": 7},
    },
    {
        "component_id": "cloudtrail_1",
        "threat_type": "Repudiation",
        "description": "Negação de ações realizadas",
        "mitigation": "Mitigado. CloudTrail registra auditoria de todas as ações na conta AWS.",
        "dread_score": 2.8,
        "dread_details": {"damage": 4, "reproducibility": 2, "exploitability": 2, "affected_users": 3, "discoverability": 3},
    },
    {
        "component_id": "sei_ec2_1",
        "threat_type": "Elevation of Privilege",
        "description": "Comprometimento de instância EC2",
        "mitigation": "SSM, patch management, IAM roles com least privilege. Revisar security groups.",
        "dread_score": 5.6,
        "dread_details": {"damage": 7, "reproducibility": 5, "exploitability": 5, "affected_users": 6, "discoverability": 5},
    },
]


class DummyPipeline:
    """Pipeline that returns fixed AWS SEI data - for testing without models."""

    async def run(self, image_bytes: bytes, **kwargs: object) -> dict:
        """Return dummy analysis result."""
        logger.info("Using DummyPipeline - returning fixed AWS SEI data")
        threats = DUMMY_THREATS
        risk_score = sum(t["dread_score"] for t in threats) / len(threats) if threats else 0
        risk_level = RiskLevel.from_score(risk_score)
        return {
            "model_used": "DummyPipeline",
            "components": DUMMY_COMPONENTS,
            "connections": DUMMY_CONNECTIONS,
            "threats": threats,
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "processing_time": 0.1,
        }
