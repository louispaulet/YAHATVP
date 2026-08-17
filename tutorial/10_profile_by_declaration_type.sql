WITH declaration_dim AS (
  SELECT
    snapshot_date,
    declaration_uuid,
    ANY_VALUE(declaration_type_label) AS declaration_type
  FROM `yahatvp-pipeline-eu.hatvp.declarations`
  WHERE snapshot_date = DATE '2026-08-18'
  GROUP BY snapshot_date, declaration_uuid
), people_by_declaration AS (
  SELECT snapshot_date, declaration_uuid
  FROM `yahatvp-pipeline-eu.hatvp.people`
  WHERE snapshot_date = DATE '2026-08-18'
  GROUP BY snapshot_date, declaration_uuid
), income_by_declaration AS (
  SELECT
    snapshot_date,
    declaration_uuid,
    SUM(CAST(normalized_value AS NUMERIC)) AS total_income_eur
  FROM `yahatvp-pipeline-eu.hatvp.incomes`
  WHERE snapshot_date = DATE '2026-08-18'
  GROUP BY snapshot_date, declaration_uuid
), asset_by_declaration AS (
  SELECT
    snapshot_date,
    declaration_uuid,
    SUM(CAST(normalized_value AS NUMERIC)) AS total_asset_value_eur
  FROM `yahatvp-pipeline-eu.hatvp.assets`
  WHERE snapshot_date = DATE '2026-08-18'
  GROUP BY snapshot_date, declaration_uuid
)
SELECT
  d.snapshot_date,
  d.declaration_type,
  COUNT(*) AS declaration_count,
  COUNTIF(p.declaration_uuid IS NOT NULL) AS declarations_with_people,
  COUNTIF(i.declaration_uuid IS NOT NULL) AS declarations_with_income,
  COUNTIF(a.declaration_uuid IS NOT NULL) AS declarations_with_assets,
  ROUND(100 * SAFE_DIVIDE(COUNTIF(i.declaration_uuid IS NOT NULL), COUNT(*)), 2) AS income_coverage_pct,
  ROUND(100 * SAFE_DIVIDE(COUNTIF(a.declaration_uuid IS NOT NULL), COUNT(*)), 2) AS asset_coverage_pct,
  ROUND(SUM(COALESCE(i.total_income_eur, 0)), 2) AS total_income_eur,
  ROUND(SUM(COALESCE(a.total_asset_value_eur, 0)), 2) AS total_asset_value_eur
FROM declaration_dim AS d
LEFT JOIN people_by_declaration AS p USING (snapshot_date, declaration_uuid)
LEFT JOIN income_by_declaration AS i USING (snapshot_date, declaration_uuid)
LEFT JOIN asset_by_declaration AS a USING (snapshot_date, declaration_uuid)
GROUP BY d.snapshot_date, d.declaration_type
ORDER BY declaration_count DESC, d.declaration_type;
