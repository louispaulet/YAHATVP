"""Structural, referential, identity, and coverage quality checks."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .quality_helpers import add_anomaly, catastrophic_reduction, duplicate_count

REQUIRED_FIELDS = {
    "declarations": ("declaration_uuid", "snapshot_date"),
    "people": ("declaration_uuid", "snapshot_date"),
    "incomes": ("declaration_uuid", "snapshot_date", "normalized_value"),
    "mandate_remunerations": ("declaration_uuid", "snapshot_date", "normalized_value"),
    "assets": ("declaration_uuid", "snapshot_date", "normalized_value"),
}
NULL_RATE_FIELDS = {
    "declarations": ("declaration_uuid", "declaration_type_id", "date_depot"),
    "people": ("declaration_uuid", "nom", "prenom"),
    "incomes": ("declaration_uuid", "income_year", "normalized_value"),
    "mandate_remunerations": ("declaration_uuid", "remuneration_year", "normalized_value"),
    "assets": ("declaration_uuid", "asset_name", "normalized_value"),
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
    _income_coverage(tables, checks)
    warnings += checks["income_sections_without_rows"]
    counts = {name: len(rows) for name, rows in tables.items()}
    previous_counts = (
        previous_report.get("counts", {})
        if previous_report and previous_report.get("status") in {"ok", "warning"}
        else {}
    )
    reductions = sum(
        _record_reduction(name, count, previous_counts, checks) for name, count in counts.items()
    )
    checks["catastrophic_row_count_reductions"] = reductions
    warnings += reductions
    null_rates = {
        name: {
            field: round(sum(row.get(field) is None for row in rows) / len(rows), 6)
            for field in fields
        }
        for name, fields in NULL_RATE_FIELDS.items()
        if (rows := tables.get(name, []))
    }
    return errors, warnings, checks, null_rates


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


def _income_coverage(tables: dict[str, list[dict[str, Any]]], checks: dict[str, Any]) -> None:
    declarations = tables.get("declarations", [])
    incomes = tables.get("incomes", [])
    checks["income_section_declarations"] = sum(
        row.get("income_section_present") is True for row in declarations
    )
    checks["income_declarations"] = len(
        {row.get("declaration_uuid") for row in incomes if row.get("declaration_uuid")}
    )
    checks["income_rows_with_source_value"] = sum(
        row.get("raw_value") is not None or row.get("spouse_raw_value") is not None
        for row in incomes
    )
    checks["income_rows_with_numeric_value"] = sum(
        isinstance(row.get("normalized_value"), (int, float))
        or isinstance(row.get("spouse_normalized_value"), (int, float))
        for row in incomes
    )
    checks["income_sections_without_rows"] = sum(
        row.get("income_section_present") is True
        and row.get("income_section_populated_item_count") == 0
        for row in declarations
    )
    streams = Counter(_income_stream(row) for row in incomes)
    checks["income_rows_by_stream"] = dict(sorted(streams.items()))
    checks["income_declarations_by_stream"] = {
        stream: len(
            {
                row.get("declaration_uuid")
                for row in incomes
                if _income_stream(row) == stream and row.get("declaration_uuid")
            }
        )
        for stream in streams
    }
    mandate = tables.get("mandate_remunerations", [])
    checks["mandate_remuneration_declarations"] = len(
        {row.get("declaration_uuid") for row in mandate if row.get("declaration_uuid")}
    )
    checks["mandate_remuneration_rows_with_source_value"] = sum(
        row.get("raw_value") is not None for row in mandate
    )
    checks["mandate_remuneration_rows_with_numeric_value"] = sum(
        isinstance(row.get("normalized_value"), (int, float)) for row in mandate
    )


def _income_stream(row: dict[str, Any]) -> str:
    return row.get("income_stream") or {
        "revenuMandatDto": "revenu_mandat",
        "mandatElectifDto": "mandate_remuneration",
    }.get(row.get("source_section"), "unknown")


def _record_reduction(
    name: str, count: int, previous: dict[str, Any], checks: dict[str, Any]
) -> int:
    if catastrophic_reduction(count, previous.get(name)):
        checks[f"catastrophic_row_count_reduction_{name}"] = 1
        return 1
    return 0
