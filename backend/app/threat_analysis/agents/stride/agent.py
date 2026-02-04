"""STRIDE threat analysis agent with RAG support and LLM fallback."""

from typing import Any

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import Settings
from app.core.logging import get_logger
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
        self._cache = LLMCacheService()
        self._retriever = self._setup_rag()

    def _setup_rag(self) -> Any | None:
        """Set up RAG retriever from knowledge base."""
        kb_path = self.settings.knowledge_base_path
        if not kb_path or not kb_path.exists():
            logger.warning("Knowledge base path not found. Running without RAG.")
            return None
        try:
            md_files = list(kb_path.glob("*.md"))
            all_docs = []
            for file_path in md_files:
                try:
                    loader = TextLoader(str(file_path), encoding="utf-8")
                    all_docs.extend(loader.load())
                except Exception as e:
                    logger.warning("Failed to load %s: %s", file_path.name, e)
            if not all_docs:
                return None
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.settings.rag_chunk_size,
                chunk_overlap=self.settings.rag_chunk_overlap,
            )
            chunks = splitter.split_documents(all_docs)
            embeddings = GoogleGenerativeAIEmbeddings(
                model=self.settings.embedding_model,
                google_api_key=self.settings.google_api_key,
            )
            vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)
            return vectorstore.as_retriever()
        except Exception as e:
            logger.error("RAG setup failed: %s", e)
            return None

    async def analyze(self, diagram_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Analyze diagram for STRIDE threats."""
        logger.info("Starting STRIDE analysis")
        context = ""
        if self._retriever:
            try:
                docs = self._retriever.get_relevant_documents(
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
            boundaries=", ".join(diagram_data.get("boundaries", [])) or "None identified",
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
