"""Human-readable quality-triage report rendering and artifact output."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def render_markdown(review: dict[str, Any]) -> str:
    summary = review["summary"]
    evidence = review["evidence"]
    reasons = summary["reason_counts"]
    dispositions = summary["disposition_counts"]
    lines = [
        f"# Quality triage — HATVP snapshot {review['snapshot_date']}",
        "",
        "## Outcome",
        "",
        (
            f"The immutable snapshot contains **{summary['flagged_records']:,} flagged records**, "
            f"with **{summary['unresolved_records']:,} unresolved records**. Reconciliation: "
            f"**{'passed' if summary['reconciliation_passed'] else 'failed'}**."
        ),
        "",
        "## Evidence",
        "",
        "| Item | Value |",
        "| --- | --- |",
        f"| Raw XML SHA-256 | `{evidence['raw_xml_sha256']}` |",
        f"| Quality report | `{evidence['quality_report_uri']}` |",
        f"| Quarantine register | `{evidence['quarantine_uri']}` |",
        "",
        "## Reconciliation",
        "",
        "| Original quality reason | Rows |",
        "| --- | ---: |",
    ]
    lines.extend(f"| {reason} | {count:,} |" for reason, count in sorted(reasons.items()))
    lines.extend(["", "| Review disposition | Rows |", "| --- | ---: |"])
    lines.extend(f"| `{name}` | {count:,} |" for name, count in sorted(dispositions.items()))
    lines.extend(
        [
            "",
            "## Duplicate declaration UUID groups",
            "",
            "| Declaration UUID | Occurrences | Content |",
            "| --- | ---: | --- |",
        ]
    )
    lines.extend(
        (
            f"| `{group['declaration_uuid']}` | {group['occurrence_count']} | "
            f"{group['content_classification']} |"
        )
        for group in review["duplicate_uuid_groups"]
    )
    lines.extend(
        [
            "",
            "## Method",
            "",
            "- Raw XML is authoritative for source verification.",
            "- Stable declaration UUIDs remain the identity boundary.",
            "- Suspicious source values remain retained and flagged.",
            "",
        ]
    )
    return "\n".join(lines)


def write_review_artifacts(review: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"quality-triage-{review['snapshot_date']}.json"
    markdown_path = output_dir / f"quality-triage-{review['snapshot_date']}.md"
    json_path.write_text(json.dumps(review, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    markdown_path.write_text(render_markdown(review))
    return json_path, markdown_path


def format_number(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return f"{value:,.0f}".replace(",", " ") if isinstance(value, (int, float)) else str(value)
