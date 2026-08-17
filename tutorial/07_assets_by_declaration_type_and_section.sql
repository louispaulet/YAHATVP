WITH declaration_labels AS (
  SELECT
    snapshot_date,
    declaration_uuid,
    ANY_VALUE(declaration_type_label) AS declaration_type
  FROM `yahatvp-pipeline-eu.hatvp.declarations`
  WHERE snapshot_date = DATE '2026-08-18'
  GROUP BY snapshot_date, declaration_uuid
)
SELECT
  a.snapshot_date,
  d.declaration_type,
  a.source_section,
  COUNT(*) AS asset_count,
  COUNT(DISTINCT a.declaration_uuid) AS declaration_count,
  ROUND(SUM(CAST(a.normalized_value AS NUMERIC)), 2) AS total_asset_value_eur
FROM `yahatvp-pipeline-eu.hatvp.assets` AS a
JOIN declaration_labels AS d USING (snapshot_date, declaration_uuid)
WHERE a.snapshot_date = DATE '2026-08-18'
GROUP BY a.snapshot_date, d.declaration_type, a.source_section
ORDER BY total_asset_value_eur DESC, d.declaration_type, a.source_section
LIMIT 20;
