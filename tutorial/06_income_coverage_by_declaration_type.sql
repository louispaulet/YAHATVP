WITH income_by_declaration AS (
  SELECT
    declaration_uuid,
    COUNT(*) AS income_row_count
  FROM `yahatvp-pipeline-eu.hatvp.incomes`
  WHERE snapshot_date = DATE '2026-08-18'
  GROUP BY declaration_uuid
)
SELECT
  d.snapshot_date,
  COALESCE(d.declaration_type_label, '<NULL>') AS declaration_type,
  COUNT(DISTINCT d.declaration_uuid) AS declaration_count,
  COUNT(DISTINCT IF(d.income_section_present, d.declaration_uuid, NULL)) AS declarations_with_income_section,
  COUNT(DISTINCT IF(i.income_row_count IS NOT NULL, d.declaration_uuid, NULL)) AS declarations_with_numeric_income,
  ROUND(
    100 * SAFE_DIVIDE(
      COUNT(DISTINCT IF(i.income_row_count IS NOT NULL, d.declaration_uuid, NULL)),
      COUNT(DISTINCT d.declaration_uuid)
    ),
    2
  ) AS numeric_income_coverage_pct
FROM `yahatvp-pipeline-eu.hatvp.declarations` AS d
LEFT JOIN income_by_declaration AS i USING (declaration_uuid)
WHERE d.snapshot_date = DATE '2026-08-18'
GROUP BY d.snapshot_date, declaration_type
ORDER BY declaration_count DESC, declaration_type;
