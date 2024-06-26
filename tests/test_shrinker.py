"""Basic test for validation code can run on every os.

test.png: https://www.pexels.com/fr-fr/photo/route-en-beton-entre-les-arbres-1563356/
"""

import io
import pathlib

from shrinkix import Shrinkix


def test_shrink(image_path: pathlib.Path) -> None:
    """Check if image is shrink."""
    shrinker = Shrinkix(max_width=512, max_height=512)
    with io.BytesIO() as stream:
        shrinker.shrink(image_path, output=stream)
        assert image_path.stat().st_size > len(stream.getbuffer())
