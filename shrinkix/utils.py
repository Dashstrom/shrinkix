"""Utils functions."""

import pathlib
from typing import IO, Any, Union

import numpy.typing as npt
from PIL import Image

PathLike = Union[str, pathlib.Path]
PathOrFile = Union[PathLike, IO[bytes]]
AllImageSource = Union[PathOrFile, Image.Image, npt.NDArray[Any]]


def open_image(image: AllImageSource) -> Image.Image:
    """Open image from all sources."""
    # Load image
    if isinstance(image, (str, pathlib.PurePath)):
        path = pathlib.Path(image)
        im: Image.Image = Image.open(path.open("rb"))
    elif isinstance(image, Image.Image):
        im = image
    else:
        try:
            im = Image.fromarray(image)  # type: ignore[arg-type]
        except AttributeError:
            im = Image.open(image)  # type: ignore[arg-type]
    return im


def ratio(before: pathlib.Path, after: pathlib.Path) -> float:
    """Return compression ratio."""
    return after.stat().st_size / before.stat().st_size
