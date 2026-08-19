-- HATVP anomaly handoff review for snapshot 2026-08-19.
-- Run with:
--   bq query --location=europe-west1 --use_legacy_sql=false < this-file
--
-- The queries read only BigQuery Bronze/Silver/Gold outputs and the anomaly
-- registry. They preserve observed values; candidate values are rule evidence.

DECLARE run_snapshot_date DATE DEFAULT DATE '2026-08-19';

-- 1. Snapshot-wide registry profile.
SELECT
  rule_id,
  COUNT(*) AS anomaly_rows,
  COUNTIF(status = 'active') AS active_rows,
  COUNTIF(previously_reported) AS internally_previously_reported_rows,
  COUNTIF(active_in_gold) AS active_in_gold_rows
FROM `yahatvp-pipeline-eu.hatvp.anomaly_registry`
WHERE snapshot_date = run_snapshot_date
GROUP BY rule_id
ORDER BY anomaly_rows DESC, rule_id;

-- 2. Exclusion-aware candidates. The row_number is computed over every Gold
-- declaration for a normalized name+surname before anomaly rows are joined.
WITH excluded_names AS (
  SELECT LOWER(TRIM(name)) AS normalized_name
  FROM UNNEST([
    'Jean-François Vigier',
    'Alain Kelyor',
    'Isabelle Kaloi-Bearune',
    'Robert Cavanna',
    'Jean-Louis Rio',
    'Claude Cannet',
    'Christelle Michel Deleage',
    'Daniel Rouge',
    'Georges Botella',
    'Allen Salmon',
    'Chantal Juglard',
    'Fabienne Keller'
  ]) AS name
),
all_declarations AS (
  SELECT
    d.declaration_uuid,
    d.date_depot,
    d.date_derniere_declaration_raw,
    d.declaration_modificative,
    d.declaration_version,
    d.declaration_type_label,
    d.mandat_label,
    p.prenom,
    p.nom,
    ROW_NUMBER() OVER (
      PARTITION BY LOWER(TRIM(p.prenom)), LOWER(TRIM(p.nom))
      ORDER BY
        d.date_depot DESC,
        d.date_derniere_declaration_raw DESC,
        IF(LOWER(COALESCE(d.declaration_modificative, '')) IN ('true', '1', 'oui'), 1, 0) DESC,
        d.declaration_version DESC,
        d.declaration_uuid DESC
    ) AS name_version_rank,
    COUNT(*) OVER (
      PARTITION BY LOWER(TRIM(p.prenom)), LOWER(TRIM(p.nom))
    ) AS name_version_count
  FROM `yahatvp-pipeline-eu.hatvp.gold_declarations` d
  JOIN `yahatvp-pipeline-eu.hatvp.gold_people` p
    USING (snapshot_date, declaration_uuid)
  WHERE d.snapshot_date = run_snapshot_date
),
latest_declarations AS (
  SELECT *
  FROM all_declarations
  WHERE name_version_rank = 1
),
registry AS (
  SELECT
    r.anomaly_id,
    r.rule_id,
    r.field,
    r.period,
    r.observed_value,
    r.expected_value_or_range,
    r.candidate_value_or_range,
    r.source_location,
    r.record_ref
  FROM `yahatvp-pipeline-eu.hatvp.anomaly_registry` r
  WHERE r.snapshot_date = run_snapshot_date
    AND r.status = 'active'
    AND r.active_in_gold
    AND NOT r.previously_reported
    AND r.rule_id IN (
      'COMP_YOY_CHANGE',
      'COMP_DIGIT_EDIT',
      'COMP_FACTOR_ERROR',
      'COMP_IMPLAUSIBLE_AMOUNT'
    )
),
linked AS (
  SELECT r.*, i.declaration_uuid
  FROM registry r
  JOIN `yahatvp-pipeline-eu.hatvp.gold_incomes` i
    ON i.snapshot_date = run_snapshot_date
   AND r.record_ref = CONCAT('incomes:', i.bronze_record_key)
  UNION ALL
  SELECT r.*, a.declaration_uuid
  FROM registry r
  JOIN `yahatvp-pipeline-eu.hatvp.gold_assets` a
    ON a.snapshot_date = run_snapshot_date
   AND r.record_ref = CONCAT('assets:', a.bronze_record_key)
  UNION ALL
  SELECT r.*, p.declaration_uuid
  FROM registry r
  JOIN `yahatvp-pipeline-eu.hatvp.gold_people` p
    ON p.snapshot_date = run_snapshot_date
   AND r.record_ref = CONCAT('people:', p.bronze_record_key)
),
dedup AS (
  SELECT DISTINCT
    anomaly_id,
    rule_id,
    field,
    period,
    observed_value,
    expected_value_or_range,
    candidate_value_or_range,
    source_location,
    declaration_uuid
  FROM linked
),
candidates AS (
  SELECT
    d.*,
    l.date_depot,
    l.date_derniere_declaration_raw,
    l.declaration_modificative,
    l.declaration_version,
    l.declaration_type_label,
    l.mandat_label,
    l.prenom,
    l.nom,
    l.name_version_rank,
    l.name_version_count
  FROM dedup d
  JOIN latest_declarations l USING (declaration_uuid)
  WHERE LOWER(TRIM(CONCAT(l.prenom, ' ', l.nom))) NOT IN (
    SELECT normalized_name FROM excluded_names
  )
)
SELECT
  prenom,
  nom,
  date_depot,
  declaration_uuid,
  name_version_rank,
  name_version_count,
  declaration_type_label,
  mandat_label,
  rule_id,
  period,
  observed_value,
  expected_value_or_range,
  candidate_value_or_range,
  source_location,
  anomaly_id
