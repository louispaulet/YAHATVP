from hatvp.quality import run_quality_checks


def _tables() -> dict[str, list[dict]]:
    return {
        "declarations": [
            {"declaration_uuid": "a"},
            {"declaration_uuid": "b"},
        ],
        "people": [
            {"declaration_uuid": "a", "prenom": "Alice", "nom": "Dupont"},
            {"declaration_uuid": "b", "prenom": "Alice", "nom": "Dupont"},
        ],
        "mandate_remunerations": [],
        "incomes": [
            {
                "declaration_uuid": "a",
                "normalized_value": 20_000_001.0,
                "raw_record_json": "income-a",
            }
        ],
        "assets": [],
        "mandates": [],
        "activities": [],
        "participations": [],
        "liabilities": [],
        "liste": [],
    }


def test_duplicate_names_are_flagged_but_not_deduplicated() -> None:
    tables = _tables()
    result = run_quality_checks(tables, snapshot_date="2026-08-16")

    assert len(tables["people"]) == 2
    assert result.report["checks"]["duplicate_person_names"] == 1
    assert result.report["checks"]["huge_income"] == 1
    assert result.report["quality"]["flagged_records"] >= 3
    assert all(row["quality_status"] == "FLAG" for row in tables["people"])


def test_duplicate_stable_identifier_is_reported() -> None:
    tables = _tables()
    tables["declarations"].append({"declaration_uuid": "a"})

    result = run_quality_checks(tables, snapshot_date="2026-08-16")

    assert result.report["checks"]["duplicate_declaration_ids"] == 1
    assert result.report["quality"]["warnings"] > 0


def test_income_coverage_is_reported_separately_from_row_count() -> None:
    tables = _tables()
    tables["declarations"][0].update(
        {"income_section_present": True, "income_section_populated_item_count": 0}
    )
    tables["declarations"][1].update(
        {"income_section_present": True, "income_section_populated_item_count": 1}
    )
    tables["incomes"][0].update({"raw_value": "20 000 001", "spouse_raw_value": None})

    result = run_quality_checks(tables, snapshot_date="2026-08-16")

    assert result.report["counts"]["incomes"] == 1
    assert result.report["checks"]["income_section_declarations"] == 2
    assert result.report["checks"]["income_declarations"] == 1
    assert result.report["checks"]["income_rows_with_source_value"] == 1
    assert result.report["checks"]["income_rows_with_numeric_value"] == 1
    assert result.report["checks"]["income_sections_without_rows"] == 1
    assert result.report["quality"]["warnings"] > 0


def test_mandate_remuneration_coverage_is_reported_separately() -> None:
    tables = _tables()
    tables["mandate_remunerations"] = [
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

    result = run_quality_checks(tables, snapshot_date="2026-08-16")

    assert result.report["counts"]["mandate_remunerations"] == 2
    assert result.report["checks"]["mandate_remuneration_declarations"] == 1
    assert result.report["checks"]["mandate_remuneration_rows_with_source_value"] == 2
    assert result.report["checks"]["mandate_remuneration_rows_with_numeric_value"] == 2


def test_unified_income_coverage_reports_each_source_stream() -> None:
    tables = _tables()
    tables["incomes"].append(
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

    result = run_quality_checks(tables, snapshot_date="2026-08-16")

    assert result.report["checks"]["income_rows_by_stream"] == {
        "mandate_remuneration": 1,
        "unknown": 1,
    }
    assert result.report["checks"]["income_declarations_by_stream"] == {
        "mandate_remuneration": 1,
        "unknown": 1,
    }


def test_catastrophic_row_count_reduction_is_explicitly_reported() -> None:
    result = run_quality_checks(
        _tables(),
        previous_report={
            "status": "warning",
            "counts": {"declarations": 100, "people": 100},
        },
        snapshot_date="2026-08-16",
    )

    assert result.report["checks"]["catastrophic_row_count_reductions"] == 2
    assert result.report["checks"]["catastrophic_row_count_reduction_declarations"] == 1
    assert result.report["checks"]["catastrophic_row_count_reduction_people"] == 1

    failed_previous_report = run_quality_checks(
        _tables(),
        previous_report={
            "status": "error",
            "counts": {"declarations": 100, "people": 100},
        },
        snapshot_date="2026-08-16",
    )
    assert failed_previous_report.report["checks"]["catastrophic_row_count_reductions"] == 0


def test_negative_asset_values_are_retained_and_flagged() -> None:
    tables = _tables()
    negative_asset = {
        "declaration_uuid": "a",
        "asset_name": "Compte courant",
        "raw_value": "-260",
        "normalized_value": -260.0,
    }
    tables["assets"].append(negative_asset)

    result = run_quality_checks(tables, snapshot_date="2026-08-16")

    assert negative_asset["normalized_value"] == -260.0
    assert negative_asset["quality_status"] == "FLAG"
    assert negative_asset["quality_reason"] == "negative asset value"
    assert result.report["checks"]["negative_assets"] == 1
