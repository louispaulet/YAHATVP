"""Select one historical Parquet representation per snapshot."""

from __future__ import annotations


def preferred_history_paths(bronze_paths: list[str], silver_paths: list[str]) -> list[str]:
    """Prefer Bronze per snapshot, falling back to legacy Silver partitions."""

    selected: dict[tuple[str, str], str] = {}
    for layer, paths in (("silver", silver_paths), ("bronze", bronze_paths)):
        for path in sorted(paths):
            if not path.endswith("data.parquet"):
                continue
            snapshot = next(
                (
                    part.partition("=")[2]
                    for part in path.split("/")
                    if part.startswith("snapshot_date=")
                ),
                None,
            )
            key = ("snapshot", snapshot) if snapshot is not None else (layer, path)
            selected[key] = path
    return sorted(selected.values())
