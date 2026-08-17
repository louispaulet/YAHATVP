# BigQuery tutorial

This folder contains ten small, progressively harder queries against the
curated HATVP BigQuery layer. Each `.sql` file has one query and each matching
`.csv` file is the result captured from that query.

## Prerequisites

The examples use the production project and dataset:

```text
Project: yahatvp-pipeline-eu
Dataset: hatvp
Tables: declarations, people, incomes, assets
Location: europe-west1
```

Authenticate with Google Cloud ADC or another BigQuery-supported identity, then
run a query from the repository root. For example:

```bash
bq --project_id=yahatvp-pipeline-eu \
  --location=europe-west1 \
  query --use_legacy_sql=false --format=csv \
  < tutorial/01_declarations_by_type.sql \
  > tutorial/01_declarations_by_type.csv
```

The checked-in results use the fixed snapshot `2026-08-18`. To analyze another
partition, replace `DATE '2026-08-18'` in the SQL file and regenerate only its
matching CSV. The query files intentionally do not use `MAX(snapshot_date)`, so
the SQL and CSV remain a reproducible pair after a new weekly load.

## Queries

| # | SQL / CSV | Difficulty | What it demonstrates |
| ---: | --- | --- | --- |
| 1 | `01_declarations_by_type` | Easy | Grouping and counting declarations by type. |
| 2 | `02_people_quality_by_civilite` | Easy | Grouping people rows and calculating a quality-flag percentage. |
| 3 | `03_assets_by_section` | Easy | Counts, null-aware values, sums, and averages by asset section. |
| 4 | `04_incomes_by_stream` | Easy | Comparing the two income streams and their year ranges. |
| 5 | `05_duplicate_declaration_ids` | Easy | Finding repeated stable declaration identifiers for review. |
| 6 | `06_income_coverage_by_declaration_type` | Intermediate | A left join from declarations to per-declaration income coverage. |
| 7 | `07_assets_by_declaration_type_and_section` | Intermediate | Joining asset rows to declaration labels and aggregating by two dimensions. |
| 8 | `08_income_by_mandat` | Intermediate | Aggregating income at declaration grain before joining mandate labels. |
| 9 | `09_income_vs_assets_by_declaration` | Advanced | Joining per-declaration income and asset totals and calculating a ratio. |
| 10 | `10_profile_by_declaration_type` | Advanced | Combining all four curated tables into one coverage and value profile. |

## Reading the joins

`declaration_uuid` is the stable join key shared by the curated tables. The
source can contain repeated declaration UUIDs; query 5 makes those records
visible instead of deleting them. The later analytical examples group the
declarations table by `(snapshot_date, declaration_uuid)` and use
`ANY_VALUE(...)` for descriptive labels so a source duplicate does not multiply
child-table totals. This is an analysis convenience, not a source correction or
deduplication step in the ingestion pipeline.

The CSVs intentionally contain aggregate results and, only where useful for a
record-level comparison, declaration UUIDs. They do not export names, emails,
telephone numbers, or addresses from the people table.

## Regenerating all results

Each result can be regenerated independently. The following loop preserves the
one-SQL-file/one-CSV-file relationship; it assumes the filenames remain paired:

```bash
for sql in tutorial/*.sql; do
  csv="${sql%.sql}.csv"
  bq --project_id=yahatvp-pipeline-eu \
    --location=europe-west1 \
    query --use_legacy_sql=false --format=csv < "$sql" > "$csv"
done
```

The CSVs are checked-in teaching artifacts, not a replacement for the
immutable raw and silver GCS outputs or the curated BigQuery tables.
