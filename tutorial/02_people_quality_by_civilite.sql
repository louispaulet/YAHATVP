SELECT
  snapshot_date,
  COALESCE(NULLIF(TRIM(civilite), ''), '<UNKNOWN>') AS civilite,
  COUNT(*) AS people_row_count,
  COUNTIF(quality_status = 'FLAG') AS flagged_row_count,
  ROUND(100 * SAFE_DIVIDE(COUNTIF(quality_status = 'FLAG'), COUNT(*)), 2) AS flagged_row_pct
FROM `yahatvp-pipeline-eu.hatvp.people`
WHERE snapshot_date = DATE '2026-08-18'
GROUP BY snapshot_date, civilite
ORDER BY people_row_count DESC, civilite;
