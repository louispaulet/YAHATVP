"""Stable paths and state helpers for independently ingested sources."""

from __future__ import annotations

import json
from typing import Any

from ..download import DownloadedFile
from ..storage import ArtifactStore

OFFICIAL_SOURCE = "hatvp_website"


def source_raw_prefix(source_id: str) -> str:
    """Keep the historic official path while isolating backup sources."""

    return "" if source_id == OFFICIAL_SOURCE else f"source={source_id}/"


def raw_snapshot_path(source_id: str, snapshot: str, name: str) -> str:
    """Build one immutable raw-object path for a source snapshot."""

    return f"raw/{source_raw_prefix(source_id)}snapshot_date={snapshot}/{name}"


def raw_metadata_path(source_id: str, snapshot: str) -> str:
    """Build the metadata path paired with one raw source snapshot."""

    return raw_snapshot_path(source_id, snapshot, "metadata.json")


def source_state_path(source_id: str) -> str:
    """Return the latest raw-ingestion state path for one source."""

    return f"state/sources/{source_id}/latest.json"


def load_source_state(store: ArtifactStore, source_id: str) -> dict[str, Any]:
    """Read source state, falling back to the legacy official state."""

    path = source_state_path(source_id)
    if store.exists(path):
        return json.loads(store.read_bytes(path))
    if source_id == OFFICIAL_SOURCE and store.exists("state/latest.json"):
        return json.loads(store.read_bytes("state/latest.json"))
    return {}


def write_source_state(store: ArtifactStore, source_id: str, state: dict[str, Any]) -> None:
    """Record raw-ingestion completion without advancing processed state."""

    write_state_at(store, source_state_path(source_id), state)


def write_state_at(store: ArtifactStore, path: str, state: dict[str, Any]) -> None:
    """Write a JSON state object to a validated logical path."""

    store.put_bytes(
        path,
        (json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(),
        content_type="application/json",
    )


def build_source_state(
    metadata: dict[str, Any], downloaded: dict[str, DownloadedFile], archive_hash: str | None = None
) -> dict[str, Any]:
    """Build the raw-ingestion hash record used by source-aware cascades."""

    result = {
        "source_id": metadata["ingestion_source"],
        "snapshot_date": metadata["snapshot_date"],
        "fetched_at": metadata["fetched_at"],
        "xml_sha256": downloaded["declarations.xml"].sha256,
        "files": {name: item.sha256 for name, item in downloaded.items()},
    }
    result.update(
        {"csv_sha256": downloaded["liste.csv"].sha256} if "liste.csv" in downloaded else {}
    )
    result.update({"archive_sha256": archive_hash} if archive_hash else {})
    return result


def source_ids(store: ArtifactStore) -> tuple[str, ...]:
    """Discover ingested sources while retaining legacy official deployments."""

    found: set[str] = set()
    if any(
        path.startswith("raw/snapshot_date=") for path in store.list_paths("raw/")
    ) or store.exists("state/latest.json"):
        found.add(OFFICIAL_SOURCE)
    for path in store.list_paths("state/sources/"):
        parts = path.split("/")
        if len(parts) >= 4 and parts[-1] == "latest.json":
            found.add(parts[2])
    return tuple(sorted(found))
