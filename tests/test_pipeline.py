import json
import shutil
from pathlib import Path

import polars as pl
import pytest
from google.api_core.exceptions import PreconditionFailed

from hatvp import main as main_module
from hatvp.bigquery import CURATED_TABLES
from hatvp.config import Settings
from hatvp.download import DownloadedFile
from hatvp.main import PARQUET_SCHEMAS, TABLE_COLUMNS, PipelineFailure, _write_parquet, run_pipeline
from hatvp.storage import GCSArtifactStore

FIXTURES = Path(__file__).parent / "fixtures"


def _fixture_downloader(url: str, name: str, destination: Path, **_: object) -> DownloadedFile:
    return _downloader_for()(url, name, destination)


def _downloader_for(
    *,
    xml_source: Path = FIXTURES / "declarations.xml",
    csv_source: Path = FIXTURES / "liste.csv",
):
    def downloader(url: str, name: str, destination: Path, **_: object) -> DownloadedFile:
        source = csv_source if name == "liste.csv" else xml_source
        shutil.copyfile(source, destination)
        from hatvp.hashing import sha256_file

        return DownloadedFile(
            name=name,
            url=url,
            path=destination,
            size_bytes=destination.stat().st_size,
            sha256=sha256_file(destination),
            elapsed_seconds=0.001,
        )

    return downloader


def _changed_fixture(source: Path, destination: Path, old: bytes, new: bytes) -> Path:
    content = source.read_bytes()
    assert old in content
    destination.write_bytes(content.replace(old, new, 1))
    return destination


def _state_path(output: Path) -> Path:
    return output / "hatvp" / "state/latest.json"


def _raw_path(output: Path, snapshot_date: str, name: str) -> Path:
    return output / "hatvp" / f"raw/snapshot_date={snapshot_date}/{name}"


def _settings_with_bigquery(output: Path) -> Settings:
    return _settings(output).model_copy(
        update={"hatvp_enable_bigquery": True, "hatvp_bigquery_project": "fixture-project"}
    )


def _assert_warning_status(status: str) -> None:
    assert status == "SUCCESS_WITH_WARNINGS"


def _settings(output: Path) -> Settings:
    return Settings(
        local_output=output,
        hatvp_xml_url="fixture://declarations.xml",
        hatvp_csv_url="fixture://liste.csv",
    )


def _cli_with_fixture(
    monkeypatch: pytest.MonkeyPatch,
    output: Path,
    *,
    xml_source: Path = FIXTURES / "declarations.xml",
    csv_source: Path = FIXTURES / "liste.csv",
) -> int:
    real_run_pipeline = main_module.run_pipeline

    def fixture_run_pipeline(
        settings: Settings, *, dry_run: bool = False, force: bool = False
    ) -> str:
        return real_run_pipeline(
            settings,
            dry_run=dry_run,
            force=force,
            downloader=_downloader_for(xml_source=xml_source, csv_source=csv_source),
        )

    monkeypatch.setattr(main_module, "run_pipeline", fixture_run_pipeline)
    return main_module.cli(["--local-output", str(output)])


def _json_log_events(stderr: str) -> list[dict]:
    return [json.loads(line) for line in stderr.splitlines() if line.startswith("{")]


def test_unchanged_snapshot_detection(tmp_path: Path) -> None:
    output = tmp_path / "output"
    assert (
        run_pipeline(_settings(output), downloader=_fixture_downloader) == "SUCCESS_WITH_WARNINGS"
    )
    state_path = output / "hatvp" / "state/latest.json"
    first_state = json.loads(state_path.read_text())

    assert run_pipeline(_settings(output), downloader=_fixture_downloader) == "NO_CHANGE"
    assert json.loads(state_path.read_text()) == first_state


def test_cli_returns_nonzero_and_logs_failed_for_invalid_xml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    for fixture_name in ("malformed.xml", "invalid_top_level.xml"):
        output = tmp_path / fixture_name.removesuffix(".xml")

        assert _cli_with_fixture(monkeypatch, output, xml_source=FIXTURES / fixture_name) == 1

        events = _json_log_events(capsys.readouterr().err)
        assert any(
            event.get("event") == "pipeline_failed" and event.get("status") == "FAILED"
            for event in events
        )
        assert not _state_path(output).exists()


