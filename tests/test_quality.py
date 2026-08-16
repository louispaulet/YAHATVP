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
