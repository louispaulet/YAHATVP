# 2026-10-06 production ingestion memory recovery

## Failure and diagnosis

The scheduled execution `hatvp-ingestion-gjt24` on 2026-10-05 downloaded the
HATVP CSV and XML successfully, then failed twice at the Cloud Run Job's 4 GiB
memory limit. The CSV was 3,188,280 bytes and the XML was 79,520,455 bytes. The
new CSV and XML hashes (`781fc5e5…` and `a042d437…`) differed from the last
processed snapshot (`045c5970…` and `5d65b2ab…`), so the job had to rebuild the
analytical layers. The failed execution did not advance `state/latest.json`.

The known larger profile of 8 vCPU / 32 GiB was applied, but both attempts in
execution `hatvp-ingestion-4tsx8` also reached the memory limit. Inspection of
the history loader showed that it read both Bronze and Silver Parquet objects
for snapshots present in both layers, then deduplicated those rows later during
Silver construction. The stored `incomes` objects had five snapshot dates
represented in both layers, so this needlessly inflated the full in-memory
rebuild.

## Repair

- Updated the GitHub Actions deployment and repository instructions to keep
  `hatvp-ingestion` at 8 vCPU / 32 GiB. The updated profile is deployed from
  commit `6ca97ec`.
- Changed historical loading to select Bronze for each snapshot when present,
  while preserving Silver-only legacy snapshots. The processing fix is in
  commit `50deaaf`.
- The corrected CI workflow
  [37518534872](https://github.com/louispaulet/YAHATVP/actions/runs/37518534872)
  passed the full Python suite (183 tests), Ruff, formatting, package build,
  deployment configuration, image build, and Cloud Run deployment.

## Production verification

The normal, non-forced retry `hatvp-ingestion-pjq2w` completed successfully in
11m30.77s on 2026-10-06 with one successful task. Its image was
`europe-west1-docker.pkg.dev/yahatvp-pipeline-eu/hatvp/hatvp:50deaafc6d2a80a35831f09cf04970754a7ae697`.
The log emitted `bigquery_load_complete` for all 13 tables:

```text
declarations, people, incomes, assets,
silver_declarations, silver_people, silver_incomes, silver_assets,
gold_declarations, gold_people, gold_incomes, gold_assets, anomaly_registry
```

`pipeline_complete` followed the loads, and only then did `state/latest.json`
advance from `2026-08-30` to `2026-10-06`. The processed state records the new
CSV hash `781fc5e54b20bda1be5b095dcd76bbfee674cee342ec36e694099f6781704597`,
XML hash `a042d437b9b05f0af0aa93e7e95f18b038fb21c0eb8a3b69f499dc1e66bcd9cb`,
and pipeline commit `50deaafc6d2a80a35831f09cf04970754a7ae697`.

The quality report for snapshot `2026-10-06` has zero errors, 57,370 flagged
records (1.9% fewer than the previous report's 58,502), no flagged-record
regression, and 40,156 warnings. The status is `SUCCESS_WITH_WARNINGS`; the
20-run warning streak remains open for human review. No source values were
corrected or deleted.

Execution details are available in the
[Cloud Run execution](https://console.cloud.google.com/run/jobs/executions/details/europe-west1/hatvp-ingestion-pjq2w?project=366762423535).
