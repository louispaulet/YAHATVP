"""Fixed BigQuery aggregation query for the public dashboard."""

from __future__ import annotations

import re

TABLES = ("declarations", "people", "incomes", "assets")
IDENTIFIER = re.compile(r"^[A-Za-z0-9_-]+$")


def validate_identifier(value: str) -> str:
    """Allow only project and dataset identifiers supplied by deployment config."""

    if not IDENTIFIER.fullmatch(value):
        raise ValueError("Invalid BigQuery project or dataset identifier")
    return value


def build_query(project: str, dataset: str) -> str:
    """Build one parameter-free query over the latest shared source snapshot."""

    prefix = f"`{validate_identifier(project)}.{validate_identifier(dataset)}`"
    return f"""
WITH latest AS (
  SELECT MAX(snapshot_date) AS snapshot_date FROM {prefix}.declarations
),
table_counts AS (
  SELECT 'declarations' AS table_name, COUNT(*) AS row_count
  FROM {prefix}.declarations AS t CROSS JOIN latest AS l
  WHERE t.snapshot_date = l.snapshot_date
  UNION ALL
  SELECT 'people', COUNT(*)
  FROM {prefix}.people AS t CROSS JOIN latest AS l
  WHERE t.snapshot_date = l.snapshot_date
  UNION ALL
  SELECT 'incomes', COUNT(*)
  FROM {prefix}.incomes AS t CROSS JOIN latest AS l
  WHERE t.snapshot_date = l.snapshot_date
  UNION ALL
  SELECT 'assets', COUNT(*)
  FROM {prefix}.assets AS t CROSS JOIN latest AS l
  WHERE t.snapshot_date = l.snapshot_date
),
income_breakdown AS (
  SELECT COALESCE(t.income_stream, 'unknown') AS label,
         COUNT(*) AS row_count,
         COALESCE(SUM(t.normalized_value), 0) AS total_value
  FROM {prefix}.incomes AS t CROSS JOIN latest AS l
  WHERE t.snapshot_date = l.snapshot_date
  GROUP BY label
),
asset_breakdown AS (
  SELECT COALESCE(t.source_section, 'unknown') AS label,
         COUNT(*) AS row_count,
         COALESCE(SUM(t.normalized_value), 0) AS total_value
  FROM {prefix}.assets AS t CROSS JOIN latest AS l
  WHERE t.snapshot_date = l.snapshot_date
  GROUP BY label
),
declaration_breakdown AS (
  SELECT COALESCE(t.declaration_type_label, 'unknown') AS label,
         COUNT(*) AS row_count
  FROM {prefix}.declarations AS t CROSS JOIN latest AS l
  WHERE t.snapshot_date = l.snapshot_date
  GROUP BY label
)
SELECT
  FORMAT_DATE('%Y-%m-%d', latest.snapshot_date) AS snapshot_date,
  CURRENT_TIMESTAMP() AS generated_at,
  TO_JSON_STRING(
    ARRAY(SELECT AS STRUCT table_name, row_count FROM table_counts ORDER BY table_name)
  ) AS tables_json,
  TO_JSON_STRING(
    ARRAY(SELECT AS STRUCT label, row_count, total_value FROM income_breakdown
          ORDER BY total_value DESC, label)
  ) AS income_json,
  TO_JSON_STRING(
    ARRAY(SELECT AS STRUCT label, row_count, total_value FROM asset_breakdown
          ORDER BY total_value DESC, label LIMIT 12)
  ) AS assets_json,
  TO_JSON_STRING(
    ARRAY(SELECT AS STRUCT label, row_count FROM declaration_breakdown
          ORDER BY rows DESC, label LIMIT 12)
  ) AS declaration_json
FROM latest
"""
