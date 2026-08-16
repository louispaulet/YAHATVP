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
