from __future__ import annotations

import argparse
import json
import logging
import tempfile
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import polars as pl

from .bigquery import load_parquet_tables
from .config import Settings
from .download import DownloadedFile, download_to_path
from .parser import parse_sources
from .quality import QualityResult, run_quality_checks
from .storage import ArtifactStore, GCSArtifactStore, LocalArtifactStore

logger = logging.getLogger("hatvp")

TABLE_COLUMNS = {
    "liste": ["snapshot_date", "source_file"],
    "declarations": ["declaration_uuid", "snapshot_date", "source_file"],
    "people": ["declaration_uuid", "snapshot_date", "source_file"],
    "mandates": ["declaration_uuid", "snapshot_date", "source_section"],
    "activities": ["declaration_uuid", "snapshot_date", "source_section"],
    "participations": ["declaration_uuid", "snapshot_date", "source_section"],
    "incomes": ["declaration_uuid", "snapshot_date", "source_section", "normalized_value"],
    "assets": ["declaration_uuid", "snapshot_date", "source_section", "normalized_value"],
    "liabilities": ["declaration_uuid", "snapshot_date", "source_section", "normalized_value"],
}


class PipelineFailure(RuntimeError):
    pass


def _configure_logging() -> None:
    class JsonFormatter(logging.Formatter):
        reserved = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__)

        def format(self, record: logging.LogRecord) -> str:
            payload = {
                "timestamp": datetime.now(UTC).isoformat(),
                "severity": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
            payload.update(
                {
                    key: value
                    for key, value in record.__dict__.items()
                    if key not in self.reserved and not key.startswith("_")
                }
            )
            if record.exc_info:
                payload["exception"] = self.formatException(record.exc_info)
            return json.dumps(payload, ensure_ascii=False, default=str)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)


def _snapshot_date() -> str:
    return datetime.now(ZoneInfo("Europe/Paris")).date().isoformat()


def _store(settings: Settings, *, dry_run: bool = False) -> ArtifactStore:
    if settings.local_output is not None:
        return LocalArtifactStore(settings.local_output, settings.hatvp_prefix)
    if dry_run:
        return LocalArtifactStore(
            Path(tempfile.mkdtemp(prefix="hatvp-dry-run-")), settings.hatvp_prefix
        )
    if not settings.hatvp_bucket:
        raise ValueError("HATVP_BUCKET is required unless --local-output is used")
    return GCSArtifactStore(settings.hatvp_bucket, settings.hatvp_prefix)


def _load_state(store: ArtifactStore) -> dict:
    if not store.exists("state/latest.json"):
        return {}
    return json.loads(store.read_bytes("state/latest.json"))


def _write_parquet(rows: list[dict], path: Path, required_columns: list[str]) -> None:
    if rows:
        frame = pl.DataFrame(rows, infer_schema_length=None)
    else:
        frame = pl.DataFrame({column: [] for column in required_columns})
    for column in required_columns:
        if column not in frame.columns:
            frame = frame.with_columns(pl.lit(None).alias(column))
    if "snapshot_date" in frame.columns and frame.schema["snapshot_date"] == pl.String:
        frame = frame.with_columns(pl.col("snapshot_date").str.to_date(format="%Y-%m-%d"))
    frame.write_parquet(path, compression="zstd")


