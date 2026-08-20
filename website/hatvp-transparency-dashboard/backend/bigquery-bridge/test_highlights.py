import json

from highlight_payloads import highlights_payload
from query_highlights import build_highlights_query


def row():
    return {
        "snapshot_date": "2026-08-19",
        "generated_at": "2026-08-20T00:00:00Z",
        "income_changes_json": json.dumps(
            [
                {
                    "declaration_uuid": "income-1",
                    "prenom": "Alice",
                    "nom": "DUPONT",
                    "previous_year": 2023,
                    "income_year": 2024,
                    "previous_amount": 50_000,
                    "amount": 120_000,
                    "absolute_change": 70_000,
                    "ratio": 2.4,
                    "review_required": True,
                }
            ]
        ),
        "unusual_assets_json": json.dumps(
            [
                {
                    "declaration_uuid": "asset-1",
                    "prenom": "Bob",
                    "nom": "MARTIN",
                    "source_section": "immeubleDto",
                    "asset_name": "Maison",
                    "raw_value": "2 400 000",
                    "normalized_value": 2_400_000,
                    "anomaly_status": "active",
                    "review_required": True,
                }
            ]
        ),
        "amended_records_json": json.dumps(
            [
                {
                    "declaration_uuid": "amended-1",
                    "prenom": "Claire",
                    "nom": "DURAND",
                    "filing_count": 5,
                    "amended_count": 3,
                    "first_filed": "2022-01-01",
                    "latest_filed": "2026-01-01",
                }
            ]
        ),
    }


def test_highlights_query_is_fixed_source_linked_and_excludes_current_year():
    query = build_highlights_query("project", "dataset")
    assert "gold_incomes" in query and "gold_assets" in query and "anomaly_registry" in query
    assert "silver_declarations" in query and "silver_people" in query
    assert "current_declarations" in query
    assert "status NOT IN ('superseded', 'resolved')" in query
    assert "r.rule_id IN (" in query
    assert "date_debut_mandat" not in query
    assert "PARTITION BY h.declaration_uuid" in query
    assert "PARTITION BY a.declaration_uuid" in query
    assert "SAFE_CAST(i.income_year AS INT64) < EXTRACT(YEAR" in query
    assert "h.previous_year = h.income_year - 1" in query
    assert "h.review_required OR h.previous_review_required" in query
    assert "p.date_naissance_date" in query
    assert "adresse_" not in query and "telephone" not in query and "email" not in query


def test_highlights_payload_preserves_values_and_review_state():
    payload = highlights_payload(row())
    assert payload["incomeChanges"][0]["absoluteChange"] == 70_000
    assert payload["incomeChanges"][0]["reviewRequired"] is True
    assert payload["unusualAssets"][0]["rawValue"] == "2 400 000"
    assert payload["amendedRecords"][0]["amendedCount"] == 3
