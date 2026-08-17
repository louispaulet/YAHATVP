WITH declaration_labels AS (
  SELECT
    snapshot_date,
    declaration_uuid,
    ANY_VALUE(declaration_type_label) AS declaration_type
  FROM `yahatvp-pipeline-eu.hatvp.declarations`
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
  d.declaration_uuid,
  d.declaration_type,
  ROUND(i.total_income_eur, 2) AS total_income_eur,
  ROUND(a.total_asset_value_eur, 2) AS total_asset_value_eur,
  ROUND(SAFE_DIVIDE(i.total_income_eur, a.total_asset_value_eur), 4) AS income_to_asset_ratio
FROM declaration_labels AS d
JOIN income_by_declaration AS i USING (snapshot_date, declaration_uuid)
JOIN asset_by_declaration AS a USING (snapshot_date, declaration_uuid)
WHERE a.total_asset_value_eur > 0
ORDER BY a.total_asset_value_eur DESC, d.declaration_uuid
LIMIT 20;
