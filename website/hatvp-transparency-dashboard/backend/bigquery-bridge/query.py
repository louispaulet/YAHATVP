"""Fixed BigQuery aggregation queries for the public dashboard slices."""

from __future__ import annotations

from query_support import TABLES, VIEWS, dataset_prefix, validate_identifier


def build_query(project: str, dataset: str, view: str = "overview") -> str:
    """Build one fixed, latest-snapshot query for an independent dashboard slice."""

    if view not in VIEWS:
        raise ValueError("Invalid dashboard query view")
    prefix = dataset_prefix(project, dataset)
    latest = (
        f"WITH latest AS (SELECT MAX(snapshot_date) AS snapshot_date FROM {prefix}.declarations)\n"
    )
    if view == "overview":
        body = f"""SELECT FORMAT_DATE('%Y-%m-%d', l.snapshot_date) AS snapshot_date,
CURRENT_TIMESTAMP() AS generated_at,
TO_JSON_STRING(ARRAY(
  SELECT AS STRUCT table_name, row_count FROM (
    SELECT 'declarations' AS table_name, COUNT(*) AS row_count FROM {prefix}.declarations t
    CROSS JOIN latest l WHERE t.snapshot_date = l.snapshot_date
    UNION ALL SELECT 'people', COUNT(DISTINCT IF(
      NULLIF(TRIM(t.nom), '') IS NULL AND NULLIF(TRIM(t.prenom), '') IS NULL,
      NULL,
      TO_JSON_STRING(STRUCT(
        NORMALIZE_AND_CASEFOLD(NULLIF(TRIM(t.nom), '')) AS nom,
        NORMALIZE_AND_CASEFOLD(NULLIF(TRIM(t.prenom), '')) AS prenom
      ))
    )) FROM {prefix}.people t
    CROSS JOIN latest l WHERE t.snapshot_date = l.snapshot_date
    UNION ALL SELECT 'incomes', COUNT(*) FROM {prefix}.incomes t
    CROSS JOIN latest l WHERE t.snapshot_date = l.snapshot_date
    UNION ALL SELECT 'assets', COUNT(*) FROM {prefix}.assets t
    CROSS JOIN latest l WHERE t.snapshot_date = l.snapshot_date
  ) ORDER BY table_name
)) AS tables_json FROM latest l"""
    elif view == "income":
        body = f"""SELECT FORMAT_DATE('%Y-%m-%d', l.snapshot_date) AS snapshot_date,
CURRENT_TIMESTAMP() AS generated_at,
TO_JSON_STRING(ARRAY(SELECT AS STRUCT COALESCE(income_stream, 'unknown') AS label,
COUNT(*) AS row_count, COALESCE(SUM(normalized_value), 0) AS total_value
FROM {prefix}.incomes t CROSS JOIN latest l WHERE t.snapshot_date = l.snapshot_date
GROUP BY label ORDER BY total_value DESC, label)) AS items_json,
COALESCE((SELECT SUM(normalized_value) FROM {prefix}.incomes t
WHERE t.snapshot_date = l.snapshot_date), 0) AS total_value,
(SELECT COUNT(DISTINCT income_year) FROM {prefix}.incomes t
WHERE t.snapshot_date = l.snapshot_date) AS year_count
FROM latest l"""
    elif view == "assets":
        body = f"""SELECT FORMAT_DATE('%Y-%m-%d', l.snapshot_date) AS snapshot_date,
CURRENT_TIMESTAMP() AS generated_at,
TO_JSON_STRING(ARRAY(SELECT AS STRUCT COALESCE(source_section, 'unknown') AS label,
COUNT(*) AS row_count, COALESCE(SUM(normalized_value), 0) AS total_value
FROM {prefix}.assets t CROSS JOIN latest l WHERE t.snapshot_date = l.snapshot_date
GROUP BY label ORDER BY total_value DESC, label LIMIT 12)) AS items_json,
COALESCE((SELECT SUM(normalized_value) FROM {prefix}.assets t
WHERE t.snapshot_date = l.snapshot_date), 0) AS total_value
FROM latest l"""
    else:
        body = f"""SELECT FORMAT_DATE('%Y-%m-%d', l.snapshot_date) AS snapshot_date,
CURRENT_TIMESTAMP() AS generated_at,
TO_JSON_STRING(ARRAY(SELECT AS STRUCT COALESCE(declaration_type_label, 'unknown') AS label,
COUNT(*) AS row_count
FROM {prefix}.declarations t CROSS JOIN latest l WHERE t.snapshot_date = l.snapshot_date
GROUP BY label ORDER BY row_count DESC, label LIMIT 12)) AS items_json FROM latest l"""
    return latest + body


__all__ = ["TABLES", "VIEWS", "build_query", "validate_identifier"]
