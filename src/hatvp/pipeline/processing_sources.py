"""Materialize the latest raw snapshot of each source for processing."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..config import Settings
from ..storage import ArtifactStore
from .source_contract import (
    load_source_state,
    raw_metadata_path,
    raw_snapshot_path,
    source_ids,
)


@dataclass(frozen=True)
class RawSource:
    source_id: str
    snapshot: str
    xml: Path
    csv: Path
    metadata: dict[str, Any]


def materialize_sources(
    store: ArtifactStore, settings: Settings, directory: Path
) -> list[RawSource]:
    sources: list[RawSource] = []
    for source_id in source_ids(store):
        state = load_source_state(store, source_id)
        snapshot = str(state.get("snapshot_date") or "")
        if not snapshot:
            continue
        metadata = _metadata(store, settings, source_id, snapshot, state)
        folder = directory / source_id
        folder.mkdir(parents=True, exist_ok=True)
        xml_key = raw_snapshot_path(source_id, snapshot, "declarations.xml")
        if not store.exists(xml_key):
            raise ValueError(f"Raw source object is missing: {xml_key}")
        xml = folder / "declarations.xml"
        xml.write_bytes(store.read_bytes(xml_key))
        csv = folder / "liste.csv"
        csv_key = raw_snapshot_path(source_id, snapshot, "liste.csv")
        if store.exists(csv_key):
            csv.write_bytes(store.read_bytes(csv_key))
        else:
            csv.write_text("id_origine;url_dossier\n", encoding="utf-8")
        sources.append(RawSource(source_id, snapshot, xml, csv, metadata))
    if not sources:
        raise ValueError("No ingested raw source is available for processing")
    return sources


def _metadata(
    store: ArtifactStore,
    settings: Settings,
    source_id: str,
    snapshot: str,
    state: dict[str, Any],
) -> dict[str, Any]:
    path = raw_metadata_path(source_id, snapshot)
    value = (
        json.loads(store.read_bytes(path))
        if store.exists(path)
        else {"snapshot_date": snapshot, "files": []}
    )
    value.setdefault("ingestion_source", source_id)
    value.setdefault("pipeline_version", settings.pipeline_version)
    value.setdefault("source_metadata", _legacy_metadata(settings, source_id, snapshot, state))
    for item in value["source_metadata"].values():
        item.setdefault("ingestion_source", source_id)
        item.setdefault("source_snapshot_date", snapshot)
    return value


def _legacy_metadata(
    settings: Settings, source_id: str, snapshot: str, state: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    return {
        "declarations.xml": {
            "url": settings.hatvp_xml_url,
            "sha256": state.get("xml_sha256"),
            "ingestion_source": source_id,
            "source_object": raw_snapshot_path(source_id, snapshot, "declarations.xml"),
            "pipeline_version": settings.pipeline_version,
        },
        "liste.csv": {
            "url": settings.hatvp_csv_url,
            "sha256": state.get("csv_sha256"),
            "ingestion_source": source_id,
            "source_object": raw_snapshot_path(source_id, snapshot, "liste.csv"),
            "pipeline_version": settings.pipeline_version,
        },
    }
