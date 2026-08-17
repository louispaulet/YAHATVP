import pytest
from query import TABLES, build_query, validate_identifier


def test_query_is_fixed_to_curated_tables_and_latest_snapshot():
    query = build_query("yahatvp-pipeline-eu", "hatvp")
    for table in TABLES:
        assert f"`yahatvp-pipeline-eu.hatvp`.{table}" in query
    assert "MAX(snapshot_date)" in query
    assert "WHERE t.snapshot_date = l.snapshot_date" in query


def test_query_does_not_select_raw_or_personal_fields():
    query = build_query("project", "dataset")
    assert "raw_record_json" not in query
    assert "adresse_" not in query
    assert "telephone" not in query
    assert "email" not in query


def test_query_returns_json_aggregate_columns():
    query = build_query("project", "dataset")
    assert "tables_json" in query
    assert "income_json" in query
    assert "assets_json" in query
    assert "declaration_json" in query


def test_query_uses_the_latest_snapshot_for_each_table():
    query = build_query("project", "dataset")
    assert query.count("MAX(snapshot_date)") == 1
    assert query.count("CROSS JOIN latest AS l") == 7
    assert query.count("t.snapshot_date = l.snapshot_date") == 7


def test_query_groups_income_values_by_stream():
    query = build_query("project", "dataset")
    assert "income_stream" in query
    assert "SUM(t.normalized_value)" in query
    assert "GROUP BY label" in query


def test_query_groups_asset_values_by_source_section():
    query = build_query("project", "dataset")
    assert "source_section" in query
    assert "asset_breakdown" in query


def test_query_groups_declarations_by_type():
    query = build_query("project", "dataset")
    assert "declaration_type_label" in query
    assert "COUNT(*) AS row_count" in query
    assert "ORDER BY row_count DESC, label" in query


def test_query_limits_public_breakdowns():
    query = build_query("project", "dataset")
    assert "asset_breakdown" in query
    assert "declaration_breakdown" in query
    assert "LIMIT 12" in query
    assert "ORDER BY total_value DESC" in query


@pytest.mark.parametrize("value", ["project.name", "dataset`", "bad space", ""])
def test_identifier_rejects_sql_fragments(value):
    with pytest.raises(ValueError, match="Invalid"):
        validate_identifier(value)


@pytest.mark.parametrize("value", ["project", "project-123", "dataset_123"])
def test_identifier_accepts_google_cloud_names(value):
    assert validate_identifier(value) == value


def test_table_contract_is_deterministic():
    assert TABLES == ("declarations", "people", "incomes", "assets")
    assert build_query("p", "d") == build_query("p", "d")
