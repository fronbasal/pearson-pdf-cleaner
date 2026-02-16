from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from pathlib import Path

from .core import complete_watermark_removal, detect_processable

LOGGER = logging.getLogger("pearson_pdf_cleaner")


@dataclass(frozen=True)
class CliArgs:
    input_file: Path
    output_file: Path
    verbose: bool
    dry_run: bool
    force: bool


def _parse_args() -> CliArgs:
    parser = argparse.ArgumentParser(
        prog="pearson-pdf-cleaner",
        description="Remove watermarks from PDFs by stripping artifact content blocks.",
    )
    parser.add_argument("input_file", type=Path, help="Input PDF path")
    parser.add_argument("output_file", type=Path, help="Output PDF path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite output file if it exists",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check if the file is processable",
    )

    args = parser.parse_args()
    return CliArgs(
        input_file=args.input_file,
        output_file=args.output_file,
        verbose=args.verbose,
        dry_run=args.dry_run,
        force=args.force,
    )


def main() -> None:
    args = _parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    if not args.verbose:
        logging.getLogger("pypdf").setLevel(logging.ERROR)

    # Check if output file exists
    if args.output_file.exists() and not args.force:
        LOGGER.error(
            "Output file already exists: %s (use -f/--force to overwrite)",
            args.output_file,
        )
        raise SystemExit(1)

    if args.dry_run:
        result = detect_processable(args.input_file)
        if not result.processable:
            LOGGER.error("Not processable: %s", result.reason)
            raise SystemExit(2)

        LOGGER.info("Processable: yes")
        return

    stats = complete_watermark_removal(
        args.input_file,
        args.output_file,
        verbose=args.verbose,
    )
    LOGGER.info("Done: processed %s pages", stats.pages_processed)


if __name__ == "__master__":
    main()
