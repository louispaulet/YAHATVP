"""Income coverage quality checks and source-stream reconciliation tests."""

from hatvp.quality import run_quality_checks
from tests.quality_support import tables


def test_income_coverage_is_reported_separately_from_row_count() -> None:
    value = tables()
    value["declarations"][0].update(
        {"income_section_present": True, "income_section_populated_item_count": 0}
    )
    value["declarations"][1].update(
        {"income_section_present": True, "income_section_populated_item_count": 1}
    )
    value["incomes"][0].update({"raw_value": "20 000 001", "spouse_raw_value": None})

    result = run_quality_checks(value, snapshot_date="2026-08-16")

    assert result.report["counts"]["incomes"] == 1
    assert result.report["checks"]["income_section_declarations"] == 2
    assert result.report["checks"]["income_declarations"] == 1
    assert result.report["checks"]["income_rows_with_source_value"] == 1
    assert result.report["checks"]["income_rows_with_numeric_value"] == 1
    assert result.report["checks"]["income_sections_without_rows"] == 1


def test_mandate_remuneration_coverage_is_reported_separately() -> None:
    value = tables()
    value["mandate_remunerations"] = [
        {
            "declaration_uuid": "a",
            "snapshot_date": "2026-08-16",
            "normalized_value": 55_740.0,
            "raw_value": "55 740",
            "remuneration_year": 2020,
        },
        {
            "declaration_uuid": "a",
            "snapshot_date": "2026-08-16",
            "normalized_value": 0.0,
            "raw_value": "0",
            "remuneration_year": 2021,
        },
    ]

    result = run_quality_checks(value, snapshot_date="2026-08-16")

    assert result.report["counts"]["mandate_remunerations"] == 2
    assert result.report["checks"]["mandate_remuneration_declarations"] == 1
    assert result.report["checks"]["mandate_remuneration_rows_with_source_value"] == 2
    assert result.report["checks"]["mandate_remuneration_rows_with_numeric_value"] == 2


def test_unified_income_coverage_reports_each_source_stream() -> None:
    value = tables()
    value["incomes"].append(
        {
            "declaration_uuid": "b",
            "source_section": "mandatElectifDto",
            "income_stream": "mandate_remuneration",
            "income_year": "2025",
            "raw_value": "50 000",
            "normalized_value": 50_000.0,
            "spouse_raw_value": None,
        }
    )

    result = run_quality_checks(value, snapshot_date="2026-08-16")

    assert result.report["checks"]["income_rows_by_stream"] == {
        "mandate_remuneration": 1,
        "unknown": 1,
    }
    assert result.report["checks"]["income_declarations_by_stream"] == {
        "mandate_remuneration": 1,
        "unknown": 1,
    }
