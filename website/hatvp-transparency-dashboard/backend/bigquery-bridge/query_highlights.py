"""Fixed BigQuery query for source-linked editorial highlights."""

from __future__ import annotations

from query_support import accent_fold, dataset_prefix


def build_highlights_query(project: str, dataset: str) -> str:
    """Build a latest-snapshot query for three explainable public highlights."""

    prefix = dataset_prefix(project, dataset)
    gold_declarations = f"{prefix}.gold_declarations"
    gold_people = f"{prefix}.gold_people"
    gold_incomes = f"{prefix}.gold_incomes"
    gold_assets = f"{prefix}.gold_assets"
    silver_declarations = f"{prefix}.silver_declarations"
    silver_people = f"{prefix}.silver_people"
    return f"""WITH latest AS (
  SELECT MAX(snapshot_date) AS snapshot_date FROM {gold_declarations}
), people AS (
  SELECT declaration_uuid, prenom, nom, date_naissance_date
  FROM {gold_people} p CROSS JOIN latest l
  WHERE p.snapshot_date = l.snapshot_date
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY declaration_uuid ORDER BY bronze_record_key DESC
  ) = 1
), declarations AS (
  SELECT declaration_uuid, mandat_label, date_depot
  FROM {gold_declarations} d CROSS JOIN latest l
  WHERE d.snapshot_date = l.snapshot_date
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY declaration_uuid ORDER BY date_depot DESC, bronze_record_key DESC
  ) = 1
), annual_income AS (
  SELECT i.declaration_uuid, SAFE_CAST(i.income_year AS INT64) AS income_year,
    SUM(i.normalized_value) AS amount,
    COUNTIF(NOT COALESCE(i.metric_eligible, TRUE) OR COALESCE(i.anomaly_active, FALSE)) > 0
      AS review_required
  FROM {gold_incomes} i CROSS JOIN latest l
  WHERE i.snapshot_date = l.snapshot_date
    AND i.normalized_value IS NOT NULL
    AND SAFE_CAST(i.income_year AS INT64) < EXTRACT(YEAR FROM l.snapshot_date)
  GROUP BY i.declaration_uuid, income_year
), income_history AS (
  SELECT *, LAG(income_year) OVER w AS previous_year,
    LAG(amount) OVER w AS previous_amount,
    LAG(review_required) OVER w AS previous_review_required
  FROM annual_income WINDOW w AS (PARTITION BY declaration_uuid ORDER BY income_year)
), income_changes AS (
  SELECT h.declaration_uuid, p.prenom, p.nom, d.mandat_label,
    h.previous_year, h.income_year, h.previous_amount, h.amount,
    h.amount - h.previous_amount AS absolute_change,
    SAFE_DIVIDE(h.amount, NULLIF(h.previous_amount, 0)) AS ratio,
    h.review_required OR h.previous_review_required AS review_required
  FROM income_history h JOIN people p USING (declaration_uuid)
  LEFT JOIN declarations d USING (declaration_uuid)
  WHERE h.previous_year = h.income_year - 1
    AND h.previous_amount IS NOT NULL
  ORDER BY ABS(absolute_change) DESC, h.declaration_uuid
  LIMIT 8
), unusual_assets AS (
  SELECT a.declaration_uuid, p.prenom, p.nom, d.mandat_label,
    a.source_section, a.asset_name, a.raw_value, a.normalized_value,
    a.anomaly_status,
    NOT COALESCE(a.metric_eligible, TRUE) OR COALESCE(a.anomaly_active, FALSE)
      AS review_required
  FROM {gold_assets} a CROSS JOIN latest l
  JOIN people p USING (declaration_uuid)
  LEFT JOIN declarations d USING (declaration_uuid)
  WHERE a.snapshot_date = l.snapshot_date AND a.normalized_value IS NOT NULL
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY {accent_fold("COALESCE(p.prenom, '')")},
      {accent_fold("COALESCE(p.nom, '')")},
      COALESCE(CAST(p.date_naissance_date AS STRING), p.declaration_uuid),
      a.source_section, a.asset_name,
      CAST(a.normalized_value AS STRING)
    ORDER BY d.date_depot DESC, a.declaration_uuid
  ) = 1
  ORDER BY ABS(a.normalized_value) DESC, a.declaration_uuid
  LIMIT 8
), silver_filings AS (
  SELECT CONCAT({accent_fold("COALESCE(p.prenom, '')")}, '|',
      {accent_fold("COALESCE(p.nom, '')")}, '|',
      CAST(p.date_naissance_date AS STRING)) AS person_key,
    d.declaration_uuid, d.date_depot,
    d.declaration_modificative, d.mandat_label, p.prenom, p.nom
  FROM {silver_declarations} d
  JOIN {silver_people} p USING (snapshot_date, bronze_record_key, declaration_uuid)
  CROSS JOIN latest l
  WHERE d.snapshot_date = l.snapshot_date
    AND p.date_naissance_date IS NOT NULL
    AND (NULLIF(TRIM(p.prenom), '') IS NOT NULL OR NULLIF(TRIM(p.nom), '') IS NOT NULL)
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY d.declaration_uuid ORDER BY d.date_depot DESC, d.bronze_record_key DESC
  ) = 1
), amended_records AS (
  SELECT person_key, ANY_VALUE(prenom) AS prenom, ANY_VALUE(nom) AS nom,
    COUNT(*) AS filing_count,
    COUNTIF(LOWER(COALESCE(declaration_modificative, 'false')) IN ('true', '1', 'oui'))
      AS amended_count,
    MIN(date_depot) AS first_filed, MAX(date_depot) AS latest_filed,
    ARRAY_AGG(declaration_uuid ORDER BY date_depot DESC, declaration_uuid DESC LIMIT 1)[OFFSET(0)]
      AS declaration_uuid,
    ARRAY_AGG(mandat_label IGNORE NULLS ORDER BY date_depot DESC LIMIT 1)[SAFE_OFFSET(0)]
      AS mandat_label
  FROM silver_filings
  GROUP BY person_key
  HAVING amended_count > 0
  ORDER BY amended_count DESC, filing_count DESC, person_key
  LIMIT 8
)
SELECT FORMAT_DATE('%Y-%m-%d', l.snapshot_date) AS snapshot_date,
  CURRENT_TIMESTAMP() AS generated_at,
  TO_JSON_STRING(ARRAY(SELECT AS STRUCT * FROM income_changes)) AS income_changes_json,
  TO_JSON_STRING(ARRAY(SELECT AS STRUCT * FROM unusual_assets)) AS unusual_assets_json,
  TO_JSON_STRING(ARRAY(SELECT AS STRUCT * FROM amended_records)) AS amended_records_json
FROM latest l"""


__all__ = ["build_highlights_query"]
