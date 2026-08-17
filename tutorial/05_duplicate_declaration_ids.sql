SELECT
  snapshot_date,
  declaration_uuid,
  COUNT(*) AS declaration_row_count,
  COUNT(DISTINCT declaration_version) AS version_count,
  MIN(date_depot) AS first_deposit_date,
  MAX(date_depot) AS last_deposit_date
FROM `yahatvp-pipeline-eu.hatvp.declarations`
WHERE snapshot_date = DATE '2026-08-18'
GROUP BY snapshot_date, declaration_uuid
HAVING COUNT(*) > 1
ORDER BY declaration_row_count DESC, declaration_uuid;
