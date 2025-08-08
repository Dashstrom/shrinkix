"""Init module of shrinkix."""

from .cli import entrypoint
from .info import (
    __author__,
    __copyright__,
    __email__,
    __issues__,
    __license__,
    __maintainer__,
    __maintainer_email__,
    __project__,
    __summary__,
    __version__,
)
from .shrinker import Shrinkix

__all__ = [
    "Shrinkix",
    "__author__",
    "__copyright__",
    "__email__",
    "__issues__",
    "__license__",
    "__maintainer__",
    "__maintainer_email__",
    "__project__",
    "__summary__",
    "__version__",
    "entrypoint",
    "shrinkix",
]
