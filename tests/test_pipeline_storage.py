"""Storage adapter and BigQuery injection tests for pipeline outputs."""

from pathlib import Path

import pytest
from google.api_core.exceptions import PreconditionFailed

from hatvp import main as main_module
from hatvp.bigquery import ALL_TABLES
from hatvp.main import run_pipeline
from hatvp.pipeline import default_store
from hatvp.pipeline.source_contract import source_ids
from hatvp.storage import GCSArtifactStore, artifact_path, artifact_uri, is_immutable_artifact
from tests.pipeline_support import (
    fixture_downloader,
    settings,
    settings_with_bigquery,
    warning_status,
)


class FakeGCSBlob:
    def __init__(self, bucket: "FakeGCSBucket", name: str) -> None:
        self.bucket = bucket
        self.name = name

    def upload_from_string(self, content: bytes, **_: object) -> None:
        if self.name in self.bucket.objects:
            raise PreconditionFailed("object already exists")
        self.bucket.objects[self.name] = bytes(content)

    def exists(self) -> bool:
        return self.name in self.bucket.objects

    def download_as_bytes(self) -> bytes:
        return self.bucket.objects[self.name]


class FakeGCSBucket:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def blob(self, name: str) -> FakeGCSBlob:
        return FakeGCSBlob(self, name)


def test_gcs_immutable_write_is_idempotent_for_same_bytes_and_rejects_changes() -> None:
    store = GCSArtifactStore.__new__(GCSArtifactStore)
    store.bucket = FakeGCSBucket()
    store.prefix = "hatvp"
    store.put_bytes("raw/snapshot_date=2026-08-16/liste.csv", b"original", immutable=True)
    store.put_bytes("raw/snapshot_date=2026-08-16/liste.csv", b"original", immutable=True)

    with pytest.raises(PreconditionFailed):
        store.put_bytes("raw/snapshot_date=2026-08-16/liste.csv", b"changed", immutable=True)
    assert store.read_bytes("raw/snapshot_date=2026-08-16/liste.csv") == b"original"


def test_bigquery_receives_bronze_silver_gold_and_registry_tables(
    tmp_path: Path, monkeypatch
) -> None:
    captured: dict[str, object] = {}

    def capture_bigquery(**kwargs: object) -> None:
        captured.update(kwargs)

    monkeypatch.setattr(main_module, "load_parquet_tables", capture_bigquery)
    warning_status(
        run_pipeline(settings_with_bigquery(tmp_path / "output"), downloader=fixture_downloader)
    )

    assert captured["table_names"] == ALL_TABLES
    assert captured["location"] == "europe-west1"
    assert set(captured["table_files"]) >= set(ALL_TABLES)
    assert captured["gcs_uris"] is None


def test_storage_path_helpers_keep_prefix_and_raw_immutability_explicit() -> None:
    assert artifact_uri("hatvp/", "/raw/file.xml") == "hatvp/raw/file.xml"
    assert artifact_path("/hatvp/", "/raw/file.xml") == ("hatvp", "raw/file.xml")
    assert is_immutable_artifact("raw/file.xml")
    assert not is_immutable_artifact("quality/report.json")


def test_source_discovery_keeps_legacy_official_state_with_archive_source(tmp_path: Path) -> None:
    store = default_store(settings(tmp_path / "output"))
    store.put_bytes("state/latest.json", b'{"snapshot_date":"2026-08-23"}\n')
    store.put_bytes("state/sources/wayback_github/latest.json", b'{"source_id":"wayback_github"}\n')
    assert source_ids(store) == ("hatvp_website", "wayback_github")
