import json
import shutil
from pathlib import Path

import pytest

from hatvp import main as main_module
from hatvp.config import Settings
from hatvp.download import DownloadedFile
from hatvp.main import PipelineFailure, run_pipeline

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


def test_unchanged_snapshot_detection(tmp_path: Path) -> None:
    output = tmp_path / "output"
    assert (
        run_pipeline(_settings(output), downloader=_fixture_downloader) == "SUCCESS_WITH_WARNINGS"
    )
    state_path = output / "hatvp" / "state/latest.json"
    first_state = json.loads(state_path.read_text())

    assert run_pipeline(_settings(output), downloader=_fixture_downloader) == "NO_CHANGE"
    assert json.loads(state_path.read_text()) == first_state


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
