"""Main module."""

from .cli import entrypoint
from .info import (
    __author__,
    __email__,
    __summary__,
    __version__,
)
from .shrinker import Shrinkix

__all__ = [
    "Shrinkix",
    "__author__",
    "__email__",
    "__summary__",
    "__version__",
    "entrypoint",
]
