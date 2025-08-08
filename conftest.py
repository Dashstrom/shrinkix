"""Configuration for all tests."""

from pathlib import Path

import pytest


@pytest.fixture
def resources() -> Path:
    """Open test image."""
    return Path(__file__).parent.resolve() / "tests" / "resources"


@pytest.fixture
def image_path(resources: Path) -> Path:
    """Open test image."""
    return resources / "test.jpg"
