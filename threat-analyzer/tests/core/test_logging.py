"""Unit tests for threat_modeling_shared.logging."""

import logging

from threat_modeling_shared.logging import get_logger, setup_logging


def test_setup_logging():
    logger = setup_logging("INFO")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "threat_modeling"


def test_get_logger():
    log = get_logger("test")
    assert log.name == "threat_modeling.test"
