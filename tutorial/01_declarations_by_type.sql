SELECT
  snapshot_date,
  COALESCE(declaration_type_label, '<NULL>') AS declaration_type,
  COUNT(*) AS declaration_count
FROM `yahatvp-pipeline-eu.hatvp.declarations`
WHERE snapshot_date = DATE '2026-08-18'
GROUP BY snapshot_date, declaration_type
ORDER BY declaration_count DESC, declaration_type;
