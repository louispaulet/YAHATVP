"""Successful-run state advancement kept separate from transformation logic."""

from __future__ import annotations

from typing import Any

from ..config import Settings
from ..download import DownloadedFile
from ..storage import ArtifactStore
from .state import write_state


def write_success_state(
    store: ArtifactStore,
    snapshot: str,
    metadata: dict[str, Any],
    downloaded: dict[str, DownloadedFile],
    settings: Settings,
) -> None:
    """Advance latest.json only after every layer and load stage succeeds."""

    write_state(
        store,
        {
            "snapshot_date": snapshot,
            "fetched_at": metadata["fetched_at"],
            "xml_sha256": downloaded["declarations.xml"].sha256,
            "csv_sha256": downloaded["liste.csv"].sha256,
            "pipeline_git_sha": settings.pipeline_git_sha,
            "pipeline_version": settings.pipeline_version,
        },
    )


def state_fields() -> tuple[str, ...]:
    """Return fields used in the latest-state contract."""

    return (
        "snapshot_date",
        "fetched_at",
        "xml_sha256",
        "csv_sha256",
        "pipeline_git_sha",
        "pipeline_version",
    )


def state_advancement_gate() -> str:
    """Describe the required ordering for operational documentation."""

    return "raw -> parse -> quality -> parquet -> BigQuery -> latest.json"


def has_downloads(downloaded: dict[str, DownloadedFile]) -> bool:
    """Return whether both exact-byte source downloads are present."""

    return all(name in downloaded for name in ("declarations.xml", "liste.csv"))


def state_snapshot(
    metadata: dict[str, Any], downloaded: dict[str, DownloadedFile]
) -> dict[str, Any]:
    """Build the immutable source-hash portion used by state tests."""

    return {
        "fetched_at": metadata["fetched_at"],
        "xml_sha256": downloaded["declarations.xml"].sha256,
        "csv_sha256": downloaded["liste.csv"].sha256,
    }


def is_success_status(status: str) -> bool:
    """Return whether a warning-bearing run may advance latest state."""

    return status in {"SUCCESS", "SUCCESS_WITH_WARNINGS"}


__all__ = ["has_downloads", "state_advancement_gate", "state_fields", "write_success_state"]
