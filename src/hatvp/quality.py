from __future__ import annotations

import json
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass
from statistics import median
from typing import Any

logger = logging.getLogger(__name__)

CATASTROPHIC_ROW_COUNT_THRESHOLD = 0.5
MINIMUM_PREVIOUS_ROWS_FOR_COUNT_CHECK = 20
FLAGGED_RECORDS_INCREASE_THRESHOLD = 0.10


@dataclass
class QualityResult:
    report: dict[str, Any]
    anomalies: list[dict[str, Any]]

    @property
    def has_errors(self) -> bool:
        return self.report["quality"]["errors"] > 0

    @property
    def has_warnings(self) -> bool:
        return self.report["quality"]["warnings"] > 0 or bool(self.anomalies)


def _add_anomaly(
    anomalies: list[dict[str, Any]],
    *,
    table_name: str,
    row: dict[str, Any],
    reason: str,
    status: str = "FLAG",
) -> None:
    row["quality_status"] = status
    row["quality_reason"] = reason
    anomalies.append(
        {
            "table_name": table_name,
            "declaration_uuid": row.get("declaration_uuid"),
            "record_key": row.get("raw_record_json") or row.get("source_item_index"),
            "quality_status": status,
            "quality_reason": reason,
            "raw_record_json": json.dumps(row, ensure_ascii=False, sort_keys=True, default=str),
        }
    )


def _duplicate_count(rows: list[dict[str, Any]], key: str) -> int:
    values = [row.get(key) for row in rows if row.get(key)]
    return sum(count - 1 for count in Counter(values).values() if count > 1)


def _has_catastrophic_row_count_reduction(current: int, previous: int | None) -> bool:
    return (
        previous is not None
        and previous >= MINIMUM_PREVIOUS_ROWS_FOR_COUNT_CHECK
        and current < previous * CATASTROPHIC_ROW_COUNT_THRESHOLD
    )


def _previous_quality_summary(
    previous_report: dict[str, Any] | None,
) -> dict[str, Any]:
    if not previous_report or previous_report.get("status") not in {"ok", "warning"}:
        return {}
    quality = previous_report.get("quality")
    return quality if isinstance(quality, dict) else {}


def _robust_outliers(
    rows: list[dict[str, Any]],
    *,
    table_name: str,
    field_name: str,
    reason: str,
    anomalies: list[dict[str, Any]],
) -> int:
    values = [row.get(field_name) for row in rows if isinstance(row.get(field_name), (int, float))]
    if len(values) < 8:
        return 0
    center = median(values)
    mad = median([abs(value - center) for value in values])
    if mad == 0:
        return 0
    scale = 1.4826 * mad
    flagged = 0
    for row in rows:
        value = row.get(field_name)
        if not isinstance(value, (int, float)) or row.get("quality_status") == "FLAG":
            continue
        if abs(value - center) / scale > 10:
            _add_anomaly(anomalies, table_name=table_name, row=row, reason=reason)
            flagged += 1
    return flagged


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


