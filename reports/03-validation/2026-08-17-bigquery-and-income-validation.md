# BigQuery and income validation — 2026-08-17

## Technical summary

The refreshed BigQuery curated layer is live and validated for the
`2026-08-17` HATVP snapshot. The Cloud Run job loaded `declarations`, `people`,
`incomes`, and `assets` into the regional `yahatvp-pipeline-eu.hatvp` dataset.
All four tables are partitioned by a `DATE`-typed `snapshot_date` field. A
forced replay replaced the same snapshot without changing row counts or row
fingerprints, and a post-refresh unchanged-input execution returned
`NO_CHANGE`.

The load completed with zero quality errors. The source still contains known
review flags, so the operational status remains `SUCCESS_WITH_WARNINGS`.

This is the consolidated validation report for the refreshed curated layer.
It replaces the former standalone income-coverage note; the detailed
source-to-parser and outlier analyses remain in `../02-outliers/`.

## Curated tables validated idempotently per snapshot

| Table | Rows in snapshot partition | `snapshot_date` type | Row fingerprint |
| --- | ---: | --- | ---: |
| `declarations` | 6,611 | `DATE` | `-5383795550778946119` |
| `people` | 6,611 | `DATE` | `-2019889874151548892` |
| `incomes` | 74,791 | `DATE` | `-2929076836325473210` |
| `assets` | 1,157 | `DATE` | `-5142282871526498847` |

The counts and fingerprints were identical after successful executions
`hatvp-ingestion-f6mdg` and `hatvp-ingestion-ts6jb`. The partition metadata
reported the same row counts for partition `20260817` in all four tables.
The unchanged execution `hatvp-ingestion-rmclb` returned `NO_CHANGE` without
advancing state or rewriting derived outputs.
Other normalized tables remain in GCS and were intentionally not published to
BigQuery in this first rollout.

## Scope, data, and metric definitions

- **Snapshot:** `2026-08-17`, identified by the exact source hashes recorded in
  `state/latest.json`.
- **Curated row count:** rows where `snapshot_date = DATE '2026-08-17'`.
- **Row fingerprint:** `BIT_XOR(FARM_FINGERPRINT(TO_JSON_STRING(row)))`, used
  as a compact repeat-load comparison alongside exact row counts.
- **Source of truth:** immutable raw and silver GCS artifacts; BigQuery is the
  curated analytical copy.

## Early data findings

### Declarations and people remain aligned at the snapshot grain

Both tables contain 6,611 rows in the first curated partition. This supports a
straightforward declaration-to-person join for this snapshot, while the
existing source-quality checks still retain duplicate declaration UUID groups
for review rather than deduplicating them.

### Income coverage is intentionally sparse

The curated `incomes` table contains 74,791 numeric rows across 5,859
declarations: 74,725 annual `mandate_remuneration` rows across 5,850
declarations and 66 `revenu_mandat` rows across 9 declarations. The latter
stream remains sparse: 55 declarations have an income section, of which 46
have no populated category rows. Empty fixed category slots are still excluded
from the curated table, while annual `mandatElectifDto` values are preserved
with their source years and explicit zeroes.

### Income coverage recovery

The initial curated `incomes` result contained only 66 rows because it read
the populated `revenuMandatDto` categories. The XML also contains annual
remuneration values nested under `mandatElectifDto`; those values were already
preserved in the dedicated `mandate_remunerations` table but were not included
in the unified income view.

The parser and loader now:

- emit one unified income row per annual `mandatElectifDto` remuneration;
- tag rows as `mandate_remuneration` or `revenu_mandat`;
- preserve source years, raw French-formatted values, normalized values,
  source item indexes, remuneration indexes, and raw record JSON;
- retain empty category slots as non-observations and explicit zero-valued
  annual remuneration rows as valid source records; and
- add staged BigQuery columns before inserting by explicit column names, so
  schema evolution cannot break a repeat load through positional alignment.

The successful production verification used deployment revision
`1000d0b03a6fdcebef75b467fca1cf7a95860d84` and GitHub Actions run
`32049058688`. The forced replay `hatvp-ingestion-f6mdg`, repeat forced replay
`hatvp-ingestion-ts6jb`, and unchanged-input execution
`hatvp-ingestion-rmclb` provide the row-count, fingerprint, and `NO_CHANGE`
evidence summarized above. The new curated columns are `income_stream`
(`STRING`) and `remuneration_index` (`INT64`).

