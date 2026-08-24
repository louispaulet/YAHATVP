"""Fixed BigQuery queries for public age and declarant analyses."""

from __future__ import annotations

from query_support import accent_fold, dataset_prefix, table


def _age(reference: str, birth: str) -> str:
    """Return an exact completed-years age expression for two BigQuery dates."""

    return (
        f"EXTRACT(YEAR FROM {reference}) - EXTRACT(YEAR FROM {birth}) "
        f"- IF(FORMAT_DATE('%m-%d', {reference}) < FORMAT_DATE('%m-%d', {birth}), 1, 0)"
    )


def build_simple_analysis_query(project: str, dataset: str) -> str:
    """Build the latest-snapshot leaderboard and salary age-bin query."""

    prefix = dataset_prefix(project, dataset)
    declarations = table(prefix, "declarations")
    people = table(prefix, "people")
    incomes = table(prefix, "incomes")
    current_age = _age("l.snapshot_date", "p.date_naissance_date")
    normalized_first_name = accent_fold("COALESCE(p.prenom, '')")
    normalized_last_name = accent_fold("COALESCE(p.nom, '')")
    return f"""WITH latest AS (
  SELECT MAX(snapshot_date) AS snapshot_date FROM {declarations}
), people_base AS (
  SELECT p.declaration_uuid, p.prenom, p.nom, p.date_naissance,
    p.date_naissance_date, p.date_naissance_quality_status,
    d.mandat_label, d.organ_label, ({current_age}) AS age_years
  FROM {people} p
  JOIN {declarations} d ON d.declaration_uuid = p.declaration_uuid
    AND d.snapshot_date = p.snapshot_date
  CROSS JOIN latest l
  WHERE p.snapshot_date = l.snapshot_date
    AND p.date_naissance_date IS NOT NULL
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY {normalized_first_name},
      {normalized_last_name}, p.date_naissance_date
    ORDER BY d.date_depot DESC, p.declaration_uuid
  ) = 1
), income_age AS (
  SELECT i.normalized_value,
    ({_age("DATE(CAST(i.income_year AS INT64), 12, 31)", "p.date_naissance_date")}) AS age_years
  FROM {incomes} i
  JOIN {people} p ON p.declaration_uuid = i.declaration_uuid
    AND p.snapshot_date = i.snapshot_date
  CROSS JOIN latest l
  WHERE i.snapshot_date = l.snapshot_date
    AND i.normalized_value IS NOT NULL
    AND COALESCE(i.metric_eligible, TRUE)
    AND p.date_naissance_date IS NOT NULL
    AND SAFE_CAST(i.income_year AS INT64) IS NOT NULL
), all_age_rows AS (
  SELECT DIV(age_years, 5) * 5 AS age_bin_start, normalized_value
  FROM income_age
  WHERE age_years BETWEEN 18 AND 100
), salary_age_rows AS (
  SELECT age_bin_start, normalized_value
  FROM all_age_rows
  WHERE normalized_value != 0
), age_bin_domain AS (
  SELECT DISTINCT age_bin_start FROM all_age_rows
), age_stats AS (
  SELECT age_bin_start, COUNT(*) AS row_count, AVG(normalized_value) AS average_value
  FROM salary_age_rows GROUP BY age_bin_start
), age_medians AS (
  SELECT DISTINCT age_bin_start,
    PERCENTILE_CONT(normalized_value, 0.5) OVER (PARTITION BY age_bin_start) AS median_value
  FROM salary_age_rows
), age_bins AS (
  SELECT b.age_bin_start, COALESCE(s.row_count, 0) AS row_count,
    COALESCE(s.average_value, 0) AS average_value, COALESCE(m.median_value, 0) AS median_value
  FROM age_bin_domain b
  LEFT JOIN age_stats s USING (age_bin_start)
  LEFT JOIN age_medians m USING (age_bin_start)
), all_age_stats AS (
  SELECT age_bin_start, COUNT(*) AS row_count, AVG(normalized_value) AS average_value
  FROM all_age_rows GROUP BY age_bin_start
), all_age_medians AS (
  SELECT DISTINCT age_bin_start,
    PERCENTILE_CONT(normalized_value, 0.5) OVER (PARTITION BY age_bin_start) AS median_value
  FROM all_age_rows
), age_bins_including_zero AS (
  SELECT b.age_bin_start, s.row_count, s.average_value, m.median_value
  FROM age_bin_domain b
  JOIN all_age_stats s USING (age_bin_start)
  JOIN all_age_medians m USING (age_bin_start)
), zero_salary_bins AS (
  SELECT b.age_bin_start, COUNTIF(a.normalized_value = 0) AS row_count
  FROM age_bin_domain b
  LEFT JOIN all_age_rows a USING (age_bin_start)
  GROUP BY b.age_bin_start
)
SELECT FORMAT_DATE('%Y-%m-%d', l.snapshot_date) AS snapshot_date,
  CURRENT_TIMESTAMP() AS generated_at,
  TO_JSON_STRING(STRUCT(
    FORMAT_DATE('%Y-%m-%d', l.snapshot_date) AS reference_date,
    ARRAY(SELECT AS STRUCT * FROM people_base ORDER BY age_years, nom, prenom LIMIT 10) AS youngest,
    ARRAY(SELECT AS STRUCT * FROM people_base ORDER BY age_years DESC,
      nom, prenom LIMIT 10) AS oldest
  )) AS leaders_json,
  TO_JSON_STRING(ARRAY(
    SELECT AS STRUCT age_bin_start, FORMAT('%d–%d', age_bin_start, age_bin_start + 4) AS label,
      row_count, average_value, median_value
    FROM age_bins ORDER BY age_bin_start
  )) AS age_bins_json,
  TO_JSON_STRING(ARRAY(
    SELECT AS STRUCT age_bin_start, FORMAT('%d–%d', age_bin_start, age_bin_start + 4) AS label,
      row_count, average_value, median_value
    FROM age_bins_including_zero ORDER BY age_bin_start
  )) AS age_bins_including_zero_json,
  TO_JSON_STRING(ARRAY(
    SELECT AS STRUCT age_bin_start, FORMAT('%d–%d', age_bin_start, age_bin_start + 4) AS label,
      row_count
    FROM zero_salary_bins ORDER BY age_bin_start
  )) AS zero_salary_bins_json
FROM latest l"""


