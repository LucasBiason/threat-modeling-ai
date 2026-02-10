"""STRIDE threat analysis agent with RAG support and LLM fallback."""

from typing import Any

from threat_modeling_shared.logging import get_logger

from app.config import Settings
from app.services.rag_service import RAGService
from app.threat_analysis.agents.base import BaseAgent
from app.threat_analysis.llm import (
    GeminiConnection,
    LLMCacheService,
    OllamaConnection,
    OpenAIConnection,
    run_text_with_fallback,
)

logger = get_logger("agents.stride")


STRIDE_SYSTEM_PROMPT = """You are an expert security analyst specializing in STRIDE threat modeling.

STRIDE Categories:
- Spoofing: Pretending to be someone or something else
- Tampering: Modifying data or code without authorization
- Repudiation: Denying having performed an action
- Information Disclosure: Exposing information to unauthorized parties
- Denial of Service: Making a system unavailable
- Elevation of Privilege: Gaining unauthorized access or capabilities

For each component and connection in the architecture, identify potential threats and provide actionable mitigations.

{context}"""

STRIDE_USER_PROMPT = """Based on this architecture diagram analysis:

Components:
{components}

Connections:
{connections}

Trust Boundaries:
{boundaries}

Identify all STRIDE threats. Return a JSON list of threat objects:
[
  {{
    "component_id": "affected_component_id",
    "threat_type": "Spoofing|Tampering|Repudiation|Information Disclosure|Denial of Service|Elevation of Privilege",
    "description": "Clear description of the threat",
    "mitigation": "Specific actionable mitigation"
  }}
]

Be thorough - analyze each component and connection for potential threats.
Return ONLY the JSON list, no additional text."""

CONNECTION_ORDER = [GeminiConnection, OpenAIConnection, OllamaConnection]


def _validate_stride_result(result: Any) -> bool:
    """Validate STRIDE result is a list of threats."""
    return isinstance(result, list)


class StrideAgent(BaseAgent):
    """Agent for STRIDE threat analysis with optional RAG context and LLM fallback."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._cache = LLMCacheService(redis_url=settings.redis_url)
        self._rag_service = RAGService(settings)

    @property
    def _retriever(self) -> Any | None:
        """Retriever RAG com cache (construído uma vez por processo pelo RAGService)."""
        return self._rag_service.get_retriever()

    async def analyze(self, diagram_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Analyze diagram for STRIDE threats."""
        logger.info("Starting STRIDE analysis")
        context = ""
        retriever = self._retriever
        if retriever:
            try:
                docs = retriever.get_relevant_documents(
                    "What are typical STRIDE threats for web applications and microservices?"
                )
                context = "\n\nRelevant context:\n" + "\n".join(
                    [d.page_content for d in docs[:3]]
                )
            except Exception as e:
                logger.warning("RAG retrieval failed: %s", e)
        system_content = STRIDE_SYSTEM_PROMPT.format(context=context)
        user_content = STRIDE_USER_PROMPT.format(
            components=self._format_components(diagram_data.get("components", [])),
            connections=self._format_connections(diagram_data.get("connections", [])),
            boundaries=", ".join(diagram_data.get("boundaries", []))
            or "None identified",
        )
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]
        result = await run_text_with_fallback(
            connections=CONNECTION_ORDER,
            settings=self.settings,
            messages=messages,
            cache_get=self._cache.get,
            cache_set=self._cache.set,
            cache_key_prefix="stride",
            validate=_validate_stride_result,
        )
        if "error" in result:
            logger.error("STRIDE analysis failed: %s", result.get("error"))
            return []
        return result if isinstance(result, list) else []

    def _format_components(self, components: list[dict[str, Any]]) -> str:
        if not components:
            return "None identified"
        return "\n".join(
            f"- [{c.get('id')}] {c.get('type')}: {c.get('name')}" for c in components
        )

    def _format_connections(self, connections: list[dict[str, Any]]) -> str:
        if not connections:
            return "None identified"
        return "\n".join(
            f"- {c.get('from')} -> {c.get('to')} ({c.get('protocol', 'unknown')})"
            for c in connections
        )
