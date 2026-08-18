import pytest
from query import (
    TABLES,
    VIEWS,
    build_query,
    validate_identifier,
)


def test_query_is_fixed_to_gold_tables_and_latest_snapshot():
    query = build_query("yahatvp-pipeline-eu", "hatvp", "overview")
    for table in TABLES:
        assert f"`yahatvp-pipeline-eu.hatvp`.gold_{table}" in query
    assert "MAX(snapshot_date)" in query
    assert "WHERE t.snapshot_date = l.snapshot_date" in query


def test_query_does_not_select_raw_or_personal_fields():
    query = build_query("project", "dataset", "income")
    assert "raw_record_json" not in query
    assert "adresse_" not in query
    assert "telephone" not in query
    assert "email" not in query


@pytest.mark.parametrize("view", VIEWS)
def test_each_slice_returns_snapshot_metadata_and_one_public_payload(view):
    query = build_query("project", "dataset", view)
    assert "snapshot_date" in query
    assert "generated_at" in query
    assert "tables_json" in query or "items_json" in query


def test_overview_counts_the_four_gold_tables():
    query = build_query("project", "dataset", "overview")
    for table in TABLES:
        assert f"gold_{table} t" in query
    assert query.count("CROSS JOIN latest l") == 4


def test_overview_counts_distinct_people_by_normalized_name_pair():
    query = build_query("project", "dataset", "overview")
    assert "COUNT(DISTINCT IF(" in query
    assert "NORMALIZE_AND_CASEFOLD" in query
    assert "TO_JSON_STRING(STRUCT(" in query
    assert "NULLIF(TRIM(t.nom), '')" in query
    assert "NULLIF(TRIM(t.prenom), '')" in query


def test_income_groups_values_by_stream():
    query = build_query("project", "dataset", "income")
    assert "income_stream" in query
    assert "SUM(normalized_value)" in query
    assert "COUNT(DISTINCT income_year)" in query
    assert "AS year_count" in query
    assert "GROUP BY label" in query


def test_assets_groups_values_by_source_section():
    query = build_query("project", "dataset", "assets")
    assert "source_section" in query
    assert "AS total_value" in query
    assert "LIMIT 12" in query


def test_declarations_groups_values_by_type():
    query = build_query("project", "dataset", "declarations")
    assert "declaration_type_label" in query
    assert "COUNT(*) AS row_count" in query
    assert "ORDER BY row_count DESC, label" in query


@pytest.mark.parametrize("value", ["project.name", "dataset`", "bad space", ""])
def test_identifier_rejects_sql_fragments(value):
    with pytest.raises(ValueError, match="Invalid"):
        validate_identifier(value)


@pytest.mark.parametrize("value", ["project", "project-123", "dataset_123"])
def test_identifier_accepts_google_cloud_names(value):
    assert validate_identifier(value) == value


def test_unknown_view_is_rejected():
    with pytest.raises(ValueError, match="Invalid"):
        build_query("project", "dataset", "unknown")


def test_query_is_deterministic():
    assert build_query("p", "d", "assets") == build_query("p", "d", "assets")
