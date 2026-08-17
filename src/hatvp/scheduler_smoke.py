"""Versioned no-op workload for validating Cloud Scheduler delivery."""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

SCHEDULER_SMOKE_TASK_VERSION = "1.0.0"
PARIS_ZONE = ZoneInfo("Europe/Paris")


def payload(observed_at: datetime | None = None) -> dict[str, str]:
    observed_at = observed_at or datetime.now(UTC)
    return {
        "event": "scheduler_smoke",
        "status": "success",
        "scheduler_smoke_task_version": SCHEDULER_SMOKE_TASK_VERSION,
        "observed_at_utc": observed_at.isoformat(),
        "observed_at_europe_paris": observed_at.astimezone(PARIS_ZONE).isoformat(),
        "cloud_run_execution": os.getenv("CLOUD_RUN_EXECUTION", "unknown"),
        "cloud_run_task_index": os.getenv("CLOUD_RUN_TASK_INDEX", "unknown"),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print the smoke task version without running the task.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.version:
        print(SCHEDULER_SMOKE_TASK_VERSION)
        return 0
    print(json.dumps(payload(), separators=(",", ":")))
    return 0


__all__ = ["PARIS_ZONE", "SCHEDULER_SMOKE_TASK_VERSION", "main", "parse_args", "payload"]


if __name__ == "__main__":
    raise SystemExit(main())