def test_cli_structural_quality_failure_preserves_previous_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "output"
    changed_xml = _changed_fixture(
        FIXTURES / "declarations.xml",
        tmp_path / "changed-declarations.xml",
        b"fixture-uuid-1",
        b"fixture-uuid-1-quality-failure",
    )
    dates = iter(("2026-08-16", "2026-08-17"))
    monkeypatch.setattr(main_module, "_snapshot_date", lambda: next(dates))

    _assert_warning_status(run_pipeline(_settings(output), downloader=_fixture_downloader))
    previous_state = _state_path(output).read_bytes()

    real_parse_sources = main_module.parse_sources

    def structurally_invalid_parse(*args: object, **kwargs: object) -> dict[str, list[dict]]:
        tables = real_parse_sources(*args, **kwargs)
        tables["declarations"][0].pop("declaration_uuid")
        return tables

    monkeypatch.setattr(main_module, "parse_sources", structurally_invalid_parse)
    assert _cli_with_fixture(monkeypatch, output, xml_source=changed_xml) == 1

    events = _json_log_events(capsys.readouterr().err)
    assert any(
        event.get("event") == "quality_complete" and event.get("status") == "error"
        for event in events
    )
    assert any(
        event.get("event") == "pipeline_failed" and event.get("status") == "FAILED"
        for event in events
    )
    assert _state_path(output).read_bytes() == previous_state


