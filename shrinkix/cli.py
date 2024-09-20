"""Module for command line interface."""

import argparse
import logging
import sys
from typing import Optional, Sequence

from .core import __issues__, __summary__, __version__
from .shrinker import Shrinkix

LOG_LEVELS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
logger = logging.getLogger(__name__)


def get_parser() -> argparse.ArgumentParser:
    """Prepare ArgumentParser."""
    parser = argparse.ArgumentParser(
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
        "-r",
        "--fast-color-reduction",
        action="store_true",
        help="Use faster algorithms for color reduction.",
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
        choices=["PNG", "JPG"],
        help="Export format.",
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
        shrinker = Shrinkix(
            max_width=args.max_width,
            max_height=args.max_height,
            keep_metadata=args.keep_metadata,
            fast_color_reduction=args.fast_color_reduction,
            format=args.format,
            copyright=args.copyright,
            artist=args.artist,
        )
        shrinker.bulk(args.path, args.output_dir, colors=args.colors)
    except Exception as err:  # NoQA: BLE001
        logger.critical("Unexpected error", exc_info=err)
        logger.critical("Please, report this error to %s.", __issues__)
        sys.exit(1)
