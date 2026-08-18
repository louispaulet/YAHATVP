"""Small source-shaped fixtures for Silver, Gold, and registry unit tests."""

from __future__ import annotations

from typing import Any


def declaration(key: str, snapshot: str, depot: str, amended: str = "false") -> dict[str, Any]:
    """Build one observed declaration parent with the fields Gold orders."""

    return {
        "bronze_record_key": key,
        "declaration_uuid": "person-1",
        "snapshot_date": snapshot,
        "date_depot": depot,
        "date_debut_mandat": "2020-01-01",
        "declaration_modificative": amended,
        "date_derniere_declaration_raw": depot,
        "mandat_label": "Maire",
        "declaration_version": "20171221",
        "source_format": "xml",
        "source_object": f"raw/{snapshot}/declarations.xml",
        "source_location": f"declaration[{key}]",
    }


def income(
    key: str, snapshot: str, value: float, year: str = "2024", raw: str | None = None
) -> dict[str, Any]:
    return {
        "bronze_record_key": key,
        "declaration_uuid": "person-1",
        "snapshot_date": snapshot,
        "source_snapshot_date": snapshot,
        "income_stream": "mandate_remuneration",
        "income_type": "Maire",
        "income_year": year,
        "normalized_value": value,
        "raw_value": raw or str(value),
        "source_format": "xml",
        "source_object": f"raw/{snapshot}/declarations.xml",
        "source_location": f"declaration[{key}]/remuneration",
    }


def people(key: str, snapshot: str, birth: str) -> dict[str, Any]:
    return {
        "bronze_record_key": key,
        "declaration_uuid": "person-1",
        "snapshot_date": snapshot,
        "date_naissance": birth,
        "date_naissance_raw": birth,
        "nom": "TEST",
        "prenom": "Alice",
    }


def layer_tables() -> dict[str, list[dict[str, Any]]]:
    """Return a current fixture containing every required anomaly family."""

    parents = [
        declaration("old", "2025-01-01", "2025-01-01"),
        declaration("new", "2026-01-01", "2026-01-01", "true"),
    ]
    incomes = [
        income("old", "2025-01-01", 50_000),
        income("new", "2026-01-01", 500_000),
        income("new", "2026-01-01", 12_346, year="2023", raw="12346"),
        income("old", "2025-01-01", 12_345, year="2023", raw="12345"),
        income("new", "2026-01-01", 50_000_500_000, year="2022", raw="50000500000"),
        income("new", "2026-01-01", 200, year="2021"),
        income("old", "2025-01-01", 100, year="2021"),
    ]
    people_rows = [
        people("old", "2025-01-01", "1970-01-01"),
        people("new", "2026-01-01", "2099-01-01"),
    ]
    asset = income("new", "2026-01-01", 10_000, year="", raw="10 000")
    asset.update(
        {
            "source_section": "comptesBancaireDto",
            "department": "75",
            "municipality_department": "13",
            "source_values": {"xml": "75", "csv": "13"},
        }
    )
    return {"declarations": parents, "people": people_rows, "incomes": incomes, "assets": [asset]}


def historical_tables() -> dict[str, list[dict[str, Any]]]:
    return {
        "declarations": [declaration("old", "2025-01-01", "2025-01-01")],
        "people": [people("old", "2025-01-01", "1970-01-01")],
        "incomes": [income("old", "2025-01-01", 50_000)],
        "assets": [],
    }
