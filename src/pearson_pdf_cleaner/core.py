from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
import re
from typing import Any, cast

import pikepdf
from pypdf import PdfReader

LOGGER = logging.getLogger("pearson_pdf_cleaner")

# Pre-compiled regex pattern for watermark removal (avoid recompilation in hot loop)
# Match /Artifact blocks specifically - will be filtered by content
ARTIFACT_PATTERN = re.compile(rb"/Artifact\s+(?:BMC|BDC).*?EMC\s*", re.DOTALL)


@dataclass(frozen=True)
class RemovalStats:
    pages_processed: int


@dataclass(frozen=True)
class DetectionResult:
    processable: bool
    reason: str | None


def detect_processable(input_pdf: str | Path) -> DetectionResult:
    try:
        reader = PdfReader(str(input_pdf))
    except Exception as exc:
        return DetectionResult(
            processable=False,
            reason=f"{exc.__class__.__name__}: {exc}",
        )

    if reader.is_encrypted:
        try:
            if reader.decrypt("") == 0:
                return DetectionResult(
                    processable=False,
                    reason="PDF is encrypted",
                )
        except Exception as exc:
            return DetectionResult(
                processable=False,
                reason=f"{exc.__class__.__name__}: {exc}",
            )

    return DetectionResult(
        processable=True,
        reason=None,
    )


def complete_watermark_removal(
    input_pdf: str | Path,
    output_pdf: str | Path,
    *,
    verbose: bool = False,
) -> RemovalStats:
    """Remove watermark elements from a PDF by removing /Artifact marked content blocks."""
    input_path = str(input_pdf)

    # Extract metadata from ORIGINAL PDF before any processing
    original_reader = PdfReader(input_path)
    original_metadata = _extract_clean_metadata(original_reader)

    try:
        # Use pikepdf to open and process the PDF
        pdf = pikepdf.open(input_path)

        # Process each page
        for page_num, page in enumerate(pdf.pages, start=1):
            # Process content streams to remove artifact watermarks
            contents = page.get("/Contents")
            if contents is not None:
                # Handle both single stream and array of streams
                if isinstance(contents, (pikepdf.Array, list)):
                    streams = cast(list[Any], contents)
                else:
                    streams = [contents]

                for stream_ref in streams:
                    try:
                        if hasattr(stream_ref, "read_bytes"):
                            data = stream_ref.read_bytes()
                        else:
                            continue

                        # Remove marked content blocks (Pearson watermarks use /Artifact markers)
                        # These are non-content elements like watermarks, headers, footers
                        modified = False

                        # Use pre-compiled pattern for efficiency
                        data_after_artifact = ARTIFACT_PATTERN.sub(b"", data)
                        if data_after_artifact != data:
                            data = data_after_artifact
                            modified = True

                        if modified:
                            stream_ref.write(data)
                    except Exception:
                        if verbose:
                            LOGGER.debug(
                                "Could not process stream on page %s", page_num
                            )

            if verbose and page_num % 200 == 0:
                LOGGER.debug("Processed %s pages", page_num)

        # Update metadata before saving
        output_path = Path(output_pdf)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Sanitize docinfo metadata (remove producer, keep only safe fields)
        try:
            docinfo = cast(dict[str, Any], pdf.docinfo)
            # Set producer to empty (remove tracking)
            docinfo["/Producer"] = ""
            # Remove other identifying fields
            for key in ("/Creator", "/CreationDate", "/ModDate"):
                if key in docinfo:
                    del docinfo[key]
        except Exception as exc:
            if verbose:
                LOGGER.debug("Could not sanitize docinfo metadata: %s", exc)

        # Save final output with compression
        pdf.save(str(output_path), compress_streams=True)
        pdf.close()

        if verbose:
            LOGGER.debug("Watermark removal complete")

        return RemovalStats(pages_processed=len(pdf.pages))

    except Exception as exc:
        if verbose:
            LOGGER.debug("Error during watermark removal: %s", exc)
            import traceback

            traceback.print_exc()
        raise


def _extract_clean_metadata(reader: PdfReader) -> dict[str, str]:
    """Extract clean metadata from PDF, filtering for allowed keys."""
    allowed_info_keys: set[str] = {"/Author", "/Title", "/Subject", "/Keywords"}
    filtered_metadata: dict[str, str] = {}

    try:
        info: dict[str, Any] = reader.metadata or {}
        for key, value in info.items():
            if key in allowed_info_keys and isinstance(value, str):
                filtered_metadata[key] = value
    except Exception:
        pass

    return filtered_metadata
