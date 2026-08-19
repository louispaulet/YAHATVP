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
    declarations = table(prefix, "declarations")
    people = table(prefix, "people")
    incomes = table(prefix, "incomes")
    assets = table(prefix, "assets")
    age_at_snapshot = _age("l.snapshot_date", "p.date_naissance_date")
    search_term = accent_fold("@search_term")
    first_name = accent_fold("COALESCE(p.prenom, '')")
    last_name = accent_fold("COALESCE(p.nom, '')")
    full_name = accent_fold("CONCAT(COALESCE(p.prenom, ''), ' ', COALESCE(p.nom, ''))")
    group_name = accent_fold("CONCAT(COALESCE(prenom, ''), ' ', COALESCE(nom, ''))")
    return f"""WITH latest AS (
  SELECT MAX(snapshot_date) AS snapshot_date FROM {declarations}
), search AS (
  SELECT {search_term} AS term
), person_rows AS (
  SELECT p.declaration_uuid, p.prenom, p.nom, p.date_naissance,
    p.date_naissance_date, p.date_naissance_quality_status,
    d.mandat_label, d.organ_label, ({age_at_snapshot}) AS age_years,
    CONCAT({first_name}, '|',
      {last_name}, '|',
      COALESCE(CAST(p.date_naissance_date AS STRING), '')) AS person_key
  FROM {people} p
  JOIN {declarations} d ON d.declaration_uuid = p.declaration_uuid
    AND d.snapshot_date = p.snapshot_date
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
), selected_declarations AS (
  SELECT DISTINCT pr.declaration_uuid
  FROM person_rows pr JOIN selected_person sp USING (person_key)
), income_rows AS (
  SELECT SAFE_CAST(i.income_year AS INT64) AS year,
    COALESCE(NULLIF(i.income_type, ''), i.income_stream, 'unknown') AS income_label,
    COALESCE(NULLIF(i.source_section, ''), i.income_stream, 'unknown') AS source_label,
    SUM(i.normalized_value) AS amount
  FROM {incomes} i JOIN selected_declarations sd ON sd.declaration_uuid = i.declaration_uuid
  CROSS JOIN latest l
  WHERE i.snapshot_date = l.snapshot_date AND i.normalized_value IS NOT NULL
    AND COALESCE(i.metric_eligible, TRUE) AND SAFE_CAST(i.income_year AS INT64) IS NOT NULL
  GROUP BY year, income_label, source_label
), income_by_year AS (
  SELECT year, SUM(amount) AS combined_amount,
    ARRAY_AGG(STRUCT(source_label, income_label, amount) ORDER BY amount DESC) AS sources
  FROM income_rows GROUP BY year
), occupation_rows AS (
  SELECT SAFE_CAST(i.income_year AS INT64) AS year,
    COALESCE(NULLIF(i.income_type, ''), NULLIF(d.mandat_label, ''), 'unknown') AS label,
    COALESCE(NULLIF(d.organ_label, ''), NULLIF(i.source_section, ''), 'HATVP') AS source,
    COUNT(*) AS row_count
  FROM {incomes} i
  JOIN selected_declarations sd ON sd.declaration_uuid = i.declaration_uuid
  JOIN {declarations} d ON d.declaration_uuid = i.declaration_uuid
    AND d.snapshot_date = i.snapshot_date
  CROSS JOIN latest l
  WHERE i.snapshot_date = l.snapshot_date AND SAFE_CAST(i.income_year AS INT64) IS NOT NULL
  GROUP BY year, label, source
  UNION ALL
  SELECT EXTRACT(YEAR FROM SAFE_CAST(COALESCE(d.date_debut_mandat, d.date_depot) AS DATE)) AS year,
    COALESCE(NULLIF(d.mandat_label, ''), 'unknown') AS label,
    COALESCE(NULLIF(d.organ_label, ''), 'HATVP') AS source, COUNT(*) AS row_count
  FROM {declarations} d JOIN selected_declarations sd ON sd.declaration_uuid = d.declaration_uuid
  CROSS JOIN latest l
  WHERE d.snapshot_date = l.snapshot_date
    AND SAFE_CAST(COALESCE(d.date_debut_mandat, d.date_depot) AS DATE) IS NOT NULL
  GROUP BY year, label, source
), occupations_by_year AS (
  SELECT year, SUM(row_count) AS occupation_count,
    ARRAY_AGG(STRUCT(label, source, row_count) ORDER BY row_count DESC, label) AS occupations
  FROM occupation_rows WHERE year IS NOT NULL GROUP BY year
), asset_rows AS (
  SELECT a.asset_acquisition_year AS year, a.source_section, a.asset_name,
    a.normalized_value, EXTRACT(YEAR FROM sp.date_naissance_date) AS date_naissance_year,
    a.asset_acquisition_year - EXTRACT(YEAR FROM sp.date_naissance_date) AS relative_age
  FROM {assets} a JOIN selected_declarations sd ON sd.declaration_uuid = a.declaration_uuid
  CROSS JOIN latest l CROSS JOIN selected_person sp
  WHERE a.snapshot_date = l.snapshot_date AND a.asset_acquisition_year IS NOT NULL
), assets_by_year AS (
  SELECT year, ANY_VALUE(relative_age) AS relative_age,
    ARRAY_AGG(STRUCT(source_section, asset_name, normalized_value)
      ORDER BY normalized_value DESC) AS assets
  FROM asset_rows GROUP BY year
)
SELECT FORMAT_DATE('%Y-%m-%d', l.snapshot_date) AS snapshot_date,
  CURRENT_TIMESTAMP() AS generated_at,
  TO_JSON_STRING(STRUCT(
    sp.person_key, sp.primary_uuid, sp.prenom, sp.nom, sp.date_naissance,
    sp.age_years, sp.date_naissance_quality_status, sp.declaration_count
  )) AS person_json,
  TO_JSON_STRING(ARRAY(
    SELECT AS STRUCT person_key, primary_uuid, prenom, nom, date_naissance,
      age_years, date_naissance_quality_status, declaration_count
    FROM person_groups ORDER BY exact_match DESC, declaration_count DESC, person_key LIMIT 20
  )) AS matches_json,
  TO_JSON_STRING(ARRAY(SELECT AS STRUCT * FROM income_by_year ORDER BY year)) AS income_json,
  TO_JSON_STRING(ARRAY(SELECT AS STRUCT * FROM occupations_by_year
    ORDER BY year)) AS occupations_json,
  TO_JSON_STRING(ARRAY(SELECT AS STRUCT * FROM assets_by_year ORDER BY year)) AS assets_json
FROM latest l CROSS JOIN selected_person sp"""


__all__ = ["build_age_analysis_query", "build_simple_analysis_query"]
