SELECT
  snapshot_date,
  income_stream,
  COUNT(*) AS income_row_count,
  COUNT(DISTINCT declaration_uuid) AS declaration_count,
  ROUND(SUM(CAST(normalized_value AS NUMERIC)), 2) AS total_income_eur,
  ROUND(AVG(CAST(normalized_value AS NUMERIC)), 2) AS average_income_eur,
  MIN(income_year) AS earliest_income_year,
  MAX(income_year) AS latest_income_year
FROM `yahatvp-pipeline-eu.hatvp.incomes`
WHERE snapshot_date = DATE '2026-08-18'
GROUP BY snapshot_date, income_stream
ORDER BY total_income_eur DESC, income_stream;
