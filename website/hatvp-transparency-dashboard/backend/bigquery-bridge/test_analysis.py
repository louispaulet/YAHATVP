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


def test_age_analysis_query_is_parameterized_and_includes_all_three_timelines():
    query = build_age_analysis_query("project", "dataset")

    assert "@search_term" in query
    assert "income_by_year" in query
    assert "occupations_by_year" in query
    assert "asset_acquisition_year" in query
    assert "EXTRACT(YEAR FROM sp.date_naissance_date)" in query
    assert "sp.date_naissance_year" not in query
    assert "raw_record_json" not in query
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


def test_age_analysis_payload_maps_sources_occupations_and_assets():
    result = age_analysis_payload(
        row(
            snapshot_date="2026-08-19",
            generated_at="now",
            person_json=json.dumps(
                {
                    "person_key": "sebastien|lecornu|1976-06-11",
                    "primary_uuid": "uuid",
                    "prenom": "Sébastien",
                    "nom": "LECORNU",
                    "date_naissance": "1976-06-11",
                    "age_years": 50,
                    "date_naissance_quality_status": "valid",
                    "declaration_count": 4,
                }
            ),
            matches_json="[]",
            income_json=json.dumps(
                [
                    {
                        "year": 2025,
                        "combined_amount": 120,
                        "sources": [
                            {"source_label": "source", "income_label": "salary", "amount": 120}
                        ],
                    }
                ]
            ),
            occupations_json=json.dumps(
                [
                    {
                        "year": 2025,
                        "occupation_count": 1,
                        "occupations": [
                            {"label": "Minister", "source": "Government", "row_count": 1}
                        ],
                    }
                ]
            ),
            assets_json=json.dumps(
                [
                    {
                        "year": 2007,
                        "relative_age": 30,
                        "assets": [
                            {
                                "source_section": "immeubleDto",
                                "asset_name": "House",
                                "normalized_value": 770000,
                            }
                        ],
                    }
                ]
            ),
        )
    )

    assert result["person"]["lastName"] == "LECORNU"
    assert result["incomeByYear"][0]["combinedAmount"] == 120.0
    assert result["occupationsByYear"][0]["occupations"][0]["label"] == "Minister"
    assert result["assetTimeline"][0]["relativeAge"] == 30
