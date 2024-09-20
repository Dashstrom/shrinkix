"""Module for shrink images."""

import pathlib
from math import floor, sqrt
from time import time
from typing import Any, Dict, List, Literal, Optional

from PIL import Image
from tqdm import tqdm

from .utils import AllImageSource, PathLike, PathOrFile, open_image, ratio

MAX_COLORS = 256
MAX_SAMPLE = 100_00


class Shrinkix:
    def __init__(  # noqa: PLR0913
        self,
        *,
        format: Optional[Literal["PNG", "JPG"]] = None,  # noqa: A002
        keep_metadata: Optional[bool] = None,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        fast_color_reduction: Optional[bool] = None,
        verbose: bool = False,
        artist: Optional[str] = None,
        copyright: Optional[str] = None,  # noqa: A002
    ) -> None:
        """Instantiate Shrinkix."""
        self.keep_metadata = keep_metadata is True
        self.fast_color_reduction = fast_color_reduction is True
        self.max_width = max_width
        self.max_height = max_height
        self.verbose = verbose
        self.copyright = copyright
        self.artist = artist
        if format is None:
            self.format = "PNG"
        else:
            self.format = format

    def shrink(
        self,
        image: AllImageSource,
        output: PathOrFile,
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

        # Remove metadata
        if not self.keep_metadata:
            data = list(im.convert("RGBA").getdata())
            im = Image.new("RGBA", im.size)
            im.putdata(data)

        # Reduce colors
        im = self.reduce(im)
        options: Dict[str, Any] = {"format": self.format}

        # Add exif information
        import piexif

        if self.artist is not None or self.copyright is not None:
            exif_dict: Dict[str, Any] = {"0th": {}}
            if self.artist is not None:
                exif_dict["0th"][piexif.ImageIFD.Artist] = self.artist
            if self.copyright is not None:
                exif_dict["0th"][piexif.ImageIFD.Copyright] = self.copyright
            options["exif"] = piexif.dump(exif_dict)

        # Save with optimization
        if self.format == "PNG":
            options["optimize"] = True
        elif self.format == "JPG":
            quality = floor(30 + 65 * (1 - min(sqrt(w * h) / 4096, 1)))
            options["quality"] = quality
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
        files: List[PathLike],
        output: PathLike,
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
                bar.write(f"Processing {src}")
                start = time()
                self.shrink(src, dst)
                end = time()
                elapsed = end - start
                bar.write(
                    f"Export at {dst}, "
                    f"ratio: {ratio(src, dst):.2%}, time: {elapsed:.3f}s",
                )

    def reduce(
        self,
        image: AllImageSource,
        colors: Optional[int] = None,
    ) -> Image.Image:
        """Reduce image colors."""
        # Open and format for model
        im = open_image(image)

        # Palette is not supported on JPG
        if self.format == "JPG":
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
            blocks, block_counts = np.unique(
                sample // 16,
                axis=0,
                return_counts=True,
            )
            colors = len(block_counts)
            if colors > MAX_COLORS:
                colors = MAX_COLORS

        if self.fast_color_reduction:
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
