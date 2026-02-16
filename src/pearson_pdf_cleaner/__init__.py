"""Pearson PDF cleaner package."""

from .core import (
    DetectionResult,
    RemovalStats,
    complete_watermark_removal,
    detect_processable,
)

__all__ = [
    "DetectionResult",
    "RemovalStats",
    "complete_watermark_removal",
    "detect_processable",
]
