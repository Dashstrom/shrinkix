"""Configuration for all tests."""

import pathlib

import pytest


@pytest.fixture
def resources() -> pathlib.Path:
    """Open test image."""
    return pathlib.Path(__file__).parent.resolve() / "tests" / "resources"


@pytest.fixture
def image_path(resources: pathlib.Path) -> pathlib.Path:
    """Open test image."""
    return resources / "test.jpg"
