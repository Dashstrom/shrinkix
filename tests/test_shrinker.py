"""Basic tests to verify image shrinking functionality on any OS.

Uses a sample image from:
https://www.pexels.com/fr-fr/photo/route-en-beton-entre-les-arbres-1563356/
"""

import io
import pathlib

import numpy as np
from PIL import Image

from shrinkix import Shrinkix


def test_shrink_input_path(image_path: pathlib.Path) -> None:
    """Verify that shrinking an image from a file path reduces its size.

    Args:
        image_path: Path to the input image file.
    """
    shrinker = Shrinkix(max_width=512, max_height=512)
    with io.BytesIO() as output_stream:
        shrinker.shrink(image_path, output=output_stream)
        # Check that the shrunk image size is smaller than original file size
        assert image_path.stat().st_size > len(output_stream.getbuffer())


def test_shrink_output_path(
    image_path: pathlib.Path,
    tmp_path: pathlib.Path,
) -> None:
    """Verify that shrinking an image and saving to a file reduces its size."""
    shrinker = Shrinkix(max_width=512, max_height=512)
    with io.BytesIO() as output_stream:
        output_file = tmp_path / image_path.name
        shrinker.shrink(image_path, output=output_file)
        # Confirm the shrunk file size is smaller than the original image size
        assert image_path.stat().st_size > len(output_stream.getbuffer())


def test_shrink_input_array(image_path: pathlib.Path) -> None:
    """Verify shrinking an image from a numpy array reduces its size."""
    shrinker = Shrinkix(max_width=512, max_height=512)
    with io.BytesIO() as output_stream:
        image = Image.open(image_path)
        image_array = np.asarray(image)
        shrinker.shrink(image_array, output=output_stream, format="JPEG")
        # Ensure shrunk image size is smaller than original file size
        assert image_path.stat().st_size > len(output_stream.getbuffer())


def test_shrink_input_stream(image_path: pathlib.Path) -> None:
    """Verify shrinking an image from a binary stream reduces its size."""
    shrinker = Shrinkix(max_width=512, max_height=512)
    with io.BytesIO() as output_stream, image_path.open("rb") as input_stream:
        shrinker.shrink(input_stream, output=output_stream, format="JPEG")
        # Confirm shrunk image size is smaller than original file size
        assert image_path.stat().st_size > len(output_stream.getbuffer())


def test_shrink_input_stream_exp(image_path: pathlib.Path) -> None:
    """Verify shrinking with experimental color reduction."""
    shrinker = Shrinkix(
        max_width=512,
        max_height=512,
        experimental_color_reduction=True,
    )
    with io.BytesIO() as output_stream, image_path.open("rb") as input_stream:
        shrinker.shrink(input_stream, output=output_stream, format="JPEG")
        # Confirm shrunk image size is smaller than original file size
        assert image_path.stat().st_size > len(output_stream.getbuffer())


def test__artist(image_path: pathlib.Path) -> None:
    """Verify shrinking with artists metadata."""
    shrinker = Shrinkix(
        max_width=512,
        max_height=512,
        experimental_color_reduction=True,
        artist="Plop",
        copyright="Mine picture",
    )
    with io.BytesIO() as output_stream, image_path.open("rb") as input_stream:
        shrinker.shrink(input_stream, output=output_stream, format="JPEG")
        # Confirm shrunk image size is smaller than original file size
        assert image_path.stat().st_size > len(output_stream.getbuffer())