def _write_report(
    store: ArtifactStore, snapshot_date: str, quality: QualityResult, *, dry_run: bool
) -> None:
    if dry_run:
        return
    report_path = f"quality/snapshot_date={snapshot_date}/report.json"
    store.put_bytes(
        report_path,
        (json.dumps(quality.report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(),
        content_type="application/json",
    )
    if quality.anomalies:
        anomaly_path = f"quarantine/snapshot_date={snapshot_date}/anomalies.parquet"
        temporary = Path(tempfile.mkstemp(suffix=".parquet")[1])
        try:
            _write_parquet(
                quality.anomalies, temporary, ["table_name", "quality_status", "quality_reason"]
            )
            store.put_file(anomaly_path, temporary, content_type="application/vnd.apache.parquet")
        finally:
            temporary.unlink(missing_ok=True)


def _archive_raw(
    store: ArtifactStore,
    snapshot_date: str,
    downloaded: dict[str, DownloadedFile],
    metadata: dict,
    *,
    dry_run: bool,
) -> None:
    if dry_run:
        return
    for name, source in downloaded.items():
        store.put_file(
            f"raw/snapshot_date={snapshot_date}/{name}",
            source.path,
            content_type="application/xml" if name.endswith(".xml") else "text/csv",
            immutable=True,
        )
    store.put_bytes(
        f"raw/snapshot_date={snapshot_date}/metadata.json",
        (json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(),
        content_type="application/json",
        immutable=True,
    )


def _reuse_snapshot_metadata(
    store: ArtifactStore,
    snapshot_date: str,
    metadata: dict,
    *,
    dry_run: bool,
) -> dict:
    if dry_run:
        return metadata
    metadata_path = f"raw/snapshot_date={snapshot_date}/metadata.json"
    if not store.exists(metadata_path):
        return metadata
    existing = json.loads(store.read_bytes(metadata_path))
    existing_hashes = {item.get("name"): item.get("sha256") for item in existing.get("files", [])}
    current_hashes = {item.get("name"): item.get("sha256") for item in metadata.get("files", [])}
    if existing_hashes == current_hashes:
        return existing
    raise PipelineFailure(
        f"Immutable raw snapshot {snapshot_date} already exists with different source hashes"
    )


def _write_tables(
    store: ArtifactStore,
    tables: dict[str, list[dict]],
    snapshot_date: str,
    working_dir: Path,
    *,
    dry_run: bool,
) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for table_name, rows in tables.items():
        output = working_dir / f"{table_name}.parquet"
        _write_parquet(rows, output, TABLE_COLUMNS.get(table_name, []))
        files[table_name] = output
        if not dry_run:
            store.put_file(
                f"silver/{table_name}/snapshot_date={snapshot_date}/data.parquet",
                output,
                content_type="application/vnd.apache.parquet",
            )
    return files


def _same_snapshot(state: dict, downloaded: dict[str, DownloadedFile]) -> bool:
    return (
        state.get("xml_sha256") == downloaded["declarations.xml"].sha256
        and state.get("csv_sha256") == downloaded["liste.csv"].sha256
    )


def run_pipeline(
    settings: Settings,
    *,
    dry_run: bool = False,
    force: bool = False,
    downloader: Callable[..., DownloadedFile] = download_to_path,
) -> str:
    if not dry_run:
        settings.validate_storage()
    store = _store(settings, dry_run=dry_run)
    snapshot_date = _snapshot_date()
    started = time.perf_counter()
    previous_state = _load_state(store) if not dry_run else {}

    with tempfile.TemporaryDirectory(prefix="hatvp-run-") as temporary_dir:
        working_dir = Path(temporary_dir)
        downloaded = {
            "liste.csv": downloader(
                settings.hatvp_csv_url,
                "liste.csv",
                working_dir / "liste.csv",
                user_agent=settings.user_agent,
                connect_timeout_seconds=settings.download_connect_timeout_seconds,
                read_timeout_seconds=settings.download_read_timeout_seconds,
                retries=settings.download_retries,
            ),
            "declarations.xml": downloader(
                settings.hatvp_xml_url,
                "declarations.xml",
                working_dir / "declarations.xml",
                user_agent=settings.user_agent,
                connect_timeout_seconds=settings.download_connect_timeout_seconds,
                read_timeout_seconds=settings.download_read_timeout_seconds,
                retries=settings.download_retries,
            ),
        }
        logger.info(
            "hash_comparison",
            extra={
                "event": "hash_comparison",
                "previous_xml_sha256": previous_state.get("xml_sha256"),
                "previous_csv_sha256": previous_state.get("csv_sha256"),
                "new_xml_sha256": downloaded["declarations.xml"].sha256,
                "new_csv_sha256": downloaded["liste.csv"].sha256,
                "snapshot_date": snapshot_date,
            },
        )
        if (
            not force
            and not dry_run
            and previous_state
            and _same_snapshot(previous_state, downloaded)
        ):
            logger.info(
                "pipeline_complete", extra={"event": "pipeline_complete", "status": "NO_CHANGE"}
            )
            return "NO_CHANGE"

        metadata = {
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
        metadata = _reuse_snapshot_metadata(store, snapshot_date, metadata, dry_run=dry_run)
        _archive_raw(store, snapshot_date, downloaded, metadata, dry_run=dry_run)

        tables = parse_sources(
            downloaded["liste.csv"].path,
            downloaded["declarations.xml"].path,
            snapshot_date,
        )
        previous_report = None
        if not dry_run and store.exists(
            f"quality/snapshot_date={previous_state.get('snapshot_date')}/report.json"
        ):
            previous_report = json.loads(
                store.read_bytes(
                    f"quality/snapshot_date={previous_state['snapshot_date']}/report.json"
                )
            )
        quality = run_quality_checks(
            tables, previous_report=previous_report, snapshot_date=snapshot_date
        )
        _write_report(store, snapshot_date, quality, dry_run=dry_run)
        table_files = _write_tables(store, tables, snapshot_date, working_dir, dry_run=dry_run)

        if quality.has_errors:
            raise PipelineFailure(
                f"Quality checks failed: {quality.report['quality']['errors']} error(s)"
            )

        if settings.hatvp_enable_bigquery and not dry_run:
            if not settings.bigquery_project:
                raise PipelineFailure("HATVP_BIGQUERY_PROJECT is required when BigQuery is enabled")
            gcs_uris = None
            if settings.hatvp_bucket and not settings.local_output:
                gcs_uris = {
                    table_name: f"gs://{settings.hatvp_bucket}/{settings.hatvp_prefix}/silver/{table_name}/"
                    f"snapshot_date={snapshot_date}/data.parquet"
                    for table_name in table_files
                }
            load_parquet_tables(
                project=settings.bigquery_project,
                dataset=settings.hatvp_bigquery_dataset,
                table_files=table_files,
                snapshot_date=snapshot_date,
                gcs_uris=gcs_uris,
            )
        elif settings.hatvp_enable_bigquery and dry_run:
            logger.info(
                "bigquery_skipped", extra={"event": "bigquery_skipped", "reason": "dry_run"}
            )

        if not dry_run:
            state = {
                "snapshot_date": snapshot_date,
                "fetched_at": metadata["fetched_at"],
                "xml_sha256": downloaded["declarations.xml"].sha256,
                "csv_sha256": downloaded["liste.csv"].sha256,
                "pipeline_git_sha": settings.pipeline_git_sha,
                "pipeline_version": settings.pipeline_version,
            }
            store.put_bytes(
                "state/latest.json",
                (json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(),
                content_type="application/json",
            )

        status = "SUCCESS_WITH_WARNINGS" if quality.has_warnings else "SUCCESS"
        logger.info(
            "pipeline_complete",
            extra={
                "event": "pipeline_complete",
                "status": status,
                "snapshot_date": snapshot_date,
                "elapsed_seconds": round(time.perf_counter() - started, 3),
            },
        )
        return status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the HATVP ingestion pipeline")
    parser.add_argument(
        "--dry-run", action="store_true", help="Process inputs without mutating outputs"
    )
    parser.add_argument(
        "--force", action="store_true", help="Reprocess even when hashes are unchanged"
    )
    parser.add_argument(
        "--local-output", type=Path, help="Write artifacts below this directory instead of GCS"
    )
    return parser


def cli(argv: list[str] | None = None) -> int:
    _configure_logging()
    args = build_parser().parse_args(argv)
    settings = Settings()
    if args.local_output is not None:
        settings = settings.model_copy(update={"local_output": args.local_output})
    try:
        status = run_pipeline(settings, dry_run=args.dry_run, force=args.force)
    except Exception:
        logger.exception("pipeline_failed", extra={"event": "pipeline_failed", "status": "FAILED"})
        return 1
    logger.info("pipeline_status", extra={"event": "pipeline_status", "status": status})
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
