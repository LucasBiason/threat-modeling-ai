"""Pytest fixtures for threat-analyzer tests."""

import os
from pathlib import Path

import pytest

# Ensure threat-analyzer/app is on path when running from project root
_root = Path(__file__).resolve().parent.parent
if str(_root) not in os.environ.get("PYTHONPATH", ""):
    import sys

    sys.path.insert(0, str(_root))


@pytest.fixture
def sample_image_bytes():
    """Minimal valid PNG bytes (1x1 pixel)."""
    return (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
        b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
