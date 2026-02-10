"""Guardrail: validate that image is a valid architecture diagram.

Rejects images that are not architecture diagrams (photos, sequence diagrams,
flowcharts, random images, etc.) before running the full pipeline.
"""

from __future__ import annotations

from typing import Any

from threat_modeling_shared.logging import get_logger

from app.config import Settings
from app.threat_analysis.exceptions import ArchitectureDiagramValidationError
from app.threat_analysis.llm import (
    GeminiConnection,
    OllamaConnection,
    OpenAIConnection,
    run_vision_with_fallback,
)

logger = get_logger("guardrails.architecture")

GUARDRAIL_PROMPT = """Analyze this image and determine if it is an architecture diagram.

An architecture diagram shows:
- System components (Users, Servers, Databases, Gateways, Load Balancers, APIs, etc.)
- Connections and data flows between components
- Trust boundaries (VPCs, networks, subnets)

NOT valid architecture diagrams:
- Sequence diagrams (UML with actors and messages over time)
- Photos or screenshots of real environments
- Flowcharts or process diagrams
- Generic illustrations or clipart
- Plain text or documents

Return ONLY a valid JSON object:
{"is_architecture_diagram": true/false, "reason": "brief explanation in one sentence"}

Examples:
- Valid: {"is_architecture_diagram": true, "reason": "Diagram shows web server, database, and load balancer with connections"}
- Invalid: {"is_architecture_diagram": false, "reason": "This is a UML sequence diagram showing message flows, not architecture components"}
"""

CONNECTION_ORDER = [GeminiConnection, OpenAIConnection, OllamaConnection]


def _validate_guardrail_result(result: dict[str, Any]) -> bool:
    """Check if guardrail LLM returned a valid structure."""
    if not isinstance(result, dict) or "error" in result:
        return False
    if "is_architecture_diagram" not in result:
        return False
    return True


async def validate_architecture_diagram(
    image_bytes: bytes,
    settings: Settings,
) -> None:
    """Validate that the image is a valid architecture diagram.

    Uses a lightweight LLM vision call to classify the image.
    Raises ArchitectureDiagramValidationError if not valid.

    Args:
        image_bytes: Raw image content.
        settings: Application settings for LLM configuration.

    Raises:
        ArchitectureDiagramValidationError: If the image is not an architecture diagram.
    """
    logger.info("Guardrail: validating image is architecture diagram")

    result = await run_vision_with_fallback(
        connections=CONNECTION_ORDER,
        settings=settings,
        prompt=GUARDRAIL_PROMPT,
        image_bytes=image_bytes,
        cache_get=None,
        cache_set=None,
        cache_key_prefix="guardrail",
        validate=_validate_guardrail_result,
    )

    if "error" in result:
        logger.warning(
            "Guardrail: LLM validation failed, allowing through: %s",
            result.get("error"),
        )
        return

    raw_valid = result.get("is_architecture_diagram", False)
    is_valid = raw_valid is True or (
        isinstance(raw_valid, str) and raw_valid.lower() == "true"
    )
    reason = result.get("reason", "No reason provided") or "No reason provided"

    if not is_valid:
        logger.warning("Guardrail: image rejected - %s", reason)
        raise ArchitectureDiagramValidationError(
            reason=f"Imagem não é um diagrama de arquitetura válido: {reason}",
            details={"llm_reason": reason, "raw_result": result},
        )

    logger.info("Guardrail: image validated as architecture diagram")
