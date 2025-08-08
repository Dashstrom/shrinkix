"""Module for command line interface."""

import argparse
import logging
import sys
import warnings
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn, TextIO

from .info import __issues__, __project__, __summary__, __version__

LOG_LEVELS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
logger = logging.getLogger(__name__)


def showwarning(  # pragma: no cover
    message: Warning | str,
    category: type[Warning],
    filename: str,
    lineno: int,
    file: TextIO | None = None,  # noqa: ARG001
    line: str | None = None,  # noqa: ARG001
) -> None:
    """Show warning within the logger."""
    for module_name, module in sys.modules.items():  # noqa: B007
        module_path = getattr(module, "__file__", None)
        if module_path and Path(module_path).samefile(filename):
            break
    else:
        module_name = Path(filename).stem
    msg = f"{category.__name__}: {message}"
    logger = logging.getLogger(module_name)
    try:
        _, _, func, info = logger.findCaller()
    except ValueError:  # pragma: no cover
        func, info = "(unknown function)", None
    record = logger.makeRecord(
        logger.name,
        logging.WARNING,
        filename,
        lineno,
        msg,
        (),
        None,
        func,
        None,
        info,
    )
    logger.handle(record)


class HelpArgumentParser(argparse.ArgumentParser):
    """Parser for show usage on error."""

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
        help="Output for all images.",
    )
    parser.add_argument(
        "-i",
        "--inplace",
        action="store_true",
        help="Replace original images.",
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


def setup_logging(*, verbose: bool | None = None) -> None:
    """Do setup logging."""
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.WARNING,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    )
    warnings.showwarning = showwarning


def entrypoint(argv: Sequence[str] | None = None) -> None:
    """Entrypoint for command line interface."""
    try:
        parser = get_parser()
        args = parser.parse_args(argv)
        setup_logging(verbose=args.verbose)
        from .shrinker import Shrinkix  # noqa: PLC0415

        shrinker = Shrinkix(
            max_width=args.max_width,
            max_height=args.max_height,
            keep_metadata=args.keep_metadata,
            experimental_color_reduction=args.experimental_color_reduction,
            copyright=args.copyright,
            artist=args.artist,
            background=args.background,
            quality=args.quality,
        )
        if args.output_dir and args.inplace:
            parser.error(
                '"-o/--output-dir" and "-i/--inplace" are mutually exclusive'
            )
        if not args.output_dir or not args.inplace:
            parser.error(
                "you should provide at least "
                '"-o/--output-dir" or "-i/--inplace"'
            )
        shrinker.bulk(
            args.path,
            output=args.output_dir,
            format=args.format,
            inplace=args.inplace,
            colors=args.colors,
        )
    except Exception as err:  # NoQA: BLE001  # pragma: no cover
        logger.critical(
            "Unexpected error (%s, version %s)",
            __project__,
            __version__,
            exc_info=err,
        )
        logger.critical("Please, report this error to %s.", __issues__)
        sys.exit(1)