def test_cli_warning_run_emits_structured_hash_quality_and_status_events(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "output"

    assert _cli_with_fixture(monkeypatch, output) == 0

    events = _json_log_events(capsys.readouterr().err)
    by_event = {event.get("event"): event for event in events}
    assert by_event["hash_comparison"]["new_xml_sha256"]
    assert by_event["hash_comparison"]["new_csv_sha256"]
    assert by_event["quality_complete"]["counts"]
    assert by_event["pipeline_complete"]["status"] == "SUCCESS_WITH_WARNINGS"


def test_dry_run_does_not_write_local_outputs(tmp_path: Path) -> None:
    output = tmp_path / "output"

    assert (
        run_pipeline(_settings(output), dry_run=True, downloader=_fixture_downloader)
        == "SUCCESS_WITH_WARNINGS"
    )
    assert not output.exists()


def test_state_is_not_updated_after_pipeline_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "output"

    def broken_downloader(url: str, name: str, destination: Path, **_: object) -> DownloadedFile:
        source = FIXTURES / ("liste.csv" if name == "liste.csv" else "malformed.xml")
        shutil.copyfile(source, destination)
        from hatvp.hashing import sha256_file

        return DownloadedFile(
            name=name,
            url=url,
            path=destination,
            size_bytes=destination.stat().st_size,
            sha256=sha256_file(destination),
            elapsed_seconds=0.001,
        )

    with pytest.raises(ValueError, match="malformed"):
        run_pipeline(_settings(output), downloader=broken_downloader)

    with pytest.raises(ValueError, match="malformed"):
        run_pipeline(_settings(output), downloader=broken_downloader)

    assert not (output / "hatvp" / "state/latest.json").exists()


def test_changed_xml_hash_triggers_processing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "output"
    changed_xml = _changed_fixture(
        FIXTURES / "declarations.xml",
        tmp_path / "changed-declarations.xml",
        b"fixture-uuid-1",
        b"fixture-uuid-1-changed",
    )
    dates = iter(("2026-08-16", "2026-08-17"))
    monkeypatch.setattr(main_module, "_snapshot_date", lambda: next(dates))

    _assert_warning_status(run_pipeline(_settings(output), downloader=_fixture_downloader))
    first_state = json.loads(_state_path(output).read_text())
    _assert_warning_status(
        run_pipeline(_settings(output), downloader=_downloader_for(xml_source=changed_xml))
    )

    second_state = json.loads(_state_path(output).read_text())
    assert second_state["xml_sha256"] != first_state["xml_sha256"]
    assert second_state["snapshot_date"] == "2026-08-17"


def test_changed_csv_hash_triggers_processing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "output"
    changed_csv = _changed_fixture(
        FIXTURES / "liste.csv",
        tmp_path / "changed-liste.csv",
        b"SOURCE-1",
        b"SOURCE-1-changed",
    )
    dates = iter(("2026-08-16", "2026-08-17"))
    monkeypatch.setattr(main_module, "_snapshot_date", lambda: next(dates))

    _assert_warning_status(run_pipeline(_settings(output), downloader=_fixture_downloader))
    first_state = json.loads(_state_path(output).read_text())
    _assert_warning_status(
        run_pipeline(_settings(output), downloader=_downloader_for(csv_source=changed_csv))
    )

    second_state = json.loads(_state_path(output).read_text())
    assert second_state["csv_sha256"] != first_state["csv_sha256"]
    assert second_state["snapshot_date"] == "2026-08-17"


def test_bigquery_failure_does_not_advance_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "output"
    changed_xml = _changed_fixture(
        FIXTURES / "declarations.xml",
        tmp_path / "changed-declarations.xml",
        b"fixture-uuid-1",
        b"fixture-uuid-1-bq-failure",
    )
    dates = iter(("2026-08-16", "2026-08-17"))
    monkeypatch.setattr(main_module, "_snapshot_date", lambda: next(dates))
    _assert_warning_status(run_pipeline(_settings(output), downloader=_fixture_downloader))
    previous_state = _state_path(output).read_bytes()

    def fail_bigquery(**_: object) -> None:
        raise RuntimeError("fixture BigQuery failure")

    monkeypatch.setattr(main_module, "load_parquet_tables", fail_bigquery)
    with pytest.raises(RuntimeError, match="fixture BigQuery failure"):
        run_pipeline(
            _settings_with_bigquery(output),
            downloader=_downloader_for(xml_source=changed_xml),
        )

    assert _state_path(output).read_bytes() == previous_state


def test_bigquery_receives_only_curated_tables(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "output"
    captured: dict[str, object] = {}

    def capture_bigquery(**kwargs: object) -> None:
        captured.update(kwargs)

    monkeypatch.setattr(main_module, "load_parquet_tables", capture_bigquery)
    _assert_warning_status(
        run_pipeline(_settings_with_bigquery(output), downloader=_fixture_downloader)
    )

    assert captured["table_names"] == CURATED_TABLES
    assert captured["location"] == "europe-west1"
    assert set(captured["table_files"]) >= set(CURATED_TABLES)
    assert captured["gcs_uris"] is None


def test_curated_parquet_schema_is_stable_for_empty_and_null_only_rows(
    tmp_path: Path,
) -> None:
    empty_path = tmp_path / "empty-incomes.parquet"
    _write_parquet(
        [],
        empty_path,
        TABLE_COLUMNS["incomes"],
        PARQUET_SCHEMAS["incomes"],
    )
    empty_schema = pl.read_parquet_schema(empty_path)
    assert empty_schema["snapshot_date"] == pl.Date
    assert empty_schema["normalized_value"] == pl.Float64
    assert empty_schema["raw_value"] == pl.String

    null_only_path = tmp_path / "null-only-people.parquet"
    _write_parquet(
        [{"declaration_uuid": "fixture", "snapshot_date": "2026-08-17", "email": None}],
        null_only_path,
        TABLE_COLUMNS["people"],
        PARQUET_SCHEMAS["people"],
    )
    null_only_schema = pl.read_parquet_schema(null_only_path)
    assert null_only_schema["snapshot_date"] == pl.Date
    assert null_only_schema["email"] == pl.String


def test_immutable_raw_snapshot_rejects_different_bytes_for_same_date(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "output"
    changed_csv = _changed_fixture(
        FIXTURES / "liste.csv",
        tmp_path / "changed-liste.csv",
        b"SOURCE-1",
        b"SOURCE-1-conflict",
    )
    monkeypatch.setattr(main_module, "_snapshot_date", lambda: "2026-08-16")
    _assert_warning_status(run_pipeline(_settings(output), downloader=_fixture_downloader))
    previous_state = _state_path(output).read_bytes()

    with pytest.raises(PipelineFailure, match="Immutable raw snapshot 2026-08-16"):
        run_pipeline(_settings(output), downloader=_downloader_for(csv_source=changed_csv))

    assert _state_path(output).read_bytes() == previous_state
    assert (
        _raw_path(output, "2026-08-16", "liste.csv").read_bytes()
        == (FIXTURES / "liste.csv").read_bytes()
    )


class _FakeGCSBlob:
    def __init__(self, bucket: "_FakeGCSBucket", name: str) -> None:
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


class _FakeGCSBucket:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def blob(self, name: str) -> _FakeGCSBlob:
        return _FakeGCSBlob(self, name)


def test_gcs_immutable_write_is_idempotent_for_same_bytes_and_rejects_changes() -> None:
    store = GCSArtifactStore.__new__(GCSArtifactStore)
    store.bucket = _FakeGCSBucket()
    store.prefix = "hatvp"

    store.put_bytes("raw/snapshot_date=2026-08-16/liste.csv", b"original", immutable=True)
    store.put_bytes("raw/snapshot_date=2026-08-16/liste.csv", b"original", immutable=True)

    with pytest.raises(PreconditionFailed):
        store.put_bytes("raw/snapshot_date=2026-08-16/liste.csv", b"changed", immutable=True)

    assert store.read_bytes("raw/snapshot_date=2026-08-16/liste.csv") == b"original"
