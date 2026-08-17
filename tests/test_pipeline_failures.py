import shutil
from pathlib import Path

import pytest

from hatvp import main as main_module
from hatvp.download import DownloadedFile
from hatvp.main import run_pipeline
from tests.pipeline_support import (
    FIXTURES,
    changed_fixture,
    cli_with_fixture,
    downloader_for,
    fixture_downloader,
    json_events,
    settings,
    settings_with_bigquery,
    state_path,
    warning_status,
)


def test_cli_returns_nonzero_and_logs_failed_for_invalid_xml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    for fixture_name in ("malformed.xml", "invalid_top_level.xml"):
        output = tmp_path / fixture_name.removesuffix(".xml")

        assert cli_with_fixture(monkeypatch, output, xml_source=FIXTURES / fixture_name) == 1
        events = json_events(capsys.readouterr().err)
        assert any(event.get("event") == "pipeline_failed" for event in events)
        assert not state_path(output).exists()


def test_state_is_not_updated_after_parser_failure(tmp_path: Path) -> None:
    output = tmp_path / "output"

    def broken_downloader(url: str, name: str, destination: Path, **_: object) -> DownloadedFile:
        source = FIXTURES / ("liste.csv" if name == "liste.csv" else "malformed.xml")
        shutil.copyfile(source, destination)
        from hatvp.hashing import sha256_file

        return DownloadedFile(
            name, url, destination, destination.stat().st_size, sha256_file(destination), 0.001
        )

    with pytest.raises(ValueError, match="malformed"):
        run_pipeline(settings(output), downloader=broken_downloader)
    assert not state_path(output).exists()


def test_quality_failure_preserves_previous_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    output = tmp_path / "output"
    changed_xml = changed_fixture(
        FIXTURES / "declarations.xml",
        tmp_path / "changed.xml",
        b"fixture-uuid-1",
        b"fixture-quality",
    )
    dates = iter(("2026-08-16", "2026-08-17"))
    monkeypatch.setattr(main_module, "_snapshot_date", lambda: next(dates))
    warning_status(run_pipeline(settings(output), downloader=fixture_downloader))
    previous_state = state_path(output).read_bytes()
    real_parser = main_module.parse_sources

    def invalid_parser(*args: object, **kwargs: object) -> dict:
        tables = real_parser(*args, **kwargs)
        tables["declarations"][0].pop("declaration_uuid")
        return tables

    monkeypatch.setattr(main_module, "parse_sources", invalid_parser)
    assert cli_with_fixture(monkeypatch, output, xml_source=changed_xml) == 1
    assert state_path(output).read_bytes() == previous_state
    assert any(event.get("status") == "error" for event in json_events(capsys.readouterr().err))


def test_bigquery_failure_does_not_advance_state(tmp_path: Path, monkeypatch) -> None:
    output = tmp_path / "output"
    changed_xml = changed_fixture(
        FIXTURES / "declarations.xml", tmp_path / "changed.xml", b"fixture-uuid-1", b"fixture-bq"
    )
    dates = iter(("2026-08-16", "2026-08-17"))
    monkeypatch.setattr(main_module, "_snapshot_date", lambda: next(dates))
    warning_status(run_pipeline(settings(output), downloader=fixture_downloader))
    previous_state = state_path(output).read_bytes()

    monkeypatch.setattr(
        main_module,
        "load_parquet_tables",
        lambda **_: (_ for _ in ()).throw(RuntimeError("fixture BigQuery failure")),
    )
    with pytest.raises(RuntimeError, match="fixture BigQuery failure"):
        run_pipeline(
            settings_with_bigquery(output), downloader=downloader_for(xml_source=changed_xml)
        )
    assert state_path(output).read_bytes() == previous_state
