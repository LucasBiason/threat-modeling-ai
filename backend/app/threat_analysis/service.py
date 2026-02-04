"""Threat Analysis service orchestrating the analysis pipeline."""

import time
from functools import lru_cache
from typing import Any

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

from .agents import DiagramAgent, DreadAgent, StrideAgent
from .pipeline import DummyPipeline
from .schemas import AnalysisResponse, Component, Connection, RiskLevel, Threat

logger = get_logger("service")


class ThreatModelService:
    """Service for orchestrating threat model analysis."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the service with lazy-loaded agents.

        Args:
            settings: Application settings.
        """
        self._settings = settings
        self._diagram_agent: DiagramAgent | None = None
        self._stride_agent: StrideAgent | None = None
        self._dread_agent: DreadAgent | None = None

    @property
    def diagram_agent(self) -> DiagramAgent:
        """Get or create the diagram analysis agent."""
        if self._diagram_agent is None:
            self._diagram_agent = DiagramAgent(self._settings)
        return self._diagram_agent

    @property
    def stride_agent(self) -> StrideAgent:
        """Get or create the STRIDE analysis agent."""
        if self._stride_agent is None:
            self._stride_agent = StrideAgent(self._settings)
        return self._stride_agent

    @property
    def dread_agent(self) -> DreadAgent:
        """Get or create the DREAD scoring agent."""
        if self._dread_agent is None:
            self._dread_agent = DreadAgent(self._settings)
        return self._dread_agent

    async def run_full_analysis(self, image_bytes: bytes) -> AnalysisResponse:
        """Run the complete threat analysis pipeline.

        Runs Diagram -> STRIDE -> DREAD agents with LLM fallback.
        DummyPipeline só quando use_dummy_pipeline=True (ex.: testes unitários).
        """
        if self._settings.use_dummy_pipeline:
            return await self._run_dummy_pipeline(image_bytes)

        start_time = time.time()

        # Stage 1: Diagram Analysis
        logger.info("Stage 1: Diagram Analysis")
        diagram_data = await self.diagram_agent.analyze(image_bytes)

        # Stage 2: STRIDE Analysis
        logger.info("Stage 2: STRIDE Analysis")
        threats = await self.stride_agent.analyze(diagram_data)

        # Stage 3: DREAD Scoring
        logger.info("Stage 3: DREAD Scoring")
        scored_threats = await self.dread_agent.analyze(threats)

        # Calculate overall risk
        risk_score = self._calculate_risk_score(scored_threats)
        risk_level = RiskLevel.from_score(risk_score)

        processing_time = round(time.time() - start_time, 2)
        logger.info(
            "Analysis complete: %d components, %d threats, risk=%s (%.2f) in %.2fs",
            len(diagram_data.get("components", [])),
            len(scored_threats),
            risk_level.value,
            risk_score,
            processing_time,
        )

        return AnalysisResponse(
            model_used=diagram_data.get("model", "Unknown"),
            components=self._parse_components(diagram_data.get("components", [])),
            connections=self._parse_connections(diagram_data.get("connections", [])),
            threats=self._parse_threats(scored_threats),
            risk_score=round(risk_score, 2),
            risk_level=risk_level,
            processing_time=processing_time,
        )

    async def _run_dummy_pipeline(self, image_bytes: bytes) -> AnalysisResponse:
        """Run dummy pipeline and convert to AnalysisResponse."""
        pipeline = DummyPipeline()
        result = await pipeline.run(image_bytes)
        return AnalysisResponse(
            model_used=result["model_used"],
            components=self._parse_components(result["components"]),
            connections=self._parse_connections(result["connections"]),
            threats=self._parse_threats(result["threats"]),
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            processing_time=result["processing_time"],
        )

    def _calculate_risk_score(self, threats: list[dict[str, Any]]) -> float:
        """Calculate the overall risk score from scored threats.

        Args:
            threats: List of threats with DREAD scores.

        Returns:
            Average risk score (0-10).
        """
        if not threats:
            return 0.0

        total_score = sum(t.get("dread_score", 0) for t in threats)
        return total_score / len(threats)

    def _parse_components(self, components: list[dict[str, Any]]) -> list[Component]:
        """Parse raw component data into schema objects.

        Args:
            components: Raw component dictionaries from diagram analysis.

        Returns:
            List of validated Component objects.
        """
        result = []
        for comp in components:
            try:
                result.append(
                    Component(
                        id=comp.get("id", "unknown"),
                        type=comp.get("type", "Unknown"),
                        name=comp.get("name", "Unnamed"),
                        description=comp.get("description"),
                    )
                )
            except Exception as e:
                logger.warning("Failed to parse component: %s", str(e))
        return result

    def _parse_connections(self, connections: list[dict[str, Any]]) -> list[Connection]:
        """Parse raw connection data into schema objects.

        Args:
            connections: Raw connection dictionaries from diagram analysis.

        Returns:
            List of validated Connection objects.
        """
        result = []
        for conn in connections:
            try:
                result.append(
                    Connection(
                        from_id=conn.get("from", "unknown"),
                        to_id=conn.get("to", "unknown"),
                        protocol=conn.get("protocol"),
                        description=conn.get("description"),
                        encrypted=conn.get("encrypted"),
                    )
                )
            except Exception as e:
                logger.warning("Failed to parse connection: %s", str(e))
        return result

    def _parse_threats(self, threats: list[dict[str, Any]]) -> list[Threat]:
        """Parse raw threat data into schema objects.

        Args:
            threats: Raw threat dictionaries from STRIDE/DREAD analysis.

        Returns:
            List of validated Threat objects.
        """
        result = []
        for threat in threats:
            try:
                result.append(
                    Threat(
                        component_id=threat.get("component_id", "unknown"),
                        threat_type=threat.get("threat_type", "Unknown"),
                        description=threat.get("description", "No description"),
                        mitigation=threat.get("mitigation", "No mitigation provided"),
                        dread_score=threat.get("dread_score"),
                        dread_details=threat.get("dread_details"),
                    )
                )
            except Exception as e:
                logger.warning("Failed to parse threat: %s", str(e))
        return result


@lru_cache
def get_threat_model_service() -> ThreatModelService:
    """Get cached service instance for dependency injection.

    Returns:
        Singleton ThreatModelService instance.
    """
    settings = get_settings()
    return ThreatModelService(settings)
