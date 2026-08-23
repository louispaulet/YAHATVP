"""Raw, quality, quarantine, and normalized-table artifact writers."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from ..download import DownloadedFile
from ..quality import QualityResult
from ..storage import ArtifactStore
from ..tables import write_parquet, write_table
from .source_contract import OFFICIAL_SOURCE, source_raw_prefix


def archive_raw(
    store: ArtifactStore,
    snapshot_date: str,
    downloaded: dict[str, DownloadedFile],
    metadata: dict[str, Any],
    dry_run: bool,
    source_id: str = OFFICIAL_SOURCE,
) -> None:
    if dry_run:
        return
    for name, source in downloaded.items():
        store.put_file(
            f"raw/{source_raw_prefix(source_id)}snapshot_date={snapshot_date}/{name}",
            source.path,
            content_type=_content_type(name),
            immutable=True,
        )
    store.put_bytes(
        f"raw/{source_raw_prefix(source_id)}snapshot_date={snapshot_date}/metadata.json",
        _json(metadata),
        content_type="application/json",
        immutable=True,
    )


def write_report(
    store: ArtifactStore, snapshot_date: str, quality: QualityResult, dry_run: bool
) -> None:
    if dry_run:
        return
    store.put_bytes(
        f"quality/snapshot_date={snapshot_date}/report.json",
        _json(quality.report),
        content_type="application/json",
    )
    if not quality.anomalies:
        return
    temporary = Path(tempfile.mkstemp(suffix=".parquet")[1])
    try:
        write_parquet(
            quality.anomalies, temporary, ["table_name", "quality_status", "quality_reason"]
        )
        store.put_file(
            f"quarantine/snapshot_date={snapshot_date}/anomalies.parquet",
            temporary,
            content_type="application/vnd.apache.parquet",
        )
    finally:
        temporary.unlink(missing_ok=True)


def write_tables(
    store: ArtifactStore,
    tables: dict[str, list[dict[str, Any]]],
    snapshot_date: str,
    working_dir: Path,
    dry_run: bool,
) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for name, rows in tables.items():
        output = working_dir / f"{name}.parquet"
        write_table(rows, name, output)
        files[name] = output
        if not dry_run:
            store.put_file(
                f"silver/{name}/snapshot_date={snapshot_date}/data.parquet",
                output,
                content_type="application/vnd.apache.parquet",
            )
    return files


def _json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n"
    ).encode()


def _content_type(name: str) -> str:
    if name.endswith(".xml"):
        return "application/xml"
    if name.endswith(".zip"):
        return "application/zip"
    return "text/csv"
