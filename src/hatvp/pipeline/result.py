"""Completion status and structured logging for pipeline runs."""

from __future__ import annotations

import logging
import time

from ..quality import QualityResult

logger = logging.getLogger("hatvp")


def result_status(quality: QualityResult) -> str:
    """Map quality warnings to the stable pipeline status vocabulary."""

    return "SUCCESS_WITH_WARNINGS" if quality.has_warnings else "SUCCESS"


def finish_run(snapshot: str, started: float, quality: QualityResult) -> str:
    """Log and return the terminal status after state advancement."""

    status = result_status(quality)
    logger.info(
        "pipeline_complete",
        extra={
            "event": "pipeline_complete",
            "status": status,
            "snapshot_date": snapshot,
            "elapsed_seconds": round(time.perf_counter() - started, 3),
        },
    )
    return status


def elapsed_seconds(started: float) -> float:
    """Expose monotonic elapsed time for diagnostics and focused tests."""

    return round(time.perf_counter() - started, 3)


def status_event(status: str, snapshot: str) -> dict[str, str]:
    """Build the compact completion payload used by log assertions."""

    return {"event": "pipeline_complete", "status": status, "snapshot_date": snapshot}


def is_success(status: str) -> bool:
    """Return whether the terminal status permits state advancement."""

    return status in {"SUCCESS", "SUCCESS_WITH_WARNINGS"}


def no_change_event() -> dict[str, str]:
    """Return the stable event for a hash-equivalent invocation."""

    return {"event": "pipeline_complete", "status": "NO_CHANGE"}


def log_no_change() -> None:
    """Emit the completion event for a hash-equivalent invocation."""

    logger.info("pipeline_complete", extra=no_change_event())


__all__ = [
    "elapsed_seconds",
    "finish_run",
    "is_success",
    "log_no_change",
    "no_change_event",
    "result_status",
    "status_event",
]