def build_age_analysis_query(project: str, dataset: str) -> str:
    """Build a parameterized latest-snapshot analysis for one public declarant."""

    prefix = dataset_prefix(project, dataset)
    declarations = f"{prefix}.silver_declarations"
    people = f"{prefix}.silver_people"
    incomes = f"{prefix}.silver_incomes"
    assets = f"{prefix}.silver_assets"
    age_at_snapshot = _age("l.snapshot_date", "p.date_naissance_date")
    search_term = accent_fold("@search_term")
    first_name = accent_fold("COALESCE(p.prenom, '')")
    last_name = accent_fold("COALESCE(p.nom, '')")
    full_name = accent_fold("CONCAT(COALESCE(p.prenom, ''), ' ', COALESCE(p.nom, ''))")
    group_name = accent_fold("CONCAT(COALESCE(prenom, ''), ' ', COALESCE(nom, ''))")
    event_age = _age("a.asset_event_date", "sp.date_naissance_date")
    return f"""WITH latest AS (
  SELECT MAX(snapshot_date) AS snapshot_date FROM {declarations}
), search AS (
  SELECT {search_term} AS term
), person_rows AS (
  SELECT p.snapshot_date, p.bronze_record_key, p.declaration_uuid,
    p.prenom, p.nom, p.date_naissance,
    p.date_naissance_date, p.date_naissance_quality_status,
    d.date_depot, d.declaration_modificative, d.declaration_type_id,
    d.declaration_type_label, d.mandat_label, d.organ_label,
    ({age_at_snapshot}) AS age_years,
    CONCAT({first_name}, '|',
      {last_name}, '|',
      COALESCE(CAST(p.date_naissance_date AS STRING), '')) AS person_key
  FROM {people} p
  JOIN {declarations} d USING (snapshot_date, bronze_record_key, declaration_uuid)
  CROSS JOIN latest l CROSS JOIN search s
  WHERE p.snapshot_date = l.snapshot_date
    AND (STRPOS({first_name}, s.term) > 0
      OR STRPOS({last_name}, s.term) > 0
      OR STRPOS({full_name}, s.term) > 0)
), person_groups AS (
  SELECT person_key, ANY_VALUE(prenom) AS prenom, ANY_VALUE(nom) AS nom,
    ANY_VALUE(date_naissance) AS date_naissance,
    ANY_VALUE(date_naissance_date) AS date_naissance_date,
    ANY_VALUE(date_naissance_quality_status) AS date_naissance_quality_status,
    ANY_VALUE(age_years) AS age_years, COUNT(DISTINCT declaration_uuid) AS declaration_count,
    MIN(declaration_uuid) AS primary_uuid,
    MAX(IF({group_name} = s.term, 1, 0)) AS exact_match
  FROM person_rows CROSS JOIN search s
  GROUP BY person_key
), selected_person AS (
  SELECT * FROM person_groups ORDER BY exact_match DESC, declaration_count DESC, person_key LIMIT 1
), declaration_rows AS (
  SELECT pr.*,
    CASE WHEN STARTS_WITH(UPPER(pr.declaration_type_id), 'DI') THEN 'interest'
      WHEN STARTS_WITH(UPPER(pr.declaration_type_id), 'DSP') THEN 'assets'
      ELSE 'other' END AS declaration_family
  FROM person_rows pr JOIN selected_person sp USING (person_key)
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY pr.declaration_uuid ORDER BY pr.bronze_record_key DESC
  ) = 1
), ranked_declarations AS (
  SELECT *, ROW_NUMBER() OVER (
    PARTITION BY declaration_family
    ORDER BY date_depot DESC,
      IF(LOWER(COALESCE(declaration_modificative, 'false')) IN ('true', '1', 'oui'), 1, 0) DESC,
      declaration_uuid DESC
  ) AS family_rank
  FROM declaration_rows
), latest_interest AS (
  SELECT * FROM ranked_declarations WHERE declaration_family = 'interest' AND family_rank = 1
), latest_assets AS (
  SELECT * FROM ranked_declarations WHERE declaration_family = 'assets' AND family_rank = 1
), income_rows AS (
  SELECT SAFE_CAST(i.income_year AS INT64) AS year,
    CONCAT(i.declaration_uuid, ':', COALESCE(i.income_stream, ''), ':',
      COALESCE(CAST(i.source_item_index AS STRING), ''), ':', COALESCE(i.income_year, ''), ':',
      COALESCE(CAST(i.remuneration_index AS STRING), '')) AS source_id,
    CASE WHEN i.income_stream = 'mandate_remuneration' THEN 'mandate'
      WHEN i.income_stream = 'activity_remuneration' THEN 'activity'
      ELSE 'income' END AS source_kind,
    i.source_section, COALESCE(NULLIF(i.income_type, ''), i.income_stream, 'unknown') AS label,
    JSON_VALUE(i.raw_record_json, '$.employeur') AS employer,
    JSON_VALUE(i.raw_record_json, '$.dateDebut') AS start_date,
    JSON_VALUE(i.raw_record_json, '$.dateFin') AS end_date,
    JSON_VALUE(i.raw_record_json, '$.remuneration.brutNet') AS amount_basis,
    i.normalized_value AS amount, COALESCE(i.metric_eligible, TRUE) AS metric_eligible,
    COALESCE(NULLIF(i.anomaly_status, ''), 'ok') AS review_status
  FROM {incomes} i
  JOIN latest_interest li USING (snapshot_date, bronze_record_key, declaration_uuid)
  CROSS JOIN latest l
  WHERE i.snapshot_date = l.snapshot_date AND i.normalized_value IS NOT NULL
    AND SAFE_CAST(i.income_year AS INT64) IS NOT NULL
), income_by_year AS (
  SELECT year, SUM(IF(metric_eligible, amount, 0)) AS combined_amount,
    ARRAY_AGG(STRUCT(source_id, source_kind, source_section, label, employer, start_date,
      end_date, amount_basis, amount, metric_eligible, review_status)
      ORDER BY amount DESC, label) AS sources
  FROM income_rows GROUP BY year
), asset_rows AS (
  SELECT CONCAT(a.declaration_uuid, ':', a.source_section, ':',
      CAST(a.source_item_index AS STRING)) AS source_id,
    a.source_section AS kind,
    CASE WHEN a.source_section = 'assuranceVieDto'
        THEN COALESCE(JSON_VALUE(a.raw_record_json, '$.etablissement'), a.asset_name)
      WHEN a.source_section = 'comptesBancaireDto' THEN CONCAT(
        COALESCE(JSON_VALUE(a.raw_record_json, '$.typeCompte'), a.asset_name, 'Compte'),
        COALESCE(CONCAT(' · ', JSON_VALUE(a.raw_record_json, '$.etablissement')), ''))
      ELSE a.asset_name END AS name,
    a.normalized_value AS value,
    a.asset_acquisition_year AS event_year, a.asset_acquisition_year_raw AS event_date_raw,
    a.asset_event_date AS event_date, a.asset_event_precision AS event_precision,
    a.asset_event_source_field AS event_source_field,
    CASE WHEN a.asset_event_source_field = 'dateSouscription' THEN 'subscription'
      WHEN a.asset_event_source_field IN ('dateAcquisition', 'dateAchat', 'anneeAcquisition')
        THEN 'acquisition'
      WHEN a.asset_event_source_field = 'dateDetention' THEN 'holding'
      ELSE NULL END AS event_kind,
    CASE WHEN a.asset_event_precision = 'day' AND a.asset_event_date IS NOT NULL
      AND sp.date_naissance_date IS NOT NULL THEN ({event_age}) ELSE NULL END AS age_years,
    CASE WHEN a.asset_acquisition_year IS NOT NULL AND a.asset_event_precision != 'day'
      THEN a.asset_acquisition_year - EXTRACT(YEAR FROM sp.date_naissance_date) - 1 ELSE NULL
      END AS age_range_min,
    CASE WHEN a.asset_acquisition_year IS NOT NULL AND a.asset_event_precision != 'day'
      THEN a.asset_acquisition_year - EXTRACT(YEAR FROM sp.date_naissance_date) ELSE NULL
      END AS age_range_max,
    la.date_depot AS declared_at, COALESCE(a.metric_eligible, TRUE) AS metric_eligible,
    COALESCE(NULLIF(a.anomaly_status, ''), 'ok') AS review_status
  FROM {assets} a JOIN latest_assets la USING (snapshot_date, bronze_record_key, declaration_uuid)
  CROSS JOIN latest l CROSS JOIN selected_person sp
  WHERE a.snapshot_date = l.snapshot_date
)
SELECT FORMAT_DATE('%Y-%m-%d', l.snapshot_date) AS snapshot_date,
  CURRENT_TIMESTAMP() AS generated_at,
  TO_JSON_STRING(STRUCT(
    sp.person_key,
    COALESCE((SELECT declaration_uuid FROM latest_interest),
      (SELECT declaration_uuid FROM latest_assets), sp.primary_uuid) AS primary_uuid,
    sp.prenom, sp.nom, sp.date_naissance,
    sp.age_years, sp.date_naissance_quality_status, sp.declaration_count
  )) AS person_json,
  TO_JSON_STRING(ARRAY(
    SELECT AS STRUCT person_key, primary_uuid, prenom, nom, date_naissance,
      age_years, date_naissance_quality_status, declaration_count
    FROM person_groups ORDER BY exact_match DESC, declaration_count DESC, person_key LIMIT 20
  )) AS matches_json,
  TO_JSON_STRING(STRUCT(
    (SELECT COUNTIF(declaration_family = 'interest') FROM ranked_declarations) AS interest_count,
    (SELECT COUNTIF(declaration_family = 'assets') FROM ranked_declarations) AS asset_count,
    (SELECT AS STRUCT declaration_uuid, date_depot, declaration_type_id,
      declaration_type_label, declaration_modificative, mandat_label, organ_label
      FROM latest_interest) AS latest_interest,
    (SELECT AS STRUCT declaration_uuid, date_depot, declaration_type_id,
      declaration_type_label, declaration_modificative, mandat_label, organ_label
      FROM latest_assets) AS latest_assets,
    ARRAY(SELECT AS STRUCT rd.declaration_uuid, rd.date_depot, rd.declaration_type_id,
      rd.declaration_type_label, rd.declaration_modificative, rd.mandat_label, rd.organ_label,
      rd.declaration_family, rd.family_rank = 1 AS is_selected,
      (SELECT COUNT(*) FROM {incomes} i WHERE i.snapshot_date = rd.snapshot_date
        AND i.bronze_record_key = rd.bronze_record_key) AS income_row_count,
      (SELECT COUNT(*) FROM {assets} a WHERE a.snapshot_date = rd.snapshot_date
        AND a.bronze_record_key = rd.bronze_record_key) AS asset_row_count
      FROM ranked_declarations rd ORDER BY rd.date_depot DESC, rd.declaration_uuid DESC
    ) AS history
  )) AS declaration_context_json,
  TO_JSON_STRING(ARRAY(SELECT AS STRUCT * FROM income_by_year ORDER BY year)) AS income_json,
  TO_JSON_STRING(ARRAY(SELECT AS STRUCT * FROM asset_rows
    ORDER BY event_year, kind, name, source_id)) AS assets_json
FROM latest l CROSS JOIN selected_person sp"""


__all__ = ["build_age_analysis_query", "build_simple_analysis_query"]