FROM candidates
ORDER BY
  LOWER(nom),
  LOWER(prenom),
  rule_id,
  period,
  anomaly_id;

-- 3. Exact audited handoff rows used in the report. This makes the judgmental
-- ten-declaration sample reproducible while the query above remains the
-- general candidate generator.
WITH audited_shortlist AS (
  SELECT *
  FROM UNNEST([
    STRUCT(1 AS selection_order, '4fe560c3-59e0-42b5-bda6-094139aeef1e' AS declaration_uuid),
    STRUCT(2 AS selection_order, '2bb7d5df-98f5-4e42-ad28-0cbf2445c9e8' AS declaration_uuid),
    STRUCT(3 AS selection_order, '4794faad-da62-40f8-a76d-8e05539adeb8' AS declaration_uuid),
    STRUCT(4 AS selection_order, '46e63284-3037-44f9-bdb3-50d709a9e119' AS declaration_uuid),
    STRUCT(5 AS selection_order, '89adb603-8266-4f95-b278-657cd2e72de0' AS declaration_uuid),
    STRUCT(6 AS selection_order, '39684a69-d8f3-4616-b51e-a554727f628e' AS declaration_uuid),
    STRUCT(7 AS selection_order, 'b7fee2e7-052b-49f8-9b4b-95ee89a81696' AS declaration_uuid),
    STRUCT(8 AS selection_order, '549ef34f-1669-4c3f-895f-70a9a4279537' AS declaration_uuid),
    STRUCT(9 AS selection_order, 'bdff151a-af40-4ea0-98b7-cca32021f1aa' AS declaration_uuid),
    STRUCT(10 AS selection_order, '6e9e510a-f18f-4c76-b68e-6e58e02a7825' AS declaration_uuid)
  ])
)
SELECT
  s.selection_order,
  p.prenom,
  p.nom,
  d.date_depot,
  d.declaration_uuid,
  d.declaration_type_label,
  d.mandat_label,
  d.is_latest_declaration,
  d.active_in_gold
FROM audited_shortlist s
JOIN `yahatvp-pipeline-eu.hatvp.gold_declarations` d
  ON d.snapshot_date = run_snapshot_date
 AND d.declaration_uuid = s.declaration_uuid
JOIN `yahatvp-pipeline-eu.hatvp.gold_people` p
  ON p.snapshot_date = run_snapshot_date
 AND p.declaration_uuid = s.declaration_uuid
ORDER BY s.selection_order;
