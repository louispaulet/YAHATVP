# BigQuery Early Findings — 2026-08-17

## Technical summary

The initial BigQuery curated layer is live and validated for the
`2026-08-17` HATVP snapshot. The Cloud Run job loaded `declarations`, `people`,
`incomes`, and `assets` into the regional `yahatvp-pipeline-eu.hatvp` dataset.
All four tables are partitioned by a `DATE`-typed `snapshot_date` field. A
forced replay replaced the same snapshot without changing row counts or row
fingerprints, and an unchanged-input execution returned `NO_CHANGE`.

The load completed with zero quality errors. The source still contains known
review flags, so the operational status remains `SUCCESS_WITH_WARNINGS`.

## Curated tables loaded exactly once per snapshot

| Table | Rows in snapshot partition | `snapshot_date` type | Row fingerprint |
| --- | ---: | --- | ---: |
| `declarations` | 6,611 | `DATE` | `-5383795550778946119` |
| `people` | 6,611 | `DATE` | `-2019889874151548892` |
| `incomes` | 66 | `DATE` | `-2189167083081978288` |
| `assets` | 1,157 | `DATE` | `-5142282871526498847` |

The counts and fingerprints were identical after executions
`hatvp-ingestion-74pqj` and `hatvp-ingestion-7vgcm`. The partition metadata
reported the same row counts for partition `20260817` in all four tables.
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

The curated `incomes` table contains 66 populated numeric rows across 9
declarations. There are 55 declarations with an income section, of which 46
have no populated income rows. The source-aware parser therefore avoids
presenting empty fixed category slots as income observations. No statistical
income outliers were reported in the snapshot quality checks.

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
3. Deployed commit `ca9d19acd77c4f87916cf768c7873d3b5a0af249` through GitHub
   Actions run `32038454470` using Workload Identity Federation.
4. Confirmed structured `bigquery_load_complete` logging for the four selected
   tables during `hatvp-ingestion-74pqj`.
5. Queried `INFORMATION_SCHEMA.COLUMNS` and `INFORMATION_SCHEMA.PARTITIONS`
   to verify field type, partition id, and partition row counts.
6. Re-ran the same snapshot with `--force` and compared counts and fingerprints.
7. Re-ran without `--force`; `hatvp-ingestion-bzqvw` emitted both
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

## Limitations and robustness

- This is one snapshot, so it establishes correctness and idempotency but not
  temporal trend behavior.
- Only four curated tables are currently loaded into BigQuery; all other
  normalized tables remain GCS-only.
- The `BIT_XOR` fingerprint is a repeat-load guard, not a cryptographic table
  digest. Exact source hashes remain the authoritative snapshot identity.
- The warning-bearing quality status is expected and does not indicate a
  failed load; zero structural quality errors were reported.

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

- Should `mandate_remunerations` become the next curated table, given its
  74,725-row source population and separate outlier review work?
- What retention and cost policy should apply to future BigQuery partitions?
