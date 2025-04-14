"""Module for command line interface."""

import argparse
import logging
import sys
from collections.abc import Sequence
from typing import NoReturn, Optional

from .info import __issues__, __summary__, __version__

LOG_LEVELS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
logger = logging.getLogger(__name__)


class HelpArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:  # pragma: no cover
        """Handle error from argparse.ArgumentParser."""
        self.print_help(sys.stderr)
        self.exit(2, f"{self.prog}: error: {message}\n")


def get_parser() -> argparse.ArgumentParser:
    """Prepare ArgumentParser."""
    parser = HelpArgumentParser(
        prog="shrinkix",
        description=__summary__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s, version {__version__}",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="verbose mode, enable INFO and DEBUG messages.",
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "-k",
        "--keep-metadata",
        action="store_true",
        help="Keep metadata.",
    )
    parser.add_argument(
        "--max-height",
        type=int,
        help="Maximal height of image.",
    )
    parser.add_argument(
        "--max-width",
        type=int,
        help="Maximal width of image.",
    )
    parser.add_argument(
        "path",
        nargs="+",
        help="Path to images or directories.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="shrunk",
        help="Output for all images.",
    )
    parser.add_argument(
        "-e",
        "--experimental-color-reduction",
        action="store_true",
        help="Use experimental color reduction algorithm.",
    )
    parser.add_argument(
        "-c",
        "--colors",
        type=int,
        required=False,
        help="Colors t use in color reduction.",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["PNG", "JPEG", "WEBP"],
        help="Export format.",
    )
    parser.add_argument(
        "-b",
        "--background",
        help="Replace transparency with this color.",
    )
    parser.add_argument(
        "-q",
        "--quality",
        help="Image quality (JPEG).",
        type=int,
    )
    parser.add_argument(
        "--copyright",
        help="Copyright to add in exif metadata.",
    )
    parser.add_argument(
        "--artist",
        help="Artist to add in exif metadata.",
    )
    return parser


def setup_logging(verbose: Optional[bool] = None) -> None:
    """Do setup logging."""
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.WARNING,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    )


def entrypoint(argv: Optional[Sequence[str]] = None) -> None:
    """Entrypoint for command line interface."""
    try:
        parser = get_parser()
        args = parser.parse_args(argv)
        setup_logging(args.verbose)
        from .shrinker import Shrinkix

        shrinker = Shrinkix(
            max_width=args.max_width,
            max_height=args.max_height,
            keep_metadata=args.keep_metadata,
            experimental_color_reduction=args.experimental_color_reduction,
            format=args.format,
            copyright=args.copyright,
            artist=args.artist,
            background=args.background,
            quality=args.quality,
        )
        shrinker.bulk(args.path, args.output_dir, colors=args.colors)
    except Exception as err:  # NoQA: BLE001   # pragma: no cover
        logger.critical("Unexpected error", exc_info=err)
        logger.critical("Please, report this error to %s.", __issues__)
        sys.exit(1)
