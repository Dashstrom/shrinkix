"""Module for shrink images."""

import pathlib
from math import floor
from typing import IO, List, Optional, Union, overload

from PIL import Image

PathLike = Union[str, pathlib.Path]
PathOrFile = Union[PathLike, IO[bytes]]
PathOrFileOrImage = Union[PathOrFile, Image.Image]


class Shrinkix:
    def __init__(
        self,
        *,
        keep_metadata: Optional[bool] = None,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
    ) -> None:
        """Instantiate Shrinkix."""
        self.keep_metadata = keep_metadata is True
        self.max_width = max_width
        self.max_height = max_height

    @overload
    def shrink(
        self,
        file: PathOrFileOrImage,
        output: PathOrFile,
    ) -> None:
        pass

    @overload
    def shrink(
        self,
        file: IO[bytes],
        output: None = None,
    ) -> Image.Image:
        pass

    def shrink(
        self,
        file: PathOrFileOrImage,
        output: Optional[PathOrFile] = None,
    ) -> Optional[Image.Image]:
        """Shrink an image."""
        # Load image
        if isinstance(file, (str, pathlib.PurePath)):
            path = pathlib.Path(file)
            im = Image.open(path.open("rb"))
        elif isinstance(file, Image.Image):
            im = file
        else:
            im = Image.open(file)

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
            data = list(im.getdata())
            im = Image.new(im.mode, im.size)
            im.putdata(data)  # type: ignore[no-untyped-call]

        # Reduce colors
        im = im.convert("P", palette=Image.Palette.ADAPTIVE, colors=256)

        # Save with optimization
        if output is not None:
            if isinstance(output, (str, pathlib.PurePath)):
                output_path = pathlib.Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                im.save(output_path, optimize=True)
            else:
                im.save(output, optimize=True, format="PNG")
            return None
        return im

    def bulk(
        self,
        files: List[PathLike],
        output: PathLike,
    ) -> None:
        """Shrink a list of file and export it in output."""
        root = pathlib.Path(output).resolve()
        paths = {}
        for file in files:
            path = pathlib.Path(file)
            if path.is_dir():
                for sub_path in path.glob("**/*"):
                    if sub_path.is_file():
                        output_path = root / sub_path.with_suffix(".png").name
                        paths[sub_path] = output_path
            else:
                output_path = root / path.with_suffix(".png").name
                paths[path] = output_path

        for src, dst in paths.items():
            self.shrink(src, dst)
