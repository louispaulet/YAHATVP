"""Numeric quality checks for incomes and assets."""

from __future__ import annotations

from typing import Any

from .quality_helpers import add_anomaly, robust_outliers

INCOME_LIMIT_EUR = 10_000_000
ASSET_LIMIT_EUR = 100_000_000_000


def numeric_checks(
    tables: dict[str, list[dict[str, Any]]], anomalies: list[dict[str, Any]]
) -> tuple[int, dict[str, int]]:
    warnings = 0
    checks: dict[str, int] = {}
    incomes = tables.get("incomes", [])
    negative_income = huge_income = 0
    for row in incomes:
        value = row.get("normalized_value")
        if value is not None and value < 0:
            negative_income += 1
            add_anomaly(anomalies, table_name="incomes", row=row, reason="negative income value")
        elif value is not None and value > INCOME_LIMIT_EUR:
            huge_income += 1
            add_anomaly(
                anomalies, table_name="incomes", row=row, reason="annual income exceeds €10,000,000"
            )
    outlier_income = robust_outliers(
        incomes,
        table_name="incomes",
        field_name="normalized_value",
        reason="robust statistical income outlier; retained for review",
        anomalies=anomalies,
    )
    checks.update(
        {
            "negative_income": negative_income,
            "huge_income": huge_income,
            "statistical_income_outlier": outlier_income,
        }
    )
    assets = tables.get("assets", [])
    negative_asset = huge_asset = 0
    for row in assets:
        value = row.get("normalized_value")
        if value is not None and value < 0:
            negative_asset += 1
            add_anomaly(anomalies, table_name="assets", row=row, reason="negative asset value")
        elif value is not None and value > ASSET_LIMIT_EUR:
            huge_asset += 1
            add_anomaly(
                anomalies, table_name="assets", row=row, reason="asset value exceeds €100 billion"
            )
    outlier_asset = robust_outliers(
        assets,
        table_name="assets",
        field_name="normalized_value",
        reason="robust statistical asset outlier; retained for review",
        anomalies=anomalies,
    )
    checks.update(
        {
            "negative_assets": negative_asset,
            "huge_assets": huge_asset,
            "statistical_asset_outlier": outlier_asset,
        }
    )
    warnings += sum(checks.values())
    return warnings, checks


def numeric_limits() -> dict[str, int]:
    """Expose the documented hard limits used by the numeric checks."""

    return {"income_eur": INCOME_LIMIT_EUR, "asset_eur": ASSET_LIMIT_EUR}
