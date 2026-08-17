"""State and immutable raw-snapshot contracts for pipeline runs."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from .download import DownloadedFile
from .storage import ArtifactStore


class PipelineFailure(RuntimeError):
    """Raised when a required stage cannot safely complete."""


def load_state(store: ArtifactStore) -> dict[str, Any]:
    if not store.exists("state/latest.json"):
        return {}
    return json.loads(store.read_bytes("state/latest.json"))


def same_snapshot(state: dict[str, Any], downloaded: dict[str, DownloadedFile]) -> bool:
    return (
        state.get("xml_sha256") == downloaded["declarations.xml"].sha256
        and state.get("csv_sha256") == downloaded["liste.csv"].sha256
    )


def build_metadata(
    snapshot_date: str, settings: Any, downloaded: dict[str, DownloadedFile]
) -> dict[str, Any]:
    return {
        "snapshot_date": snapshot_date,
        "fetched_at": datetime.now(ZoneInfo("Europe/Paris")).isoformat(),
        "pipeline_git_sha": settings.pipeline_git_sha,
        "pipeline_version": settings.pipeline_version,
        "files": [
            {
                "name": item.name,
                "url": item.url,
                "size_bytes": item.size_bytes,
                "sha256": item.sha256,
                "elapsed_seconds": round(item.elapsed_seconds, 3),
            }
            for item in downloaded.values()
        ],
    }


def reuse_snapshot_metadata(
    store: ArtifactStore, snapshot_date: str, metadata: dict[str, Any], dry_run: bool
) -> dict[str, Any]:
    path = f"raw/snapshot_date={snapshot_date}/metadata.json"
    if dry_run or not store.exists(path):
        return metadata
    existing = json.loads(store.read_bytes(path))
    old = {item.get("name"): item.get("sha256") for item in existing.get("files", [])}
    new = {item.get("name"): item.get("sha256") for item in metadata.get("files", [])}
    if old == new:
        return existing
    raise PipelineFailure(
        f"Immutable raw snapshot {snapshot_date} already exists with different source hashes"
    )


def write_state(store: ArtifactStore, state: dict[str, Any]) -> None:
    store.put_bytes(
        "state/latest.json",
        (json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(),
        content_type="application/json",
    )
