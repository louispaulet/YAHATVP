"""Raw-only ingestion stages for official and Wayback-backed sources."""

from __future__ import annotations

import tempfile
import zipfile
from collections.abc import Callable
from pathlib import Path

from ..config import Settings
from ..download import DownloadedFile, download_to_path
from ..download.validation import validate_dataset_prefix
from ..hashing import sha256_file
from ..storage import ArtifactStore
from .artifacts import archive_raw
from .source_contract import (
    HF_ARCHIVE_URL,
    OFFICIAL_SOURCE,
    build_source_state,
    load_source_state,
    write_source_state,
)
from .state import build_metadata, reuse_snapshot_metadata
from .steps import download_sources, log_hashes


def ingest_official(
    settings: Settings,
    snapshot: str,
    store: ArtifactStore,
    *,
    downloader: Callable[..., DownloadedFile] = download_to_path,
    dry_run: bool = False,
    force: bool = False,
) -> str:
    previous = load_source_state(store, OFFICIAL_SOURCE) if not dry_run else {}
    with tempfile.TemporaryDirectory(prefix="hatvp-source-") as directory:
        downloaded = download_sources(settings, Path(directory), downloader)
        log_hashes(previous, downloaded, snapshot)
        if not force and previous and _same_files(previous, downloaded):
            return "NO_CHANGE"
        metadata = build_metadata(snapshot, settings, downloaded, OFFICIAL_SOURCE)
        metadata = reuse_snapshot_metadata(store, snapshot, metadata, dry_run, OFFICIAL_SOURCE)
        archive_raw(store, snapshot, downloaded, metadata, dry_run, OFFICIAL_SOURCE)
        if not dry_run:
            write_source_state(store, OFFICIAL_SOURCE, build_source_state(metadata, downloaded))
    return "INGESTED"


def ingest_wayback_zip(
    settings: Settings,
    archive: Path,
    snapshot: str,
    store: ArtifactStore,
    *,
    dry_run: bool = False,
    force: bool = False,
    source_id: str = "wayback_github",
) -> str:
    source_url = HF_ARCHIVE_URL if source_id == "wayback_hf" else f"github://{archive.name}"
    archive_hash = sha256_file(archive)
    previous = load_source_state(store, source_id) if not dry_run else {}
    if not force and previous.get("archive_sha256") == archive_hash:
        return "NO_CHANGE"
    with tempfile.TemporaryDirectory(prefix="hatvp-wayback-") as directory:
        xml_path = _extract_xml(archive, Path(directory) / "declarations.xml")
        downloaded = {
            "declarations.xml": _file(xml_path, source_url),
            archive.name: _file(archive, source_url),
        }
        metadata = build_metadata(snapshot, settings, downloaded, source_id)
        metadata["archive_sha256"] = archive_hash
        metadata = reuse_snapshot_metadata(store, snapshot, metadata, dry_run, source_id)
        archive_raw(store, snapshot, downloaded, metadata, dry_run, source_id)
        if not dry_run:
            write_source_state(store, source_id, build_source_state(metadata, downloaded, archive_hash))  # fmt: skip  # noqa: E501
    return "INGESTED"


def _extract_xml(archive: Path, destination: Path) -> Path:
    with zipfile.ZipFile(archive) as zipped:
        members = [item for item in zipped.namelist() if Path(item).suffix.casefold() == ".xml"]
        if len(members) != 1:
            raise ValueError("Wayback archive must contain exactly one XML document")
        with zipped.open(members[0]) as source, destination.open("wb") as target:
            target.write(source.read())
    validate_dataset_prefix(destination, "declarations.xml")
    return destination


def _file(path: Path, url: str) -> DownloadedFile:
    return DownloadedFile(path.name, url, path, path.stat().st_size, sha256_file(path), 0.0)


def _same_files(previous: dict, downloaded: dict[str, DownloadedFile]) -> bool:
    names = {"declarations.xml": "xml_sha256", "liste.csv": "csv_sha256"}
    return all(
        previous.get(names.get(name, f"{name.replace('.', '_')}_sha256")) == item.sha256
        for name, item in downloaded.items()
    )
