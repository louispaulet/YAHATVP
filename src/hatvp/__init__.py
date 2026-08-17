"""Yet Another HATVP Project: a small auditable ingestion pipeline.

The package deliberately exposes only stable boundary types here.  Source
parsers, quality checks, storage adapters, and pipeline stages remain separate
modules so the command-line entrypoint can compose them without an external
orchestrator.

Raw source bytes are immutable, normalized rows retain provenance, and the
latest-state marker is written only after every required output succeeds.
Suspicious but plausible values are retained and flagged for review.
"""

from .models import PipelineStatus, Row, TableRows, TableSet

__title__ = "hatvp-pipeline"
__version__ = "0.1.0"
__description__ = "Small, auditable weekly pipeline for HATVP open data"
__source_repository__ = "https://github.com/louispaulet/YAHATVP"

SUPPORTED_STATUSES: tuple[PipelineStatus, ...] = (
    "NO_CHANGE",
    "SUCCESS",
    "SUCCESS_WITH_WARNINGS",
    "FAILED",
)


def package_metadata() -> dict[str, str]:
    """Return non-secret package metadata for diagnostics and logs."""

    return {
        "name": __title__,
        "version": __version__,
        "description": __description__,
        "repository": __source_repository__,
    }


def is_terminal_status(status: str) -> bool:
    """Return whether a pipeline status represents a completed invocation."""

    return status in SUPPORTED_STATUSES


__all__ = [
    "PipelineStatus",
    "Row",
    "SUPPORTED_STATUSES",
    "TableRows",
    "TableSet",
    "__description__",
    "__source_repository__",
    "__title__",
    "__version__",
    "is_terminal_status",
    "package_metadata",
]
