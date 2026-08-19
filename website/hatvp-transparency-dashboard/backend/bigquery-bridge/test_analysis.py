import json
from types import SimpleNamespace

from analysis_payloads import age_analysis_payload, simple_analysis_payload
from query_analysis import build_age_analysis_query, build_simple_analysis_query


def row(**values):
    return SimpleNamespace(**values)


def test_simple_analysis_query_filters_salary_ages_and_exposes_zero_counts():
    query = build_simple_analysis_query("project", "dataset")

    assert "date_naissance_date" in query
    assert "date_naissance_quality_status" in query
    assert "ORDER BY age_years" in query
    assert "PERCENTILE_CONT" in query
    assert "WHERE age_years BETWEEN 18 AND 100" in query
    assert "WHERE normalized_value != 0" in query
    assert "FROM salary_age_rows GROUP BY age_bin_start" in query
    assert "age_bins_including_zero_json" in query
    assert "zero_salary_bins_json" in query
    assert "COUNTIF(a.normalized_value = 0)" in query
    assert "metric_eligible" in query
    assert "raw_record_json" not in query


def test_age_analysis_query_ranks_declaration_families_and_keeps_flagged_values():
    query = build_age_analysis_query("project", "dataset")

    assert (
        "REGEXP_REPLACE(NORMALIZE_AND_CASEFOLD(@search_term, NFD), r'\\p{M}', '') AS term" in query
    )
    assert (
        "REGEXP_REPLACE(NORMALIZE_AND_CASEFOLD(COALESCE(p.prenom, ''), NFD), r'\\p{M}', '')"
        in query
    )
    assert "income_by_year" in query
    assert "`project.dataset`.silver_declarations" in query
    assert "`project.dataset`.silver_incomes" in query
    assert "`project.dataset`.silver_assets" in query
    assert "`project.dataset`.gold_declarations" not in query
    assert "PARTITION BY declaration_family" in query
    assert "PARTITION BY pr.declaration_uuid" in query
    assert "declaration_family = 'interest' AND family_rank = 1" in query
    assert "declaration_family = 'assets' AND family_rank = 1" in query
    assert "JOIN latest_interest" in query
    assert "JOIN latest_assets" in query
    assert "AND COALESCE(i.metric_eligible, TRUE)" not in query
    assert "JSON_VALUE(i.raw_record_json, '$.employeur')" in query
    assert "asset_event_date" in query
    assert "asset_event_precision" in query
    assert "occupations_by_year" not in query
    assert "adresse_" not in query


def test_simple_analysis_payload_maps_leaders_and_bins():
    result = simple_analysis_payload(
        row(
            snapshot_date="2026-08-19",
            generated_at="now",
            leaders_json=json.dumps(
                {
                    "reference_date": "2026-08-19",
                    "youngest": [
                        {
                            "declaration_uuid": "young",
                            "prenom": "Young",
                            "nom": "Person",
                            "date_naissance": "2010-01-01",
                            "age_years": 16,
                            "date_naissance_quality_status": "implausible",
                            "mandat_label": "Example",
                            "organ_label": "Example town",
                        }
                    ],
                    "oldest": [],
                }
            ),
            age_bins_json=json.dumps(
                [
                    {
                        "label": "40–44",
                        "age_bin_start": 40,
                        "row_count": 2,
                        "average_value": 20,
                        "median_value": 15,
                    }
                ]
            ),
            age_bins_including_zero_json=json.dumps(
                [
                    {
                        "label": "40–44",
                        "age_bin_start": 40,
                        "row_count": 3,
                        "average_value": 13.333,
                        "median_value": 15,
                    }
                ]
            ),
            zero_salary_bins_json=json.dumps(
                [{"label": "40–44", "age_bin_start": 40, "row_count": 1}]
            ),
        )
    )

    assert result["youngest"][0]["ageYears"] == 16
    assert result["youngest"][0]["qualityStatus"] == "implausible"
    assert result["ageBins"][0]["medianSalary"] == 15.0
    assert result["ageBinsIncludingZero"][0]["rows"] == 3
    assert result["zeroSalaryBins"][0]["rows"] == 1


def test_age_analysis_payload_maps_latest_sources_history_and_asset_events():
    result = age_analysis_payload(
        row(
            snapshot_date="2026-08-19",
            generated_at="now",
            person_json=json.dumps(
                {
                    "person_key": "sebastien|lecornu|1986-06-11",
                    "primary_uuid": "uuid",
                    "prenom": "Sébastien",
                    "nom": "LECORNU",
                    "date_naissance": "1986-06-11",
                    "age_years": 40,
                    "date_naissance_quality_status": "valid",
                    "declaration_count": 6,
                }
            ),
            matches_json="[]",
            declaration_context_json=json.dumps(
                {
                    "interest_count": 3,
                    "asset_count": 3,
                    "latest_interest": {
                        "declaration_uuid": "interest-latest",
                        "date_depot": "2026-06-04",
                        "declaration_type_id": "DI",
                        "declaration_modificative": "true",
                    },
                    "latest_assets": {
                        "declaration_uuid": "assets-latest",
                        "date_depot": "2026-06-04",
                        "declaration_type_id": "DSP",
                        "declaration_modificative": "true",
                    },
                    "history": [
                        {
                            "declaration_uuid": "interest-latest",
                            "declaration_family": "interest",
                            "is_selected": True,
                            "income_row_count": 26,
                        }
                    ],
                }
            ),
            income_json=json.dumps(
                [
                    {
                        "year": 2025,
                        "combined_amount": 120,
                        "sources": [
                            {
                                "source_id": "income-1",
                                "source_kind": "activity",
                                "source_section": "activProfCinqDerniereDto",
                                "label": "Premier ministre",
                                "employer": "Government",
                                "start_date": "09/2025",
                                "end_date": "05/2026",
                                "amount_basis": "Net",
                                "amount": 120,
                                "metric_eligible": False,
                                "review_status": "active",
                            }
                        ],
                    }
                ]
            ),
            assets_json=json.dumps(
                [
                    {
                        "source_id": "asset-1",
                        "kind": "assuranceVieDto",
                        "name": "LECORNU Sébastien",
                        "value": 274,
                        "event_year": 2002,
                        "event_date_raw": "21/01/2002",
                        "event_date": "2002-01-21",
                        "event_precision": "day",
                        "event_source_field": "dateSouscription",
                        "event_kind": "subscription",
                        "age_years": 15,
                        "declared_at": "2026-06-04",
                        "metric_eligible": False,
                        "review_status": "active",
                    }
                ]
            ),
        )
    )

    assert result["person"]["lastName"] == "LECORNU"
    assert result["declarationContext"]["interestCount"] == 3
    assert result["declarationContext"]["latestAssets"]["declarationUuid"] == "assets-latest"
    assert result["declarationContext"]["history"][0]["incomeRows"] == 26
    assert result["incomeByYear"][0]["combinedAmount"] == 120.0
    assert result["incomeByYear"][0]["sources"][0]["metricEligible"] is False
    assert "occupationsByYear" not in result
    assert result["assetInventory"][0]["eventKind"] == "subscription"
    assert result["assetInventory"][0]["ageYears"] == 15
