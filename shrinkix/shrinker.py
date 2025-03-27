"""Module for shrink images."""

import pathlib
from math import floor, sqrt
from time import time
from typing import Any, Literal, Optional

from PIL import Image
from tqdm import tqdm

from .utils import (
    AllImageSource,
    PathLike,
    PathOrFile,
    open_image,
    ratio,
    size,
)

MAX_COLORS = 256
MAX_SAMPLE = 100_00


class Shrinkix:
    def __init__(  # noqa: PLR0913
        self,
        *,
        format: Optional[Literal["PNG", "JPEG", "JPG", "WEBP"]] = None,  # noqa: A002
        keep_metadata: Optional[bool] = None,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        experimental_color_reduction: Optional[bool] = None,
        verbose: bool = False,
        artist: Optional[str] = None,
        copyright: Optional[str] = None,  # noqa: A002
        background: Optional[str] = None,
        quality: Optional[int] = None,
    ) -> None:
        """Instantiate Shrinkix."""
        self.keep_metadata = keep_metadata is True
        self.experimental_color_reduction = bool(experimental_color_reduction)
        self.max_width = max_width
        self.max_height = max_height
        self.verbose = verbose
        self.copyright = copyright
        self.artist = artist
        self.background = background
        self.quality = int(quality) if quality is not None else None
        if format is None:
            self.format = "PNG"
        elif format.casefold() == "jpg":
            self.format = "JPEG"
        else:
            self.format = format.upper()

    def shrink(  # noqa: PLR0912, C901
        self,
        image: AllImageSource,
        output: PathOrFile,
        colors: Optional[int] = None,
    ) -> None:
        """Shrink an image."""
        # Load image
        im = open_image(image)

        # Find th best ratio
        w, h = im.size
        ratio = 1.0
        if self.max_width is not None and w > self.max_width:
            ratio = min(self.max_width / w, ratio)
        if self.max_height is not None and h > self.max_height:
            ratio = min(self.max_height / h, ratio)
        if ratio != 1.0:
            im = im.resize(
                (floor(w * ratio), floor(h * ratio)),
                resample=Image.Resampling.NEAREST,
            )

        # Replace background
        if self.background is not None:
            new_im = Image.new("RGBA", im.size, self.background)
            new_im.paste(im, (0, 0), im.convert("RGBA"))
            im = new_im.convert("RGB")

        # Remove metadata
        if not self.keep_metadata:
            data = list(im.convert("RGBA").getdata())
            im = Image.new("RGBA", im.size)
            im.putdata(data)

        # Reduce colors
        im = self.reduce(im, colors=colors)
        options: dict[str, Any] = {"format": self.format}

        # Add exif information
        import piexif

        if self.artist is not None or self.copyright is not None:
            exif_dict: dict[str, Any] = {"0th": {}}
            if self.artist is not None:
                exif_dict["0th"][piexif.ImageIFD.Artist] = self.artist
            if self.copyright is not None:
                exif_dict["0th"][piexif.ImageIFD.Copyright] = self.copyright
            options["exif"] = piexif.dump(exif_dict)

        # Save with optimization
        if self.quality is None:
            quality = floor(30 + 65 * (1 - min(sqrt(w * h) / 4096, 1)))
        else:
            quality = self.quality
        # https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#png
        if self.format == "PNG":
            options["optimize"] = True
        # https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg
        elif self.format == "JPEG":
            options["quality"] = quality
        # https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#webp
        elif self.format == "WEBP":
            options["lossless"] = False
            options["quality"] = quality
            options["alpha_quality"] = quality
            options["method"] = 6
        if isinstance(output, (str, pathlib.PurePath)):
            output_path = pathlib.Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            im.save(output_path, **options)
        else:
            im.save(output, **options)

    def export_name(self, path: pathlib.Path) -> str:
        """Export name."""
        return path.with_suffix(f".{self.format.lower()}").name

    def bulk(
        self,
        files: list[PathLike],
        output: PathLike,
        colors: Optional[int] = None,
    ) -> None:
        """Shrink a list of file and export it in output."""
        root = pathlib.Path(output)
        paths = {}
        for file in files:
            path = pathlib.Path(file)
            if path.is_dir():
                for sub_path in path.glob("**/*"):
                    if sub_path.is_file():
                        output_path = root / self.export_name(sub_path)
                        paths[sub_path] = output_path
            else:
                output_path = root / self.export_name(path)
                paths[path] = output_path

        with tqdm(paths.items()) as bar:
            for src, dst in bar:
                bar.write(f"Shrinking {src}")
                start = time()
                self.shrink(src, dst, colors=colors)
                end = time()
                elapsed = end - start
                bar.write(
                    f"Export at {dst}, "
                    f"ratio: {ratio(src, dst):.2%}, time: {elapsed:.3f}s, "
                    f"size: {size(src)} to {size(dst)}",
                )

    def reduce(
        self,
        image: AllImageSource,
        colors: Optional[int] = None,
    ) -> Image.Image:
        """Reduce image colors."""
        # Open and format for model
        im = open_image(image)

        # Palette is not supported on JPEG or WEBP
        if self.format in ("JPEG", "WEBP"):
            return im.convert("RGB") if im.mode != "RGB" else im

        # No optimization on palette or black and white
        if im.mode in ("L", "LA", "P", "PA"):
            return im

        # Detect if alpha
        if im.mode == "RGBA":
            alpha = True
        elif im.mode == "RGB":
            alpha = False
        else:
            im = im.convert("RGBA")
            alpha = True

        # Convert data to numpy array
        import numpy as np

        arr = np.asarray(im)
        h, w = arr.shape[:2]
        X = arr.reshape(-1, 4 if alpha else 3)  # noqa: N806

        if colors is None:
            if X.shape[0] > MAX_SAMPLE:
                index = np.random.choice(X.shape[0], MAX_SAMPLE, replace=False)  # noqa: NPY002
                sample = X[index]
            else:
                sample = X
            _, block_counts = np.unique(
                sample // 16,
                axis=0,
                return_counts=True,
            )
            colors = len(block_counts)
            colors = min(colors, MAX_COLORS)

        if not self.experimental_color_reduction:
            return im.quantize(colors)

        # Create model
        from sklearn.cluster import BisectingKMeans

        kmeans = BisectingKMeans(n_clusters=colors, max_iter=100)

        # Resolve palette indexes
        palette_indexes = kmeans.fit_predict(X)

        # Extract the created palette
        palette = (
            np.array(kmeans.cluster_centers_)
            .round()
            .astype(np.uint8)
            .flatten()
            .tolist()
        )

        # Create blank image
        reduced_image = Image.new("P", (w, h))

        # Add palette
        reduced_image.putpalette(palette, rawmode="RGBA" if alpha else "RGB")

        # Paste the pixel data into the image
        reduced_image.putdata(palette_indexes)

        # return the final result
        return reduced_image
