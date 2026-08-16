"""Versioned no-op workload for validating Cloud Scheduler delivery."""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

SCHEDULER_SMOKE_TASK_VERSION = "1.0.0"


def _payload() -> dict[str, str]:
    observed_at = datetime.now(UTC)
    return {
        "event": "scheduler_smoke",
        "status": "success",
        "scheduler_smoke_task_version": SCHEDULER_SMOKE_TASK_VERSION,
        "observed_at_utc": observed_at.isoformat(),
        "observed_at_europe_paris": observed_at.astimezone(ZoneInfo("Europe/Paris")).isoformat(),
        "cloud_run_execution": os.getenv("CLOUD_RUN_EXECUTION", "unknown"),
        "cloud_run_task_index": os.getenv("CLOUD_RUN_TASK_INDEX", "unknown"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print the smoke task version without running the task.",
    )
    args = parser.parse_args(argv)

    if args.version:
        print(SCHEDULER_SMOKE_TASK_VERSION)
        return 0

    # Keep this output as one JSON object so Cloud Logging can query it directly.
    print(json.dumps(_payload(), separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
