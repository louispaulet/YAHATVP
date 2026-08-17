"""CLI façade for source-linked HATVP quality review artifacts."""

from __future__ import annotations

import argparse
import io
import json
import tempfile
from pathlib import Path
from typing import Any

import polars as pl

from .hashing import sha256_bytes
from .parser import parse_xml
from .storage import GCSArtifactStore, LocalArtifactStore
from .triage_fingerprints import declaration_xml_fingerprints
from .triage_register import build_review_register
from .triage_report import render_markdown, write_review_artifacts

SNAPSHOT_DATE = "2026-08-16"
TABLES_FOR_SOURCE_REVIEW = ("declarations", "people", "assets")


def build_snapshot_review(
    store: Any, snapshot_date: str = SNAPSHOT_DATE, source_uri_prefix: str | None = None
) -> dict[str, Any]:
    prefix = getattr(store, "prefix", "").strip("/")
    uri = source_uri_prefix or (
        f"gs://{store.bucket.name}/{prefix}"
        if isinstance(store, GCSArtifactStore)
        else f"local://{store.root}/{prefix}"
    )
    paths = {
        "raw_xml": f"raw/snapshot_date={snapshot_date}/declarations.xml",
        "raw_csv": f"raw/snapshot_date={snapshot_date}/liste.csv",
        "metadata": f"raw/snapshot_date={snapshot_date}/metadata.json",
        "quality": f"quality/snapshot_date={snapshot_date}/report.json",
        "quarantine": f"quarantine/snapshot_date={snapshot_date}/anomalies.parquet",
    }
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


def _uri(prefix: str, path: str) -> str:
    return f"{prefix.rstrip('/')}/{path.lstrip('/')}"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--bucket")
    source.add_argument("--local-root", type=Path)
    parser.add_argument("--prefix", default="hatvp")
    parser.add_argument("--snapshot-date", default=SNAPSHOT_DATE)
    parser.add_argument("--source-uri-prefix")
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    store = (
        GCSArtifactStore(args.bucket, args.prefix)
        if args.bucket
        else LocalArtifactStore(args.local_root, args.prefix)
    )
    review = build_snapshot_review(store, args.snapshot_date, args.source_uri_prefix)
    json_path, markdown_path = write_review_artifacts(review, args.output_dir)
    print(f"wrote {json_path}")
    print(f"wrote {markdown_path}")
    return 0


__all__ = [
    "build_review_register",
    "build_snapshot_review",
    "declaration_xml_fingerprints",
    "main",
    "render_markdown",
    "write_review_artifacts",
]


if __name__ == "__main__":
    raise SystemExit(main())
