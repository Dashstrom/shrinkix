"""Utility functions and type aliases for image processing."""

import pathlib
from typing import IO, Literal

from PIL import Image

PathLike = str | pathlib.Path
PathOrFile = PathLike | IO[bytes]
Formats = Literal["PNG", "JPEG", "JPG", "WEBP"]
AllImageSource = PathOrFile | Image.Image | Image.SupportsArrayInterface


FORMAT_MAPPER: dict[str, Formats] = {
    "png": "PNG",
    "jpeg": "JPEG",
    "jpg": "JPEG",
    "webp": "WEBP",
}


def verify_format(format: str) -> Formats:  # noqa: A002
    """Normalize and verify an image format string.

    Converts a format string to uppercase standard form and
    raises an error if the format is unsupported.

    Args:
        format: Image format string (e.g. "png", ".jpg").

    Returns:
        Normalized format string (e.g. "PNG", "JPEG").

    Raises:
        ValueError: If the format is not supported.
    """
    key = format.casefold().replace(".", "")
    if key in FORMAT_MAPPER:
        return FORMAT_MAPPER[key]
    message_error = f"Invalid format {format!r}"
    raise ValueError(message_error)


def open_image(image: AllImageSource) -> Image.Image:
    """Open an image from a path, file-like object, PIL Image, or array.

    Args:
        image: Image source which may be a file path, file object,
               PIL Image instance, or array-like object.

    Returns:
        A PIL Image object representing the image.
    """
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
    """Compute the compression ratio between two files.

    Args:
        before: Path to the original file.
        after: Path to the compressed/processed file.

    Returns:
        Compression ratio as a float (after size / before size).
    """
    return after.stat().st_size / before.stat().st_size


def size(path: pathlib.Path, suffix: str = "B") -> str:
    """Return a human-readable file size string for a given path.

    Args:
        path: Path to the file.
        suffix: Size unit suffix (default "B" for bytes).

    Returns:
        Human-readable size string (e.g. "3.1MiB", "512.0B").
    """
    num: float = path.stat().st_size
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:  # noqa: PLR2004
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"