### Asset anomalies are review flags, not deletions

The `assets` table contains 1,157 rows. Quality checks retain 143 robust
statistical asset outliers and 9 negative asset values. The negative values are
consistent with small overdraft-style bank-account balances in the reviewed
source and remain flagged for auditability.

### Identity collisions remain visible

The quality report records 3,352 duplicate person-name findings and 6 duplicate
declaration UUID groups. These are source-quality findings, not evidence that
rows should be removed. The immutable raw XML, normalized rows, and source
identifiers remain available for follow-up.

## Validation method and evidence

1. Created `yahatvp-pipeline-eu.hatvp` in `europe-west1`.
2. Granted `roles/bigquery.jobUser` to `hatvp-runtime` at project scope and
   dataset-level `roles/bigquery.dataEditor` access.
3. Deployed commit `1000d0b03a6fdcebef75b467fca1cf7a95860d84` through GitHub
   Actions run `32049058688` using Workload Identity Federation.
4. Confirmed structured `bigquery_load_complete` logging for the four selected
   tables during `hatvp-ingestion-f6mdg`.
5. Queried `INFORMATION_SCHEMA.COLUMNS` and `INFORMATION_SCHEMA.PARTITIONS`
   to verify field type, partition id, and partition row counts.
6. Re-ran the same snapshot with `--force` as `hatvp-ingestion-ts6jb` and
   compared counts and fingerprints.
7. Re-ran without `--force`; `hatvp-ingestion-rmclb` emitted both
   `pipeline_complete` and `pipeline_status` with status `NO_CHANGE`.

The repeat-load comparison query was:

```sql
SELECT COUNT(*) AS row_count,
       BIT_XOR(FARM_FINGERPRINT(TO_JSON_STRING(row))) AS row_fingerprint
FROM `yahatvp-pipeline-eu.hatvp.declarations` AS row
WHERE snapshot_date = DATE '2026-08-17';
```

The same query shape was applied to each curated table. The source quality
report and state record were read from:

- `gs://yahatvp-pipeline-eu-data/hatvp/quality/snapshot_date=2026-08-17/report.json`
- `gs://yahatvp-pipeline-eu-data/hatvp/state/latest.json`

The exact source hashes for this validation are:

- XML SHA-256: `865261857f88ec6c262558bc115b37b94f97ea3418b6829267aa6cbd1458fdaf`
- CSV SHA-256: `156463f08b88dd884dcbb0721d9295869c8df7595cf98696162030123938dd29`
- Unified income Parquet:
  `gs://yahatvp-pipeline-eu-data/hatvp/silver/incomes/snapshot_date=2026-08-17/data.parquet`

The failed first replay stopped at the old 14-column BigQuery insert and did
not advance `state/latest.json`; the schema migration above resolved that
failure. Local checks and a live local-output run also completed with zero
quality errors.

## Limitations and robustness

- This is one snapshot, so it establishes correctness and idempotency but not
  temporal trend behavior.
- Only four curated tables are currently loaded into BigQuery; all other
  normalized tables remain GCS-only.
- The `BIT_XOR` fingerprint is a repeat-load guard, not a cryptographic table
  digest. Exact source hashes remain the authoritative snapshot identity.
- The warning-bearing quality status is expected and does not indicate a
  failed load; zero structural quality errors were reported.
- The two income streams have different semantics and should not be summed
  without an explicit analytical definition: `revenuMandatDto` is a sparse
  declaration-level category stream, while `mandatElectifDto` is an annual
  remuneration stream.

## Recommended next steps

- Review the quality report after each weekly load and monitor the four table
  row counts, null rates, and partition freshness.
- Monitor recurrence of the six duplicate declaration UUID groups and pursue
  source correction where appropriate.
- Add the remaining normalized tables only after their observed schemas and
  empty/null-only behavior receive the same validation treatment.
- Add Cloud Run failure and warning-spike alerts before relying on the pipeline
  without manual review.

## Further questions

- Should the detailed `mandate_remunerations` table become the next curated
  table, given its 74,725-row source population and remuneration-specific
  fields already represented in the unified `incomes` view?
- What retention and cost policy should apply to future BigQuery partitions?
