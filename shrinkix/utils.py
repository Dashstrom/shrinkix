"""Utils functions."""

import pathlib
from typing import IO, Literal, Union

from PIL import Image

PathLike = Union[str, pathlib.Path]
PathOrFile = Union[PathLike, IO[bytes]]
AllImageSource = Union[PathOrFile, Image.Image, Image.SupportsArrayInterface]
Formats = Literal["PNG", "JPEG", "JPG", "WEBP"]
FORMAT_MAPPER: dict[str, Formats] = {
    "png": "PNG",
    "jpeg": "JPEG",
    "jpg": "JPEG",
    "webp": "WEBP",
}


def verify_format(format: str) -> Formats:  # noqa: A002
    """Get normalize format and raise error if not supported."""
    key = format.casefold().replace(".", "")
    if key in FORMAT_MAPPER:
        return FORMAT_MAPPER[key]
    message_error = f"Invalid format {format!r}"
    raise ValueError(message_error)


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


def size(path: pathlib.Path, suffix: str = "B") -> str:
    """Return the human readable size."""
    num: float = path.stat().st_size
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:  # noqa: PLR2004
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"
