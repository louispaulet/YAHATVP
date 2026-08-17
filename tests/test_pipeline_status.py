"""Pipeline status, hash short-circuit, and CLI event tests."""

import json
from pathlib import Path

from hatvp import main as main_module
from hatvp.main import run_pipeline
from tests.pipeline_support import (
    FIXTURES,
    cli_with_fixture,
    fixture_downloader,
    json_events,
    settings,
    state_path,
    warning_status,
)


def test_unchanged_snapshot_detection(tmp_path: Path) -> None:
    output = tmp_path / "output"

    warning_status(run_pipeline(settings(output), downloader=fixture_downloader))
    first_state = json.loads(state_path(output).read_text())

    assert run_pipeline(settings(output), downloader=fixture_downloader) == "NO_CHANGE"
    assert json.loads(state_path(output).read_text()) == first_state


def test_dry_run_does_not_write_local_outputs(tmp_path: Path) -> None:
    output = tmp_path / "output"

    status = run_pipeline(settings(output), dry_run=True, downloader=fixture_downloader)

    assert status == "SUCCESS_WITH_WARNINGS"
    assert not output.exists()


def test_cli_warning_run_emits_hash_quality_and_status_events(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    output = tmp_path / "output"

    assert cli_with_fixture(monkeypatch, output) == 0

    events = {event.get("event"): event for event in json_events(capsys.readouterr().err)}
    assert events["hash_comparison"]["new_xml_sha256"]
    assert events["hash_comparison"]["new_csv_sha256"]
    assert events["quality_complete"]["counts"]
    assert events["pipeline_complete"]["status"] == "SUCCESS_WITH_WARNINGS"


def test_cli_with_fixture_uses_the_public_command_boundary(tmp_path: Path, monkeypatch) -> None:
    output = tmp_path / "output"

    result = cli_with_fixture(monkeypatch, output, xml_source=FIXTURES / "declarations.xml")

    assert result == 0
    assert state_path(output).exists()


def test_successful_status_contains_the_expected_snapshot(tmp_path: Path, monkeypatch) -> None:
    output = tmp_path / "output"
    monkeypatch.setattr(main_module, "_snapshot_date", lambda: "2026-08-16")

    warning_status(run_pipeline(settings(output), downloader=fixture_downloader))

    state = json.loads(state_path(output).read_text())
    assert state["snapshot_date"] == "2026-08-16"
    assert state["pipeline_version"]
    assert state["xml_sha256"]


def test_force_reprocesses_an_unchanged_snapshot(tmp_path: Path) -> None:
    output = tmp_path / "output"
    warning_status(run_pipeline(settings(output), downloader=fixture_downloader))

    assert (
        run_pipeline(settings(output), force=True, downloader=fixture_downloader)
        == "SUCCESS_WITH_WARNINGS"
    )
