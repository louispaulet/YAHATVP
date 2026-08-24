"""Fixed BigQuery aggregation queries for the public dashboard slices."""

from __future__ import annotations

from query_support import TABLES, VIEWS, dataset_prefix, table, validate_identifier


def build_query(project: str, dataset: str, view: str = "overview") -> str:
    """Build one fixed, latest-snapshot query for an independent dashboard slice."""

    if view not in VIEWS:
        raise ValueError("Invalid dashboard query view")
    prefix = dataset_prefix(project, dataset)
    declarations = table(prefix, "declarations")
    people = table(prefix, "people")
    incomes = table(prefix, "incomes")
    assets = table(prefix, "assets")
    latest = f"WITH latest AS (SELECT MAX(snapshot_date) AS snapshot_date FROM {declarations})\n"
    if view == "overview":
        body = f"""SELECT FORMAT_DATE('%Y-%m-%d', l.snapshot_date) AS snapshot_date,
CURRENT_TIMESTAMP() AS generated_at,
TO_JSON_STRING(ARRAY(
  SELECT AS STRUCT table_name, row_count FROM (
    SELECT 'declarations' AS table_name, COUNT(*) AS row_count FROM {declarations} t
    CROSS JOIN latest l WHERE t.snapshot_date = l.snapshot_date
    UNION ALL SELECT 'people', COUNT(DISTINCT IF(
      NULLIF(TRIM(t.nom), '') IS NULL AND NULLIF(TRIM(t.prenom), '') IS NULL,
      NULL,
      TO_JSON_STRING(STRUCT(
        NORMALIZE_AND_CASEFOLD(NULLIF(TRIM(t.nom), '')) AS nom,
        NORMALIZE_AND_CASEFOLD(NULLIF(TRIM(t.prenom), '')) AS prenom
      ))
    )) FROM {people} t
    CROSS JOIN latest l WHERE t.snapshot_date = l.snapshot_date
    UNION ALL SELECT 'incomes', COUNT(*) FROM {incomes} t
    CROSS JOIN latest l WHERE t.snapshot_date = l.snapshot_date
      AND COALESCE(t.metric_eligible, TRUE) AND t.normalized_value IS NOT NULL
    UNION ALL SELECT 'assets', COUNT(*) FROM {assets} t
    CROSS JOIN latest l WHERE t.snapshot_date = l.snapshot_date
      AND COALESCE(t.metric_eligible, TRUE) AND t.normalized_value IS NOT NULL
  ) ORDER BY table_name
)) AS tables_json FROM latest l"""
    elif view == "income":
        body = f"""SELECT FORMAT_DATE('%Y-%m-%d', l.snapshot_date) AS snapshot_date,
CURRENT_TIMESTAMP() AS generated_at,
TO_JSON_STRING(ARRAY(SELECT AS STRUCT COALESCE(income_stream, 'unknown') AS label,
COUNT(*) AS row_count, COALESCE(SUM(normalized_value), 0) AS total_value
FROM {incomes} t CROSS JOIN latest l WHERE t.snapshot_date = l.snapshot_date
  AND COALESCE(t.metric_eligible, TRUE) AND t.normalized_value IS NOT NULL
GROUP BY label ORDER BY total_value DESC, label)) AS items_json,
COALESCE((SELECT SUM(normalized_value) FROM {incomes} t
WHERE t.snapshot_date = l.snapshot_date
  AND COALESCE(t.metric_eligible, TRUE) AND t.normalized_value IS NOT NULL), 0) AS total_value,
(SELECT COUNT(DISTINCT income_year) FROM {incomes} t
WHERE t.snapshot_date = l.snapshot_date
  AND COALESCE(t.metric_eligible, TRUE) AND t.normalized_value IS NOT NULL) AS year_count
FROM latest l"""
    elif view == "assets":
        body = f"""SELECT FORMAT_DATE('%Y-%m-%d', l.snapshot_date) AS snapshot_date,
CURRENT_TIMESTAMP() AS generated_at,
TO_JSON_STRING(ARRAY(SELECT AS STRUCT COALESCE(source_section, 'unknown') AS label,
COUNT(*) AS row_count, COALESCE(SUM(normalized_value), 0) AS total_value
FROM {assets} t CROSS JOIN latest l WHERE t.snapshot_date = l.snapshot_date
  AND COALESCE(t.metric_eligible, TRUE) AND t.normalized_value IS NOT NULL
GROUP BY label ORDER BY total_value DESC, label LIMIT 12)) AS items_json,
COALESCE((SELECT SUM(normalized_value) FROM {assets} t
WHERE t.snapshot_date = l.snapshot_date
  AND COALESCE(t.metric_eligible, TRUE) AND t.normalized_value IS NOT NULL), 0) AS total_value
FROM latest l"""
    elif view == "gender":
        body = f"""SELECT FORMAT_DATE('%Y-%m-%d', l.snapshot_date) AS snapshot_date,
CURRENT_TIMESTAMP() AS generated_at,
TO_JSON_STRING(ARRAY(
  SELECT AS STRUCT label, row_count FROM (
    SELECT COALESCE(NULLIF(p.gender, ''), 'unknown') AS label, COUNT(*) AS row_count
    FROM {people} p CROSS JOIN latest l
    WHERE p.snapshot_date = l.snapshot_date
    GROUP BY label
  ) ORDER BY CASE label WHEN 'male' THEN 1 WHEN 'female' THEN 2 ELSE 3 END, label
)) AS gender_json,
TO_JSON_STRING(ARRAY(
  SELECT AS STRUCT label, male_count, female_count, unknown_count FROM (
    SELECT COALESCE(NULLIF(d.mandat_label, ''), NULLIF(d.mandat_type_label, ''),
      'unknown') AS label,
      COUNTIF(p.gender = 'male') AS male_count,
      COUNTIF(p.gender = 'female') AS female_count,
      COUNTIF(p.gender IS NULL OR p.gender NOT IN ('male', 'female')) AS unknown_count
    FROM {declarations} d
    LEFT JOIN {people} p ON p.declaration_uuid = d.declaration_uuid
      AND p.snapshot_date = d.snapshot_date
    CROSS JOIN latest l
    WHERE d.snapshot_date = l.snapshot_date
    GROUP BY label
    HAVING COUNTIF(p.gender = 'male') + COUNTIF(p.gender = 'female') > 0
  ) ORDER BY male_count + female_count DESC, label LIMIT 10
)) AS positions_json
FROM latest l"""
    else:
        body = f"""SELECT FORMAT_DATE('%Y-%m-%d', l.snapshot_date) AS snapshot_date,
CURRENT_TIMESTAMP() AS generated_at,
TO_JSON_STRING(ARRAY(SELECT AS STRUCT COALESCE(declaration_type_label, 'unknown') AS label,
COUNT(*) AS row_count
FROM {declarations} t CROSS JOIN latest l WHERE t.snapshot_date = l.snapshot_date
GROUP BY label ORDER BY row_count DESC, label LIMIT 12)) AS items_json FROM latest l"""
    return latest + body


__all__ = ["TABLES", "VIEWS", "build_query", "validate_identifier"]
