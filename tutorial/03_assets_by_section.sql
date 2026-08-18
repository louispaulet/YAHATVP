SELECT
  snapshot_date,
  source_section,
  COUNT(*) AS asset_count,
  COUNTIF(normalized_value IS NOT NULL) AS valued_asset_count,
  ROUND(SUM(CAST(normalized_value AS NUMERIC)), 2) AS total_normalized_value_eur,
  ROUND(AVG(CAST(normalized_value AS NUMERIC)), 2) AS average_normalized_value_eur
FROM `yahatvp-pipeline-eu.hatvp.assets`
WHERE snapshot_date = DATE '2026-08-18'
GROUP BY snapshot_date, source_section
ORDER BY total_normalized_value_eur DESC, source_section;
