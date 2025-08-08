"""Module for shrinking and optimizing images.

Provides a class for resizing images, reducing colors, and exporting
them with various options like metadata preservation, format conversion,
and bulk processing.
"""

import logging
import pathlib
from math import floor, sqrt
from time import time
from typing import Any

from PIL import Image
from tqdm import tqdm

from .utils import (
    AllImageSource,
    Formats,
    PathLike,
    PathOrFile,
    open_image,
    ratio,
    size,
    verify_format,
)

MAX_COLORS = 256
MAX_SAMPLE = 100_00

logger = logging.getLogger(__name__)


class Shrinkix:
    """Image shrinker with color reduction and metadata control."""

    def __init__(
        self,
        *,
        keep_metadata: bool | None = None,
        max_width: int | None = None,
        max_height: int | None = None,
        experimental_color_reduction: bool | None = None,
        verbose: bool = False,
        artist: str | None = None,
        copyright: str | None = None,  # noqa: A002
        background: str | None = None,
        quality: int | None = None,
    ) -> None:
        """Initialize the Shrinkix instance with options.

        Args:
            keep_metadata: Whether to preserve image metadata.
            max_width: Maximum allowed width after resizing.
            max_height: Maximum allowed height after resizing.
            experimental_color_reduction: Use exp. color reduction algorithm.
            verbose: Enable verbose logging.
            artist: Artist metadata to embed in the image.
            copyright: Copyright metadata to embed in the image.
            background: Background color to apply behind transparent images.
            quality: Compression quality setting for lossy formats.
        """
        self.keep_metadata = keep_metadata is True
        self.experimental_color_reduction = bool(experimental_color_reduction)
        self.max_width = max_width
        self.max_height = max_height
        self.verbose = verbose
        self.copyright = copyright
        self.artist = artist
        self.background = background
        self.quality = int(quality) if quality is not None else None

    def shrink(  # noqa: C901, PLR0912, PLR0915
        self,
        image: AllImageSource,
        output: PathOrFile,
        format: Formats | None = None,  # noqa: A002
        colors: int | None = None,
    ) -> None:
        """Resize, reduce colors, and save an image to the specified output.

        Args:
            image: Source image path or image object.
            output: Output file path or file-like object.
            format: Output image format (inferred if not specified).
            colors: Number of colors to reduce to (if supported).
        """
        # Get the output format
        if format is None:
            if isinstance(output, (str, pathlib.Path)):
                format = verify_format(pathlib.Path(output).suffix)  # noqa: A001
            elif isinstance(image, (str, pathlib.Path)):
                format = verify_format(pathlib.Path(image).suffix)  # noqa: A001
            else:
                msg = (
                    "Cannot infer the format from the output; "
                    "please specify the format parameter."
                )
                raise ValueError(msg)

        # Load image
        im = open_image(image)

        # Find the best resizing ratio based on max dimensions
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

        # Apply background color if specified (for transparency)
        if self.background is not None:
            new_im = Image.new("RGBA", im.size, self.background)
            new_im.paste(im, (0, 0), im.convert("RGBA"))
            im = new_im.convert("RGB")

        # Remove metadata if not keeping it
        if not self.keep_metadata:
            data = list(im.convert("RGBA").getdata())
            im = Image.new("RGBA", im.size)
            im.putdata(data)

        # Reduce colors if format supports palette
        if format not in ("JPEG", "WEBP"):
            im = self.reduce(im, colors=colors)
        else:
            im = im.convert("RGB") if im.mode != "RGB" else im

        # Prepare save options
        options: dict[str, Any] = {"format": format}

        # Add EXIF metadata if artist or copyright is specified
        import piexif  # noqa: PLC0415

        if self.artist is not None or self.copyright is not None:
            exif_dict: dict[str, Any] = {"0th": {}}
            if self.artist is not None:
                exif_dict["0th"][piexif.ImageIFD.Artist] = self.artist
            if self.copyright is not None:
                exif_dict["0th"][piexif.ImageIFD.Copyright] = self.copyright
            options["exif"] = piexif.dump(exif_dict)

        # Determine quality level if not specified
        if self.quality is None:
            quality = floor(30 + 65 * (1 - min(sqrt(w * h) / 4096, 1)))
            logger.info("Resolved quality is %s", quality)
        else:
            quality = self.quality

        # Set format-specific saving options
        # https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#png
        if format == "PNG":
            options["optimize"] = True
        # https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg
        elif format == "JPEG":
            options["quality"] = quality
        # https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#webp
        elif format == "WEBP":
            options["lossless"] = False
            options["quality"] = quality
            options["alpha_quality"] = quality
            options["method"] = 6

        # Save the image, creating directories if needed
        if isinstance(output, (str, pathlib.PurePath)):
            output_path = pathlib.Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            im.save(output_path, **options)
        else:
            im.save(output, **options)

    def export_name(self, path: pathlib.Path, format: str | None) -> str:  # noqa: A002
        """Generate an output filename with the given format extension.

        Args:
            path: Original file path.
            format: Desired output image format extension.

        Returns:
            Filename with the appropriate extension.
        """
        if format:
            return path.with_suffix(f".{format.lower()}").name
        return path.name

    def bulk(  # noqa: PLR0912
        self,
        files: list[PathLike],
        output: PathLike | None,
        inplace: bool | None = None,  # noqa: FBT001
        format: Formats | None = None,  # noqa: A002
        colors: int | None = None,
    ) -> None:
        """Shrink and export multiple image files, optionally in place.

        Args:
            files: List of file paths or directories to process.
            output: Output directory path (ignored if inplace is True).
            inplace: Whether to overwrite original files.
            format: Desired output image format.
            colors: Number of colors to reduce to.
        """
        if inplace is None:
            inplace = False
        if format:
            format = verify_format(format)  # noqa: A001

        if inplace:
            if output is not None:
                error_message = '"output" and "inplace" are mutually exclusive'
                raise ValueError(error_message)
        elif output is None:
            error_message = 'You should provide at least "output" or "inplace"'
            raise ValueError(error_message)
        else:
            output = pathlib.Path(output)

        paths: dict[pathlib.Path, pathlib.Path] = {}
        for file in files:
            path = pathlib.Path(file)
            if path.is_dir():
                source_paths = list(path.glob("**/*"))
                for sub_path in source_paths:
                    if sub_path.is_file():
                        name = self.export_name(sub_path, format)
                        parent = sub_path.parent if inplace else output
                        paths[sub_path] = parent / name  # type: ignore[operator]
            else:
                name = self.export_name(path, format)
                parent = path.parent if inplace else output
                paths[path] = parent / name  # type: ignore[operator]

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
                if inplace and src.resolve() != dst.resolve():
                    src.unlink(missing_ok=True)

    def reduce(
        self,
        image: AllImageSource,
        colors: int | None = None,
    ) -> Image.Image:
        """Reduce the number of colors in the image to optimize size.

        Uses a palette-based quantization or an experimental clustering
        method if enabled.

        Args:
            image: Image path or image object to reduce colors on.
            colors: Number of colors to reduce to. If None, auto-detected.

        Returns:
            Image with reduced color palette.
        """
        # Open and format image for processing
        im = open_image(image)

        # Skip optimization for certain palette or grayscale modes
        if im.mode in ("L", "LA", "P", "PA"):
            return im

        # Detect if image has alpha channel
        if im.mode == "RGBA":
            alpha = True
        elif im.mode == "RGB":
            alpha = False
        else:
            im = im.convert("RGBA")
            alpha = True

        # Convert image data to numpy array for clustering
        import numpy as np  # noqa: PLC0415

        arr = np.asarray(im)
        h, w = arr.shape[:2]
        X = arr.reshape(-1, 4 if alpha else 3)  # noqa: N806

        # Automatically determine number of colors if not specified
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
            logger.info("Use %s colors", colors)

        if not self.experimental_color_reduction:
            return im.quantize(colors)

        # Use Bisecting K-Means clustering for advanced palette creation
        from sklearn.cluster import BisectingKMeans  # noqa: PLC0415

        kmeans = BisectingKMeans(n_clusters=colors, max_iter=100)

        # Assign palette indexes based on clustering
        palette_indexes = kmeans.fit_predict(X)

        # Extract and format the palette colors
        palette = (
            np.array(kmeans.cluster_centers_)
            .round()
            .astype(np.uint8)
            .flatten()
            .tolist()
        )

        # Create a new palette-based image
        reduced_image = Image.new("P", (w, h))

        # Add the palette to the image
        reduced_image.putpalette(palette, rawmode="RGBA" if alpha else "RGB")

        # Apply the palette indexes as image pixel data
        reduced_image.putdata(palette_indexes)

        return reduced_image