def run_quality_checks(
    tables: dict[str, list[dict[str, Any]]],
    *,
    previous_report: dict[str, Any] | None = None,
    snapshot_date: str,
) -> QualityResult:
    errors = 0
    warnings = 0
    anomalies: list[dict[str, Any]] = []
    checks: dict[str, int] = {}

    declarations = tables.get("declarations", [])
    people = tables.get("people", [])
    incomes = tables.get("incomes", [])
    mandate_remunerations = tables.get("mandate_remunerations", [])
    assets = tables.get("assets", [])

    missing_required_fields = 0
    for table_name, fields in REQUIRED_FIELDS.items():
        rows = tables.get(table_name, [])
        for row in rows:
            missing_required_fields += sum(field not in row for field in fields)
    checks["missing_required_fields"] = missing_required_fields
    if missing_required_fields:
        errors += missing_required_fields

    missing_declaration_ids = sum(not row.get("declaration_uuid") for row in declarations)
    checks["missing_declaration_ids"] = missing_declaration_ids
    if missing_declaration_ids:
        errors += missing_declaration_ids

    duplicate_declaration_ids = _duplicate_count(declarations, "declaration_uuid")
    checks["duplicate_declaration_ids"] = duplicate_declaration_ids
    if duplicate_declaration_ids:
        warnings += duplicate_declaration_ids
        grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in declarations:
            if row.get("declaration_uuid"):
                grouped[row["declaration_uuid"]].append(row)
        for declaration_uuid, rows in grouped.items():
            if len(rows) > 1:
                for row in rows:
                    _add_anomaly(
                        anomalies,
                        table_name="declarations",
                        row=row,
                        reason=f"duplicate declaration_uuid: {declaration_uuid}",
                    )

    duplicate_names = 0
    names: defaultdict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in people:
        name = (row.get("prenom") or "").casefold(), (row.get("nom") or "").casefold()
        if all(name) and name != ("", ""):
            names[name].append(row)
    for rows in names.values():
        if len(rows) > 1:
            duplicate_names += len(rows) - 1
            for row in rows:
                _add_anomaly(
                    anomalies,
                    table_name="people",
                    row=row,
                    reason="repeated name; retained because names are not stable identity keys",
                )
    checks["duplicate_person_names"] = duplicate_names
    warnings += duplicate_names

    declaration_ids = {
        row.get("declaration_uuid") for row in declarations if row.get("declaration_uuid")
    }
    for table_name, rows in tables.items():
        if table_name in {"declarations", "liste"}:
            continue
        missing_refs = sum(row.get("declaration_uuid") not in declaration_ids for row in rows)
        if missing_refs:
            checks[f"orphan_{table_name}"] = missing_refs
            errors += missing_refs

    income_section_declarations = sum(
        row.get("income_section_present") is True for row in declarations
    )
    income_declarations = len(
        {row.get("declaration_uuid") for row in incomes if row.get("declaration_uuid")}
    )
    income_rows_with_source_value = sum(
        row.get("raw_value") is not None or row.get("spouse_raw_value") is not None
        for row in incomes
    )
    income_rows_with_numeric_value = sum(
        isinstance(row.get("normalized_value"), (int, float))
        or isinstance(row.get("spouse_normalized_value"), (int, float))
        for row in incomes
    )
    income_sections_without_rows = sum(
        row.get("income_section_present") is True
        and row.get("income_section_populated_item_count") == 0
        for row in declarations
    )
    checks["income_section_declarations"] = income_section_declarations
    checks["income_declarations"] = income_declarations
    checks["income_rows_with_source_value"] = income_rows_with_source_value
    checks["income_rows_with_numeric_value"] = income_rows_with_numeric_value
    checks["income_sections_without_rows"] = income_sections_without_rows
    warnings += income_sections_without_rows

    def income_stream(row: dict[str, Any]) -> str:
        explicit_stream = row.get("income_stream")
        if explicit_stream:
            return explicit_stream
        return {
            "revenuMandatDto": "revenu_mandat",
            "mandatElectifDto": "mandate_remuneration",
        }.get(row.get("source_section"), "unknown")

    income_rows_by_stream = Counter(income_stream(row) for row in incomes)
    income_declarations_by_stream = {
        stream: len(
            {
                row.get("declaration_uuid")
                for row in incomes
                if income_stream(row) == stream and row.get("declaration_uuid")
            }
        )
        for stream in income_rows_by_stream
    }
    checks["income_rows_by_stream"] = dict(sorted(income_rows_by_stream.items()))
    checks["income_declarations_by_stream"] = dict(sorted(income_declarations_by_stream.items()))

    mandate_remuneration_declarations = len(
        {
            row.get("declaration_uuid")
            for row in mandate_remunerations
            if row.get("declaration_uuid")
        }
    )
    mandate_remuneration_rows_with_source_value = sum(
        row.get("raw_value") is not None for row in mandate_remunerations
    )
    mandate_remuneration_rows_with_numeric_value = sum(
        isinstance(row.get("normalized_value"), (int, float)) for row in mandate_remunerations
    )
    checks["mandate_remuneration_declarations"] = mandate_remuneration_declarations
    checks["mandate_remuneration_rows_with_source_value"] = (
        mandate_remuneration_rows_with_source_value
    )
    checks["mandate_remuneration_rows_with_numeric_value"] = (
        mandate_remuneration_rows_with_numeric_value
    )

    huge_income = 0
    negative_income = 0
    for row in incomes:
        value = row.get("normalized_value")
        if value is not None and value < 0:
            negative_income += 1
            _add_anomaly(anomalies, table_name="incomes", row=row, reason="negative income value")
        elif value is not None and value > 10_000_000:
            huge_income += 1
            _add_anomaly(
                anomalies, table_name="incomes", row=row, reason="annual income exceeds €10,000,000"
            )
    checks["negative_income"] = negative_income
    checks["huge_income"] = huge_income
    outlier_income = _robust_outliers(
        incomes,
        table_name="incomes",
        field_name="normalized_value",
        reason="robust statistical income outlier; retained for review",
        anomalies=anomalies,
    )
    checks["statistical_income_outlier"] = outlier_income
    warnings += negative_income + huge_income + outlier_income

    huge_assets = 0
    negative_assets = 0
    for row in assets:
        value = row.get("normalized_value")
        if value is not None and value < 0:
            negative_assets += 1
            _add_anomaly(anomalies, table_name="assets", row=row, reason="negative asset value")
        elif value is not None and value > 100_000_000_000:
            huge_assets += 1
            _add_anomaly(
                anomalies, table_name="assets", row=row, reason="asset value exceeds €100 billion"
            )
    checks["negative_assets"] = negative_assets
    checks["huge_assets"] = huge_assets
    outlier_assets = _robust_outliers(
        assets,
        table_name="assets",
        field_name="normalized_value",
        reason="robust statistical asset outlier; retained for review",
        anomalies=anomalies,
    )
    checks["statistical_asset_outlier"] = outlier_assets
    warnings += negative_assets + huge_assets + outlier_assets

    counts = {name: len(rows) for name, rows in tables.items()}
    null_rates: dict[str, dict[str, float]] = {}
    for table_name, fields in NULL_RATE_FIELDS.items():
        rows = tables.get(table_name, [])
        if rows:
            null_rates[table_name] = {
                field: round(sum(row.get(field) is None for row in rows) / len(rows), 6)
                for field in fields
            }
    previous_counts = {}
    if previous_report and previous_report.get("status") in {"ok", "warning"}:
        previous_counts = previous_report.get("counts", {})
    catastrophic_reductions = 0
    for name, count in counts.items():
        if _has_catastrophic_row_count_reduction(count, previous_counts.get(name)):
            catastrophic_reductions += 1
            checks[f"catastrophic_row_count_reduction_{name}"] = 1
    checks["catastrophic_row_count_reductions"] = catastrophic_reductions
    warnings += catastrophic_reductions

    status = "error" if errors else "warning" if warnings else "ok"
    previous_quality = _previous_quality_summary(previous_report)
    previous_flagged_records = previous_quality.get("flagged_records")
    if not isinstance(previous_flagged_records, int) or previous_flagged_records < 0:
        previous_flagged_records = None

    previous_warning_streak = previous_quality.get("warning_streak", 0)
    if not isinstance(previous_warning_streak, int) or previous_warning_streak < 0:
        previous_warning_streak = 0
    warning_streak = (
        previous_warning_streak + 1
        if status == "warning" and previous_report and previous_report.get("status") == "warning"
        else 1
        if status == "warning"
        else 0
    )

    flagged_records = len(anomalies)
    flagged_records_increase_ratio = None
    quality_regression = False
    if previous_flagged_records is not None:
        if previous_flagged_records == 0:
            quality_regression = flagged_records > 0
        else:
            flagged_records_increase_ratio = round(
                (flagged_records - previous_flagged_records) / previous_flagged_records,
                6,
            )
            quality_regression = flagged_records_increase_ratio > FLAGGED_RECORDS_INCREASE_THRESHOLD
    quality_regression = quality_regression and status in {"ok", "warning"}

    report = {
        "snapshot_date": snapshot_date,
        "status": status,
        "counts": counts,
        "null_rates": null_rates,
        "quality": {
            "errors": errors,
            "warnings": warnings,
            "flagged_records": flagged_records,
            "previous_flagged_records": previous_flagged_records,
            "flagged_records_increase_ratio": flagged_records_increase_ratio,
            "quality_regression": quality_regression,
            "warning_streak": warning_streak,
        },
        "checks": checks,
    }
    logger.info(
        "quality_complete",
        extra={
            "event": "quality_complete",
            "status": status,
            "counts": counts,
            "errors": errors,
            "warnings": warnings,
            "flagged_records": flagged_records,
            "previous_flagged_records": previous_flagged_records,
            "flagged_records_increase_ratio": flagged_records_increase_ratio,
            "quality_regression": quality_regression,
            "warning_streak": warning_streak,
        },
    )
    if warning_streak >= 2:
        logger.warning(
            "quality_warning_streak",
            extra={
                "event": "quality_warning_streak",
                "status": status,
                "snapshot_date": snapshot_date,
                "warning_streak": warning_streak,
                "flagged_records": flagged_records,
            },
        )
    if quality_regression:
        logger.warning(
            "quality_regression",
            extra={
                "event": "quality_regression",
                "status": status,
                "snapshot_date": snapshot_date,
                "metric": "flagged_records",
                "previous_flagged_records": previous_flagged_records,
                "flagged_records": flagged_records,
                "relative_increase": flagged_records_increase_ratio,
                "threshold": FLAGGED_RECORDS_INCREASE_THRESHOLD,
            },
        )
    return QualityResult(report=report, anomalies=anomalies)
