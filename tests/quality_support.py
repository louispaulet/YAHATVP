"""Small normalized table fixtures for focused quality checks."""

from __future__ import annotations


def tables() -> dict[str, list[dict]]:
    """Return intentionally anomalous rows used by structural and numeric tests."""

    return {
        "declarations": [
            {"declaration_uuid": "a", "snapshot_date": "2026-08-16"},
            {"declaration_uuid": "b", "snapshot_date": "2026-08-16"},
        ],
        "people": [
            {
                "declaration_uuid": "a",
                "snapshot_date": "2026-08-16",
                "prenom": "Alice",
                "nom": "Dupont",
            },
            {
                "declaration_uuid": "b",
                "snapshot_date": "2026-08-16",
                "prenom": "Alice",
                "nom": "Dupont",
            },
        ],
        "mandate_remunerations": [],
        "incomes": [
            {
                "declaration_uuid": "a",
                "snapshot_date": "2026-08-16",
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


def clean_tables() -> dict[str, list[dict]]:
    """Return a warning-free baseline for telemetry regression tests."""

    value = tables()
    value["people"][1]["prenom"] = "Bob"
    value["people"][1]["nom"] = "Martin"
    value["incomes"][0]["normalized_value"] = 20_000.0
    return value


def income_rows() -> list[dict]:
    """Return one declared and one unified mandate income stream."""

    return [
        {
            "declaration_uuid": "a",
            "normalized_value": 20_000.0,
            "raw_value": "20 000",
            "spouse_raw_value": None,
        },
        {
            "declaration_uuid": "b",
            "source_section": "mandatElectifDto",
            "income_stream": "mandate_remuneration",
            "income_year": "2025",
            "raw_value": "50 000",
            "normalized_value": 50_000.0,
            "spouse_raw_value": None,
        },
    ]
