"""Logging configuration for Threat Modeling AI services."""

import logging
import sys
from typing import Literal


def setup_logging(
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
) -> logging.Logger:
    """Configure application logging.

    Args:
        level: The logging level to use.

    Returns:
        The configured root logger.
    """
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=getattr(logging, level),
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Reduce noise from third-party libraries
    for name in ("httpx", "httpcore", "chromadb", "langchain", "uvicorn.access"):
        logging.getLogger(name).setLevel(logging.WARNING)

    logger = logging.getLogger("threat_modeling")
    logger.info("Logging configured at level: %s", level)
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(f"threat_modeling.{name}")
