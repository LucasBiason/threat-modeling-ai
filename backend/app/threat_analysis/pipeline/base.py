"""Pipeline base protocol."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ThreatAnalysisPipeline(Protocol):
    """Protocol for threat analysis pipelines (Dummy, YOLO, LLM, Hybrid)."""

    async def run(self, image_bytes: bytes, **kwargs: object) -> dict:
        """Run full analysis and return raw result dict.

        Returns:
            Dict with keys: model_used, components, connections, threats,
            risk_score, risk_level, processing_time.
        """
        ...
