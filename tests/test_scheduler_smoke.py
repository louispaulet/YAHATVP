"""Unit tests for the versioned Cloud Scheduler smoke task."""

import json
from datetime import UTC, datetime

from hatvp.scheduler_smoke import (
    PARIS_ZONE,
    SCHEDULER_SMOKE_TASK_VERSION,
    main,
    observed_times,
    parse_args,
    payload,
    runtime_fields,
)


def test_scheduler_smoke_reports_version_and_completes(capsys) -> None:
    assert main([]) == 0

    result = json.loads(capsys.readouterr().out)
    assert result["event"] == "scheduler_smoke"
    assert result["status"] == "success"
    assert result["scheduler_smoke_task_version"] == SCHEDULER_SMOKE_TASK_VERSION
    assert result["observed_at_europe_paris"].endswith(("+01:00", "+02:00"))


def test_scheduler_smoke_version_flag(capsys) -> None:
    assert main(["--version"]) == 0
    assert capsys.readouterr().out.strip() == SCHEDULER_SMOKE_TASK_VERSION


def test_payload_converts_a_known_utc_time_to_paris() -> None:
    observed = datetime(2026, 1, 1, 12, tzinfo=UTC)

    value = payload(observed)

    assert value["observed_at_utc"] == observed.isoformat()
    assert value["observed_at_europe_paris"].endswith("+01:00")
    assert observed.astimezone(PARIS_ZONE).hour == 13


def test_smoke_helpers_keep_cli_and_runtime_boundaries_typed() -> None:
    assert parse_args(["--version"]).version is True
    assert set(runtime_fields()) == {"cloud_run_execution", "cloud_run_task_index"}
    utc, paris = observed_times(datetime(2026, 8, 17, tzinfo=UTC))
    assert utc.endswith("+00:00")
    assert paris.endswith("+02:00")


def test_payload_uses_unknown_values_when_cloud_run_metadata_is_absent(monkeypatch) -> None:
    monkeypatch.delenv("CLOUD_RUN_EXECUTION", raising=False)
    monkeypatch.delenv("CLOUD_RUN_TASK_INDEX", raising=False)

    value = payload(datetime(2026, 8, 17, tzinfo=UTC))

    assert value["cloud_run_execution"] == "unknown"
    assert value["cloud_run_task_index"] == "unknown"


def test_versioned_smoke_parser_rejects_unknown_arguments() -> None:
    import pytest

    with pytest.raises(SystemExit):
        parse_args(["--unexpected"])


def test_runtime_fields_have_string_values_for_json_serialization() -> None:
    assert all(isinstance(value, str) for value in runtime_fields().values())


def test_payload_contains_both_timezones_for_a_fixed_observation() -> None:
    value = payload(datetime(2026, 8, 17, 10, tzinfo=UTC))
    assert value["observed_at_utc"].startswith("2026-08-17T10:00:00")
    assert "observed_at_europe_paris" in value
