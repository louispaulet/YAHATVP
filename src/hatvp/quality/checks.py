"""Structural, referential, identity, and coverage quality checks."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .coverage import count_reductions, income_coverage, null_rates
from .helpers import add_anomaly, duplicate_count

REQUIRED_FIELDS = {
    "declarations": ("declaration_uuid", "snapshot_date"),
    "people": ("declaration_uuid", "snapshot_date"),
    "incomes": ("declaration_uuid", "snapshot_date", "normalized_value"),
    "mandate_remunerations": ("declaration_uuid", "snapshot_date", "normalized_value"),
    "assets": ("declaration_uuid", "snapshot_date", "normalized_value"),
}


def structural_checks(
    tables: dict[str, list[dict[str, Any]]],
    previous_report: dict[str, Any] | None,
    anomalies: list[dict[str, Any]],
) -> tuple[int, int, dict[str, Any], dict[str, dict[str, float]]]:
    errors = warnings = 0
    checks: dict[str, Any] = {}
    declarations = tables.get("declarations", [])
    missing = sum(
        sum(field not in row for field in fields)
        for name, fields in REQUIRED_FIELDS.items()
        for row in tables.get(name, [])
    )
    checks["missing_required_fields"] = missing
    errors += missing
    missing_ids = sum(not row.get("declaration_uuid") for row in declarations)
    checks["missing_declaration_ids"] = missing_ids
    errors += missing_ids
    duplicate_ids = duplicate_count(declarations, "declaration_uuid")
    checks["duplicate_declaration_ids"] = duplicate_ids
    if duplicate_ids:
        warnings += duplicate_ids
        groups = defaultdict(list)
        for row in declarations:
            if row.get("declaration_uuid"):
                groups[row["declaration_uuid"]].append(row)
        for uuid, rows in groups.items():
            if len(rows) > 1:
                for row in rows:
                    add_anomaly(
                        anomalies,
                        table_name="declarations",
                        row=row,
                        reason=f"duplicate declaration_uuid: {uuid}",
                    )
    warnings += _duplicate_names(tables.get("people", []), checks, anomalies)
    declaration_ids = {
        row.get("declaration_uuid") for row in declarations if row.get("declaration_uuid")
    }
    for name, rows in tables.items():
        if name in {"declarations", "liste"}:
            continue
        missing_refs = sum(row.get("declaration_uuid") not in declaration_ids for row in rows)
        if missing_refs:
            checks[f"orphan_{name}"] = missing_refs
            errors += missing_refs
    income_coverage(tables, checks)
    warnings += checks["income_sections_without_rows"]
    counts = {name: len(rows) for name, rows in tables.items()}
    reductions = count_reductions(counts, previous_report, checks)
    checks["catastrophic_row_count_reductions"] = reductions
    warnings += reductions
    return errors, warnings, checks, null_rates(tables)


def _duplicate_names(
    people: list[dict[str, Any]], checks: dict[str, Any], anomalies: list[dict[str, Any]]
) -> int:
    groups: defaultdict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in people:
        key = ((row.get("prenom") or "").casefold(), (row.get("nom") or "").casefold())
        if all(key):
            groups[key].append(row)
    duplicates = 0
    for rows in groups.values():
        if len(rows) > 1:
            duplicates += len(rows) - 1
            for row in rows:
                add_anomaly(
                    anomalies,
                    table_name="people",
                    row=row,
                    reason="repeated name; retained because names are not stable identity keys",
                )
    checks["duplicate_person_names"] = duplicates
    return duplicates
