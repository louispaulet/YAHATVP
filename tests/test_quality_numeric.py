"""Numeric quality checks retain suspicious values and expose limits."""

from hatvp.quality import run_quality_checks
from hatvp.quality.numeric import ASSET_LIMIT_EUR, INCOME_LIMIT_EUR, numeric_limits
from tests.quality_support import tables


def test_negative_asset_values_are_retained_and_flagged() -> None:
    value = tables()
    negative_asset = {
        "declaration_uuid": "a",
        "asset_name": "Compte courant",
        "raw_value": "-260",
        "normalized_value": -260.0,
    }
    value["assets"].append(negative_asset)

    result = run_quality_checks(value, snapshot_date="2026-08-16")

    assert negative_asset["normalized_value"] == -260.0
    assert negative_asset["quality_status"] == "FLAG"
    assert negative_asset["quality_reason"] == "negative asset value"
    assert result.report["checks"]["negative_assets"] == 1


def test_numeric_limits_are_explicit_and_match_quality_contract() -> None:
    assert numeric_limits() == {"income_eur": INCOME_LIMIT_EUR, "asset_eur": ASSET_LIMIT_EUR}
    assert INCOME_LIMIT_EUR == 10_000_000
    assert ASSET_LIMIT_EUR == 100_000_000_000


def test_huge_income_is_flagged_without_deleting_the_source_value() -> None:
    value = tables()
    original = value["incomes"][0]["normalized_value"]

    result = run_quality_checks(value, snapshot_date="2026-08-16")

    assert value["incomes"][0]["normalized_value"] == original
    assert result.report["checks"]["huge_income"] == 1
    assert any(row["table_name"] == "incomes" for row in result.anomalies)


def test_numeric_check_reports_outlier_counters_alongside_hard_limits() -> None:
    value = tables()
    value["assets"] = [
        {"declaration_uuid": "a", "normalized_value": 1.0},
        {"declaration_uuid": "b", "normalized_value": 1_000_000.0},
        {"declaration_uuid": "c", "normalized_value": 1_000_001.0},
    ]

    result = run_quality_checks(value, snapshot_date="2026-08-16")

    assert "statistical_asset_outlier" in result.report["checks"]
    assert result.report["checks"]["negative_assets"] == 0
    assert result.report["checks"]["huge_assets"] == 0


def test_numeric_quality_keeps_raw_value_in_anomaly_payload() -> None:
    value = tables()
    value["incomes"][0]["raw_value"] = "20 000 001"

    result = run_quality_checks(value, snapshot_date="2026-08-16")
    income_anomaly = next(row for row in result.anomalies if row["table_name"] == "incomes")

    assert income_anomaly["raw_record_json"]
    assert income_anomaly["quality_reason"] == "annual income exceeds €10,000,000"


def test_numeric_quality_counts_null_values_as_unflagged() -> None:
    value = tables()
    value["assets"] = [{"declaration_uuid": "a", "normalized_value": None}]

    result = run_quality_checks(value, snapshot_date="2026-08-16")

    assert result.report["checks"]["negative_assets"] == 0
    assert result.report["checks"]["huge_assets"] == 0
