"""Coverage metrics and previous-count comparisons for quality reports."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .quality_helpers import catastrophic_reduction

NULL_RATE_FIELDS = {
    "declarations": ("declaration_uuid", "declaration_type_id", "date_depot"),
    "people": ("declaration_uuid", "nom", "prenom"),
    "incomes": ("declaration_uuid", "income_year", "normalized_value"),
    "mandate_remunerations": ("declaration_uuid", "remuneration_year", "normalized_value"),
    "assets": ("declaration_uuid", "asset_name", "normalized_value"),
}


def income_coverage(tables: dict[str, list[dict[str, Any]]], checks: dict[str, Any]) -> None:
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
    streams = Counter(income_stream(row) for row in incomes)
    checks["income_rows_by_stream"] = dict(sorted(streams.items()))
    checks["income_declarations_by_stream"] = {
        stream: len(
            {
                row.get("declaration_uuid")
                for row in incomes
                if income_stream(row) == stream and row.get("declaration_uuid")
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


def income_stream(row: dict[str, Any]) -> str:
    return row.get("income_stream") or {
        "revenuMandatDto": "revenu_mandat",
        "mandatElectifDto": "mandate_remuneration",
    }.get(row.get("source_section"), "unknown")


def null_rates(tables: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, float]]:
    return {
        name: {
            field: round(sum(row.get(field) is None for row in rows) / len(rows), 6)
            for field in fields
        }
        for name, fields in NULL_RATE_FIELDS.items()
        if (rows := tables.get(name, []))
    }


def count_reductions(
    counts: dict[str, int], previous_report: dict[str, Any] | None, checks: dict[str, Any]
) -> int:
    previous = (
        previous_report.get("counts", {})
        if previous_report and previous_report.get("status") in {"ok", "warning"}
        else {}
    )
    reductions = 0
    for name, count in counts.items():
        if catastrophic_reduction(count, previous.get(name)):
            checks[f"catastrophic_row_count_reduction_{name}"] = 1
            reductions += 1
    return reductions


__all__ = ["NULL_RATE_FIELDS", "count_reductions", "income_coverage", "income_stream", "null_rates"]
