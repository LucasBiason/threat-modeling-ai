"""Fallback runner - try LLMs in order, validate, return first success."""

from collections.abc import Callable
from typing import Any, TypeVar

from app.core.logging import get_logger
from app.threat_analysis.llm.base import LLMConnection

logger = get_logger("llm.fallback")

T = TypeVar("T")


def is_error_result(result: dict[str, Any]) -> bool:
    """Check if result indicates an error."""
    return "error" in result


async def run_vision_with_fallback(
    connections: list[type[LLMConnection]],
    settings: Any,
    prompt: str,
    image_bytes: bytes,
    cache_get: Callable[[str, ...], Any | None] | None = None,
    cache_set: Callable[[str, Any, ...], None] | None = None,
    cache_key_prefix: str = "diagram",
    validate: Callable[[dict[str, Any]], bool] | None = None,
) -> dict[str, Any]:
    """Try each connection in order; return first valid result or aggregated errors.

    Args:
        connections: List of LLMConnection classes (not instances).
        settings: Settings to pass to each connection.
        prompt: Vision prompt.
        image_bytes: Image bytes.
        cache_get: Optional cache getter (prefix, *args) -> value or None.
        cache_set: Optional cache setter (prefix, value, *args).
        cache_key_prefix: Prefix for cache key.
        validate: Optional validator(result) -> bool. Default: not is_error_result.

    Returns:
        Valid result dict or {"error": str, "engine_errors": list}.
    """
    validator = validate or (lambda r: not is_error_result(r))

    # Check cache
    if cache_get:
        cached = cache_get(cache_key_prefix, prompt, image_bytes)
        if cached is not None and validator(cached):
            logger.info("Returning cached LLM result")
            return cached

    errors: list[dict[str, Any]] = []
    for conn_class in connections:
        conn = conn_class(settings)  # Lazy: instantiate only when we try
        if not conn.is_configured():
            logger.debug("%s not configured, skipping", conn.name)
            continue
        logger.info("Trying LLM: %s", conn.name)
        try:
            result = await conn.invoke_vision(prompt, image_bytes)
            if validator(result):
                logger.info("Success with %s", conn.name)
                if cache_set:
                    cache_set(cache_key_prefix, result, prompt, img_hash)
                return result
            err_info = result if isinstance(result.get("error"), str) else {"error": str(result)}
            errors.append({"engine": conn.name, **err_info})
        except Exception as e:
            errors.append({"engine": conn.name, "error": str(e), "error_type": "exception"})
            logger.warning("%s failed: %s", conn.name, e)

    return {
        "error": "All LLM providers failed",
        "engine_errors": errors,
    }


async def run_text_with_fallback(
    connections: list[type[LLMConnection]],
    settings: Any,
    messages: list[dict[str, str]],
    cache_get: Callable[[str, ...], Any | None] | None = None,
    cache_set: Callable[[str, Any, ...], None] | None = None,
    cache_key_prefix: str = "text",
    validate: Callable[[dict[str, Any]], bool] | None = None,
) -> dict[str, Any]:
    """Try each connection for text-only invocation."""
    validator = validate or (lambda r: not is_error_result(r))

    if cache_get:
        import json

        key = json.dumps(messages, sort_keys=True)
        cached = cache_get(cache_key_prefix, key)
        if cached is not None and validator(cached):
            logger.info("Returning cached LLM result")
            return cached

    errors: list[dict[str, Any]] = []
    for conn_class in connections:
        conn = conn_class(settings)
        if not conn.is_configured():
            continue
        logger.info("Trying LLM: %s", conn.name)
        try:
            result = await conn.invoke_text(messages)
            if validator(result):
                logger.info("Success with %s", conn.name)
                if cache_set:
                    import json

                    cache_set(cache_key_prefix, result, json.dumps(messages, sort_keys=True))
                return result
            errors.append({"engine": conn.name, "error": result.get("error", str(result))})
        except Exception as e:
            errors.append({"engine": conn.name, "error": str(e), "error_type": "exception"})

    return {"error": "All LLM providers failed", "engine_errors": errors}
