"""Read-only assembly of source-linked triage evidence from artifacts."""

from __future__ import annotations

import io
import json
import tempfile
from pathlib import Path
from typing import Any

import polars as pl

from ..hashing import sha256_bytes
from ..parser import parse_xml
from ..storage import GCSArtifactStore
from .fingerprints import declaration_xml_fingerprints
from .register import build_review_register

TABLES_FOR_SOURCE_REVIEW = ("declarations", "people", "assets")


def build_snapshot_review(
    store: Any, snapshot_date: str, source_uri_prefix: str | None = None
) -> dict[str, Any]:
    prefix = getattr(store, "prefix", "").strip("/")
    uri = source_uri_prefix or (
        f"gs://{store.bucket.name}/{prefix}"
        if isinstance(store, GCSArtifactStore)
        else f"local://{store.root}/{prefix}"
    )
    paths = _paths(snapshot_date)
    raw_xml = store.read_bytes(paths["raw_xml"])
    metadata = json.loads(store.read_bytes(paths["metadata"]))
    quality = json.loads(store.read_bytes(paths["quality"]))
    anomalies = pl.read_parquet(io.BytesIO(store.read_bytes(paths["quarantine"]))).to_dicts()
    persisted = {
        name: pl.read_parquet(
            io.BytesIO(
                store.read_bytes(f"silver/{name}/snapshot_date={snapshot_date}/data.parquet")
            )
        ).to_dicts()
        for name in TABLES_FOR_SOURCE_REVIEW
    }
    with tempfile.NamedTemporaryFile(suffix=".xml") as source:
        source.write(raw_xml)
        source.flush()
        source_tables = parse_xml(Path(source.name), snapshot_date)
        fingerprints = declaration_xml_fingerprints(Path(source.name))
    files = {item["name"]: item for item in metadata.get("files", []) if item.get("name")}
    evidence = {
        "snapshot_date": snapshot_date,
        "quality_report_uri": _uri(uri, paths["quality"]),
        "quarantine_uri": _uri(uri, paths["quarantine"]),
        "raw_xml_uri": _uri(uri, paths["raw_xml"]),
        "raw_csv_uri": _uri(uri, paths["raw_csv"]),
        "metadata_uri": _uri(uri, paths["metadata"]),
        "state_uri": _uri(uri, "state/latest.json"),
        "raw_xml_sha256": files.get("declarations.xml", {}).get("sha256") or sha256_bytes(raw_xml),
        "raw_csv_sha256": files.get("liste.csv", {}).get("sha256"),
        "pipeline_git_sha": metadata.get("pipeline_git_sha"),
        "pipeline_version": metadata.get("pipeline_version"),
        "quality_report_sha256": sha256_bytes(store.read_bytes(paths["quality"])),
        "quarantine_sha256": sha256_bytes(store.read_bytes(paths["quarantine"])),
        "silver_sha256": {},
        "quality_report": quality,
    }
    return build_review_register(
        anomalies=anomalies,
        source_tables=source_tables,
        persisted_tables=persisted,
        fingerprints=fingerprints,
        evidence=evidence,
    )


def _paths(snapshot: str) -> dict[str, str]:
    return {
        "raw_xml": f"raw/snapshot_date={snapshot}/declarations.xml",
        "raw_csv": f"raw/snapshot_date={snapshot}/liste.csv",
        "metadata": f"raw/snapshot_date={snapshot}/metadata.json",
        "quality": f"quality/snapshot_date={snapshot}/report.json",
        "quarantine": f"quarantine/snapshot_date={snapshot}/anomalies.parquet",
    }


def _uri(prefix: str, path: str) -> str:
    return f"{prefix.rstrip('/')}/{path.lstrip('/')}"


__all__ = ["TABLES_FOR_SOURCE_REVIEW", "build_snapshot_review"]
