"""Diagram analysis agent using LLM connections with fallback."""

from typing import Any

from threat_modeling_shared.logging import get_logger

from app.config import Settings
from app.threat_analysis.agents.base import BaseAgent
from app.threat_analysis.llm import (
    GeminiConnection,
    LLMCacheService,
    OllamaConnection,
    OpenAIConnection,
    run_vision_with_fallback,
)

logger = get_logger("agents.diagram")

DIAGRAM_PROMPT = """
Analyze this architecture diagram.

1. Identify all components (Users, Servers, Databases, Gateways, Load Balancers, etc.).
2. Identify the connections and data flows between them.
3. Identify trust boundaries (e.g., VPCs, Public/Private subnets, DMZs).

Return ONLY a valid JSON object structured as:
{
  "model": "model_name",
  "components": [{"id": "unique_id", "type": "ComponentType", "name": "Display Name"}],
  "connections": [{"from": "source_id", "to": "target_id", "protocol": "HTTPS/HTTP/TCP/etc"}],
  "boundaries": ["boundary name 1", "boundary name 2"]
}

Important:
- Each component must have a unique id
- Use descriptive component types (User, Server, Database, Gateway, LoadBalancer, Cache, Queue, API, Service)
- Include the communication protocol for each connection when visible
"""

CONNECTION_ORDER = [GeminiConnection, OpenAIConnection, OllamaConnection]


def _validate_diagram_result(result: dict[str, Any]) -> bool:
    """Validate diagram analysis result."""
    if not isinstance(result, dict) or "error" in result:
        return False
    components = result.get("components", [])
    if not isinstance(components, list):
        return False
    return True


class DiagramAgent(BaseAgent):
    """Agent for analyzing architecture diagrams using vision LLMs with fallback."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._cache = LLMCacheService(redis_url=settings.redis_url)

    async def analyze(self, image_bytes: bytes) -> dict[str, Any]:
        """Analyze an architecture diagram image."""
        logger.info("Starting diagram analysis")

        result = await run_vision_with_fallback(
            connections=CONNECTION_ORDER,
            settings=self.settings,
            prompt=DIAGRAM_PROMPT,
            image_bytes=image_bytes,
            cache_get=self._cache.get,
            cache_set=self._cache.set,
            cache_key_prefix="diagram",
            validate=_validate_diagram_result,
        )

        if "error" in result:
            logger.error("Diagram analysis failed: %s", result.get("error"))
            return self._get_fallback_data()

        logger.info(
            "Diagram analysis complete: %d components, %d connections",
            len(result.get("components", [])),
            len(result.get("connections", [])),
        )
        return result

    def _get_fallback_data(self) -> dict[str, Any]:
        """Get fallback data when analysis fails."""
        return {
            "model": "Fallback/Error",
            "components": [
                {"id": "unknown_1", "type": "Unknown", "name": "Unanalyzed Component"}
            ],
            "connections": [],
            "boundaries": [],
        }
