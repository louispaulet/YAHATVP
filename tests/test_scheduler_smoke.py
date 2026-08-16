import json

from hatvp.scheduler_smoke import SCHEDULER_SMOKE_TASK_VERSION, main


def test_scheduler_smoke_reports_version_and_completes(capsys):
    assert main([]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["event"] == "scheduler_smoke"
    assert payload["status"] == "success"
    assert payload["scheduler_smoke_task_version"] == SCHEDULER_SMOKE_TASK_VERSION
    assert payload["observed_at_europe_paris"].endswith(("+01:00", "+02:00"))


def test_scheduler_smoke_version_flag(capsys):
    assert main(["--version"]) == 0
    assert capsys.readouterr().out.strip() == SCHEDULER_SMOKE_TASK_VERSION
