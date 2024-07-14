"""Basic test for validation code can run on every os.

test.png: https://www.pexels.com/fr-fr/photo/route-en-beton-entre-les-arbres-1563356/
"""

import io
import pathlib

import numpy as np
from PIL import Image

from shrinkix import Shrinkix


def test_shrink_path(image_path: pathlib.Path) -> None:
    """Check if image is shrink."""
    shrinker = Shrinkix(max_width=512, max_height=512)
    with io.BytesIO() as stream:
        shrinker.shrink(image_path, output=stream)
        assert image_path.stat().st_size > len(stream.getbuffer())


def test_shrink_array(image_path: pathlib.Path) -> None:
    """Check if image is shrink."""
    shrinker = Shrinkix(max_width=512, max_height=512)
    with io.BytesIO() as stream:
        im = Image.open(image_path)
        arr = np.asarray(im)
        shrinker.shrink(arr, output=stream)
        assert image_path.stat().st_size > len(stream.getbuffer())


def test_shrink_stream(image_path: pathlib.Path) -> None:
    """Check if image is shrink."""
    shrinker = Shrinkix(max_width=512, max_height=512)
    with io.BytesIO() as stream:
        shrinker.shrink(image_path.open("rb"), output=stream)
        assert image_path.stat().st_size > len(stream.getbuffer())
