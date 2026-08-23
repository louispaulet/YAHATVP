"""BigQuery health summary for the public pipeline-status page."""

from __future__ import annotations

from query_support import dataset_prefix


def build_health_query(project: str, dataset: str) -> str:
    """Return one query covering current layers, sources, and registry status."""

    prefix = dataset_prefix(project, dataset)
    return f"""
WITH latest AS (
  SELECT MAX(snapshot_date) AS snapshot_date FROM {prefix}.gold_declarations
),
layer_rows AS (
  SELECT 'bronze' AS layer, SUM(row_count) AS row_count, 0 AS review_rows FROM (
    SELECT COUNT(*) row_count
    FROM {prefix}.declarations t CROSS JOIN latest l
    WHERE t.snapshot_date = l.snapshot_date
    UNION ALL SELECT COUNT(*)
    FROM {prefix}.people t CROSS JOIN latest l
    WHERE t.snapshot_date = l.snapshot_date
    UNION ALL SELECT COUNT(*)
    FROM {prefix}.incomes t CROSS JOIN latest l
    WHERE t.snapshot_date = l.snapshot_date
    UNION ALL SELECT COUNT(*)
    FROM {prefix}.assets t CROSS JOIN latest l
    WHERE t.snapshot_date = l.snapshot_date
  )
  UNION ALL
  SELECT 'silver', SUM(row_count), SUM(review_rows) FROM (
    SELECT COUNT(*) row_count, COUNTIF(t.anomaly_active) review_rows
    FROM {prefix}.silver_declarations t CROSS JOIN latest l
    WHERE t.snapshot_date = l.snapshot_date
    UNION ALL SELECT COUNT(*), COUNTIF(t.anomaly_active)
    FROM {prefix}.silver_people t CROSS JOIN latest l
    WHERE t.snapshot_date = l.snapshot_date
    UNION ALL SELECT COUNT(*), COUNTIF(t.anomaly_active)
    FROM {prefix}.silver_incomes t CROSS JOIN latest l
    WHERE t.snapshot_date = l.snapshot_date
    UNION ALL SELECT COUNT(*), COUNTIF(t.anomaly_active)
    FROM {prefix}.silver_assets t CROSS JOIN latest l
    WHERE t.snapshot_date = l.snapshot_date
  )
  UNION ALL
  SELECT 'gold', SUM(row_count), SUM(review_rows) FROM (
    SELECT COUNT(*) row_count, COUNTIF(t.anomaly_active) review_rows
    FROM {prefix}.gold_declarations t CROSS JOIN latest l
    WHERE t.snapshot_date = l.snapshot_date
    UNION ALL SELECT COUNT(*), COUNTIF(t.anomaly_active)
    FROM {prefix}.gold_people t CROSS JOIN latest l
    WHERE t.snapshot_date = l.snapshot_date
    UNION ALL SELECT COUNT(*), COUNTIF(t.anomaly_active)
    FROM {prefix}.gold_incomes t CROSS JOIN latest l
    WHERE t.snapshot_date = l.snapshot_date
    UNION ALL SELECT COUNT(*), COUNTIF(t.anomaly_active)
    FROM {prefix}.gold_assets t CROSS JOIN latest l
    WHERE t.snapshot_date = l.snapshot_date
  )
),
deduplicated_source_rows AS (
  SELECT COALESCE(t.ingestion_source, 'unknown') AS source_id,
         COUNT(DISTINCT t.declaration_uuid) AS declaration_count
  FROM {prefix}.gold_declarations t CROSS JOIN latest l
  WHERE t.snapshot_date = l.snapshot_date
  GROUP BY source_id
),
raw_source_rows AS (
  SELECT COALESCE(t.ingestion_source, 'unknown') AS source_id,
         COUNT(*) AS raw_declaration_count
  FROM {prefix}.declarations t CROSS JOIN latest l
  WHERE t.snapshot_date = l.snapshot_date
  GROUP BY source_id
),
source_rows AS (
  SELECT COALESCE(d.source_id, r.source_id) AS source_id,
         COALESCE(d.declaration_count, 0) AS declaration_count,
         COALESCE(r.raw_declaration_count, 0) AS raw_declaration_count
  FROM deduplicated_source_rows d
  FULL OUTER JOIN raw_source_rows r USING (source_id)
),
anomaly_rows AS (
  SELECT COALESCE(status, 'unknown') AS status, COUNT(*) AS row_count
  FROM {prefix}.anomaly_registry t CROSS JOIN latest l
  WHERE t.snapshot_date = l.snapshot_date
  GROUP BY status
),
anomaly_categories AS (
  SELECT COALESCE(NULLIF(t.rule_id, ''), 'unknown') AS category, COUNT(*) AS row_count
  FROM {prefix}.anomaly_registry t CROSS JOIN latest l
  WHERE t.snapshot_date = l.snapshot_date
    AND COALESCE(NULLIF(t.rule_id, ''), 'unknown') NOT IN ('ANOMALY_KNOWN', 'ANOMALY_REGRESSION')
  GROUP BY category
)
SELECT latest.snapshot_date,
       CURRENT_TIMESTAMP() AS generated_at,
       TO_JSON_STRING((SELECT ARRAY_AGG(STRUCT(layer, row_count, review_rows)
         ORDER BY layer) FROM layer_rows)) AS layers_json,
       TO_JSON_STRING((SELECT ARRAY_AGG(STRUCT(source_id, declaration_count, raw_declaration_count)
         ORDER BY source_id) FROM source_rows)) AS sources_json,
       TO_JSON_STRING((SELECT ARRAY_AGG(STRUCT(status, row_count)
         ORDER BY status) FROM anomaly_rows)) AS anomalies_json,
       TO_JSON_STRING((SELECT ARRAY_AGG(STRUCT(category, row_count)
         ORDER BY row_count DESC, category LIMIT 5)
         FROM anomaly_categories)) AS anomaly_categories_json
FROM latest
"""


__all__ = ["build_health_query"]
