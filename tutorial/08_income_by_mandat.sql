WITH declaration_labels AS (
  SELECT
    snapshot_date,
    declaration_uuid,
    ANY_VALUE(mandat_label) AS mandat_label
  FROM `yahatvp-pipeline-eu.hatvp.declarations`
  WHERE snapshot_date = DATE '2026-08-18'
  GROUP BY snapshot_date, declaration_uuid
), income_by_declaration AS (
  SELECT
    snapshot_date,
    declaration_uuid,
    COUNT(*) AS income_row_count,
    SUM(CAST(normalized_value AS NUMERIC)) AS total_income_eur
  FROM `yahatvp-pipeline-eu.hatvp.incomes`
  WHERE snapshot_date = DATE '2026-08-18'
  GROUP BY snapshot_date, declaration_uuid
)
SELECT
  d.snapshot_date,
  COALESCE(d.mandat_label, '<NULL>') AS mandat_label,
  COUNT(*) AS declarations_with_income,
  SUM(i.income_row_count) AS income_row_count,
  ROUND(SUM(i.total_income_eur), 2) AS total_income_eur,
  ROUND(AVG(i.total_income_eur), 2) AS average_income_per_declaration_eur,
  ROUND(MAX(i.total_income_eur), 2) AS max_income_per_declaration_eur
FROM declaration_labels AS d
JOIN income_by_declaration AS i USING (snapshot_date, declaration_uuid)
GROUP BY d.snapshot_date, mandat_label
HAVING COUNT(*) >= 5
ORDER BY total_income_eur DESC, mandat_label
LIMIT 20;
