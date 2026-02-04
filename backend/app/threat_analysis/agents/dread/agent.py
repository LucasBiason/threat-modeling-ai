"""DREAD risk scoring agent with LLM fallback."""

import json
from typing import Any

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

logger = get_logger("agents.dread")

DREAD_SYSTEM_PROMPT = """You are an expert security analyst specializing in DREAD risk scoring.

DREAD is a risk assessment model that scores threats on 5 dimensions (each 1-10):

- Damage (D): How much damage could result if the vulnerability is exploited?
- Reproducibility (R): How easy is it to reproduce the attack?
- Exploitability (E): How easy is it to launch an attack?
- Affected Users (A): How many users would be affected?
- Discoverability (D): How easy is it to discover the vulnerability?

Be consistent and realistic in your scoring."""

DREAD_USER_PROMPT = """Score the following threats using DREAD methodology.

Threats to score:
{threats}

For each threat, return the original threat object with added DREAD scoring:
- dread_score: the average of all 5 DREAD scores (rounded to 2 decimal places)
- dread_details: object with individual scores (damage, reproducibility, exploitability, affected_users, discoverability)

Return ONLY a JSON list with the scored threats."""

CONNECTION_ORDER = [GeminiConnection, OpenAIConnection, OllamaConnection]


def _validate_dread_result(result: Any) -> bool:
    """Validate DREAD result is a list of threats."""
    return isinstance(result, list)


class DreadAgent(BaseAgent):
    """Agent for DREAD risk scoring with LLM fallback."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._cache = LLMCacheService()

    async def analyze(self, threats: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Score threats using DREAD methodology."""
        if not threats:
            return []
        logger.info("Starting DREAD scoring for %d threats", len(threats))
        threats_str = json.dumps(threats, indent=2)
        user_content = DREAD_USER_PROMPT.format(threats=threats_str)
        messages = [
            {"role": "system", "content": DREAD_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]
        result = await run_text_with_fallback(
            connections=CONNECTION_ORDER,
            settings=self.settings,
            messages=messages,
            cache_get=self._cache.get,
            cache_set=self._cache.set,
            cache_key_prefix="dread",
            validate=_validate_dread_result,
        )
        if "error" in result:
            logger.error("DREAD scoring failed: %s", result.get("error"))
            return threats  # Return original without scores
        scored = result if isinstance(result, list) else threats
        for t in scored:
            if "dread_score" in t:
                t["dread_score"] = max(1, min(10, t["dread_score"]))
        return scored
