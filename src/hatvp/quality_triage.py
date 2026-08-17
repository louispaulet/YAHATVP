"""CLI façade for source-linked HATVP quality review artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

from .storage import GCSArtifactStore, LocalArtifactStore
from .triage_fingerprints import declaration_xml_fingerprints
from .triage_register import build_review_register
from .triage_report import render_markdown, write_review_artifacts
from .triage_snapshot import build_snapshot_review

SNAPSHOT_DATE = "2026-08-16"


def artifact_store(bucket: str | None, local_root: Path | None, prefix: str):
    """Select the configured triage artifact adapter for CLI and tests."""

    if bucket:
        return GCSArtifactStore(bucket, prefix)
    if local_root is None:
        raise ValueError("Either --bucket or --local-root is required")
    return LocalArtifactStore(local_root, prefix)


def triage_snapshot_path(output_dir: Path, snapshot_date: str) -> Path:
    """Return the local report directory for a snapshot review."""

    return output_dir / f"snapshot_date={snapshot_date}"


def triage_output_paths(output_dir: Path, snapshot_date: str) -> tuple[Path, Path]:
    """Return the JSON and Markdown destinations for a snapshot review."""

    directory = triage_snapshot_path(output_dir, snapshot_date)
    return directory / "review.json", directory / "review.md"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--bucket")
    source.add_argument("--local-root", type=Path)
    parser.add_argument("--prefix", default="hatvp")
    parser.add_argument("--snapshot-date", default=SNAPSHOT_DATE)
    parser.add_argument("--source-uri-prefix")
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    store = artifact_store(args.bucket, args.local_root, args.prefix)
    review = build_snapshot_review(store, args.snapshot_date, args.source_uri_prefix)
    json_path, markdown_path = write_review_artifacts(review, args.output_dir)
    print(f"wrote {json_path}")
    print(f"wrote {markdown_path}")
    return 0


__all__ = [
    "build_review_register",
    "build_snapshot_review",
    "declaration_xml_fingerprints",
    "artifact_store",
    "triage_snapshot_path",
    "main",
    "render_markdown",
    "write_review_artifacts",
]


if __name__ == "__main__":
    raise SystemExit(main())
