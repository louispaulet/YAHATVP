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
    anomaly_registry = f"{prefix}.anomaly_registry"
    silver_declarations = f"{prefix}.silver_declarations"
    silver_people = f"{prefix}.silver_people"
    return f"""WITH latest AS (
  SELECT MAX(snapshot_date) AS snapshot_date FROM {gold_declarations}
), current_declarations AS (
  SELECT d.snapshot_date, d.declaration_uuid, d.bronze_record_key, d.mandat_label, d.date_depot,
    p.prenom, p.nom
  FROM {gold_declarations} d
  JOIN {gold_people} p USING (snapshot_date, bronze_record_key, declaration_uuid)
  CROSS JOIN latest l
  WHERE d.snapshot_date = l.snapshot_date
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY {accent_fold("TRIM(COALESCE(p.prenom, ''))")},
      {accent_fold("TRIM(COALESCE(p.nom, ''))")}
    ORDER BY d.date_depot DESC,
      IF(LOWER(COALESCE(d.declaration_modificative, 'false')) IN ('true', '1', 'oui'), 1, 0) DESC,
      d.declaration_uuid DESC
  ) = 1
), active_income_records AS (
  SELECT r.record_ref
  FROM {anomaly_registry} r CROSS JOIN latest l
    WHERE r.snapshot_date = l.snapshot_date
    AND r.record_ref LIKE 'incomes:%'
    AND r.status NOT IN ('superseded', 'resolved')
    AND COALESCE(r.active_in_gold, TRUE)
    AND r.rule_id IN (
      'COMP_FACTOR_ERROR', 'COMP_IMPLAUSIBLE_AMOUNT', 'COMP_CONCATENATED_VALUE',
      'COMP_CONFLICT_SAME_PERIOD', 'COMP_SUPERSEDED_DECLARATION'
    )
    GROUP BY r.record_ref
), annual_income AS (
  SELECT i.declaration_uuid, SAFE_CAST(i.income_year AS INT64) AS income_year,
    SUM(i.normalized_value) AS amount,
    COUNTIF(flagged.record_ref IS NOT NULL) > 0 AS review_required
  FROM {gold_incomes} i
  JOIN current_declarations c USING (snapshot_date, bronze_record_key, declaration_uuid)
  LEFT JOIN active_income_records flagged
    ON flagged.record_ref = CONCAT('incomes:', i.bronze_record_key)
  CROSS JOIN latest l
  WHERE i.snapshot_date = l.snapshot_date
    AND i.normalized_value IS NOT NULL
    AND SAFE_CAST(i.income_year AS INT64) < EXTRACT(YEAR FROM l.snapshot_date)
  GROUP BY i.declaration_uuid, income_year
), income_history AS (
  SELECT *, LAG(income_year) OVER w AS previous_year,
    LAG(amount) OVER w AS previous_amount,
    LAG(review_required) OVER w AS previous_review_required
  FROM annual_income WINDOW w AS (PARTITION BY declaration_uuid ORDER BY income_year)
), income_change_candidates AS (
  SELECT h.declaration_uuid, c.prenom, c.nom, c.mandat_label,
    h.previous_year, h.income_year, h.previous_amount, h.amount,
    h.amount - h.previous_amount AS absolute_change,
    SAFE_DIVIDE(h.amount, NULLIF(h.previous_amount, 0)) AS ratio,
    h.review_required OR h.previous_review_required AS review_required,
    ROW_NUMBER() OVER (
      PARTITION BY h.declaration_uuid
      ORDER BY ABS(h.amount - h.previous_amount) DESC, h.income_year DESC
    ) AS candidate_rank
  FROM income_history h JOIN current_declarations c USING (declaration_uuid)
  WHERE h.previous_year = h.income_year - 1
    AND h.previous_amount IS NOT NULL
    AND (h.review_required OR h.previous_review_required)
), income_changes AS (
  SELECT declaration_uuid, prenom, nom, mandat_label, previous_year, income_year,
    previous_amount, amount, absolute_change, ratio, review_required
  FROM income_change_candidates
  WHERE candidate_rank = 1
  ORDER BY ABS(absolute_change) DESC, declaration_uuid
  LIMIT 8
), unusual_assets AS (
  SELECT a.declaration_uuid, c.prenom, c.nom, c.mandat_label,
    a.source_section, a.asset_name, a.raw_value, a.normalized_value,
    a.anomaly_status, TRUE AS review_required
  FROM {gold_assets} a
  JOIN current_declarations c USING (snapshot_date, bronze_record_key, declaration_uuid)
  WHERE FALSE
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
