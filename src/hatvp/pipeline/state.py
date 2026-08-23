"""State and immutable raw-snapshot contracts for pipeline runs."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from ..download import DownloadedFile
from ..storage import ArtifactStore
from .source_contract import OFFICIAL_SOURCE, raw_metadata_path, raw_snapshot_path


class PipelineFailure(RuntimeError):
    """Raised when a required stage cannot safely complete."""


def load_state(store: ArtifactStore) -> dict[str, Any]:
    if not store.exists("state/latest.json"):
        return {}
    return json.loads(store.read_bytes("state/latest.json"))


def build_metadata(
    snapshot_date: str,
    settings: Any,
    downloaded: dict[str, DownloadedFile],
    source_id: str = OFFICIAL_SOURCE,
) -> dict[str, Any]:
    files = [
        {
            "name": item.name,
            "url": item.url,
            "size_bytes": item.size_bytes,
            "sha256": item.sha256,
            "elapsed_seconds": round(item.elapsed_seconds, 3),
        }
        for item in downloaded.values()
    ]
    return {
        "snapshot_date": snapshot_date,
        "fetched_at": datetime.now(ZoneInfo("Europe/Paris")).isoformat(),
        "pipeline_git_sha": settings.pipeline_git_sha,
        "pipeline_version": settings.pipeline_version,
        "ingestion_source": source_id,
        "files": files,
        "source_metadata": bronze_source_metadata(settings, snapshot_date, downloaded, source_id),
    }


def bronze_source_metadata(
    settings: Any,
    snapshot_date: str,
    downloaded: dict[str, DownloadedFile],
    source_id: str = OFFICIAL_SOURCE,
) -> dict[str, dict[str, Any]]:
    def object_uri(name: str) -> str:
        path = f"{settings.hatvp_prefix}/{raw_snapshot_path(source_id, snapshot_date, name)}"
        return f"gs://{settings.hatvp_bucket}/{path}" if settings.hatvp_bucket else path

    return {
        name: {
            "url": source.url,
            "sha256": source.sha256,
            "source_object": object_uri(name),
            "pipeline_version": settings.pipeline_version,
            "ingestion_source": source_id,
            "source_snapshot_date": snapshot_date,
        }
        for name, source in downloaded.items()
    }


def reuse_snapshot_metadata(
    store: ArtifactStore,
    snapshot_date: str,
    metadata: dict[str, Any],
    dry_run: bool,
    source_id: str = OFFICIAL_SOURCE,
) -> dict[str, Any]:
    path = raw_metadata_path(source_id, snapshot_date)
    if dry_run or not store.exists(path):
        return metadata
    existing = json.loads(store.read_bytes(path))
    old = {item.get("name"): item.get("sha256") for item in existing.get("files", [])}
    new = {item.get("name"): item.get("sha256") for item in metadata.get("files", [])}
    if old == new:
        existing.setdefault("source_metadata", metadata.get("source_metadata", {}))
        return existing
    raise PipelineFailure(
        f"Immutable raw snapshot {snapshot_date} already exists with different source hashes"
    )


def write_state(store: ArtifactStore, state: dict[str, Any]) -> None:
    payload = (json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    store.put_bytes("state/latest.json", payload, content_type="application/json")
