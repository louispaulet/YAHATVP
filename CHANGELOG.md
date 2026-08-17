# Changelog

## 2026-08-17 — Deploy and replay the income coverage fix

### Verified

- Fast-forwarded the fix/report branch onto `main` and deployed the Cloud Run
  Job through GitHub Actions run `31980037696` at code revision `97af103`, then
  redeployed the force-execution entrypoint fix at `dc77f44` through run
  `31980500905`.
- Forced online execution `hatvp-ingestion-lcpv9` completed successfully and
  rewrote the 2026-08-17 GCS snapshot outputs with `incomes=66`,
  `income_rows_with_numeric_value=66`, `income_declarations=9`, and zero
  quality errors.
- Confirmed the normalized income Parquet object exists in GCS and the source
  category values reconcile to the source `totalElu` aggregates.
- Confirmed `HATVP_ENABLE_BIGQUERY=false`; the `hatvp` BigQuery dataset was not
  found, so no BigQuery tables were created by this run.

## 2026-08-17 — Make Cloud Run force executions appendable

### Changed

- Switched the container application invocation from Docker `CMD` to an
  explicit `ENTRYPOINT`, so Cloud Run execution-time arguments such as
  `--force` append to `python -m hatvp.main` instead of replacing the
  executable.

### Follow-up

- The deployed job's BigQuery flag remains `HATVP_ENABLE_BIGQUERY=false`; the
  forced run will reprocess GCS/Parquet outputs but will not create BigQuery
  tables until BigQuery is explicitly enabled and permission-validated.

## 2026-08-17 — Add `revenuMandatDto` income outlier report

### Added

- Added `reports/statistical-income-outliers-2026-08-17.md` with the full
  source-to-parser funnel, category distribution, declaration-level summaries,
  review candidates, and `totalElu` reconciliation.

### Verified

- The live XML contains 198 fixed category slots but only 66 numeric elected-
  person category values; the normalized `incomes` table contains exactly 66
  rows across 9 declarations.
- The 66 category values sum to €1,098,531, exactly matching the 22 source
  `totalElu` aggregates; the robust income detector finds zero formal outliers
  at the configured absolute z-score > 10 threshold.

## 2026-08-17 — Expand manual income trace

### Changed

- Extended the manual-review JSON bundle with all nine source income category
  slots, the `totalElu` aggregate, and a numeric reconciliation between the
  populated categories and the source total.

### Verified

- The six populated category values reconcile exactly to `totalElu=73005`; the
  three empty source category slots remain visible for manual review.

## 2026-08-17 — Add live declaration manual-review bundle

### Added

- Added a representative live declaration XML and associated normalized JSON
  bundle under
  `reports/manual-review/2026-08-17/6dcd326d-e076-4d7a-a428-15075a15dddd/`.
- Included source SHA-256, GCS snapshot path, parser commit, table counts, and
  all normalized rows for the selected declaration UUID.

### Changed

- Empty DTO item containers no longer create synthetic rows such as
  `{"items": null}` in assets, activities, participations, or liabilities.

### Verified

- The selected review bundle contains 1 declaration, 1 person, 1 mandate, 6
  incomes, 19 assets, and 0 liabilities.
- Focused parser and quality tests pass: 12 tests.

## 2026-08-17 — Correct income row counting and coverage reporting

### Changed

- Excluded empty fixed income category slots from the normalized `incomes`
  table while retaining source values and the `totalElu` fallback.
- Added declaration-level income-section presence and populated-item metadata.
- Added quality checks for income sections, distinct income declarations, source
  values, numeric values, and empty income sections.

### Verified

- The live 2026-08-17 XML replay changed the income table from 198 category
  slots to 66 populated rows, across 9 declarations; 55 declarations contain
  the income section and 46 of those sections have no populated rows.
- Focused parser and quality tests pass: 12 tests.

## 2026-08-17 — Portable HTML outlier report

### Added

- Added the canonical report artifact and self-contained HTML version at
  `reports/statistical-asset-outliers-2026-08-17.artifact.json` and
  `reports/statistical-asset-outliers-2026-08-17.html`.
- Added native charts for outliers by asset section, euro value band, and
  highest-value declaration groups.
- Marked monetary fields and table/chart axes as euro-denominated while
  preserving raw source numeric text for fact checking.

### Verified

- Artifact validation passed with 22 blocks, 3 charts, 4 tables, and 4 metric
  cards.
- Portable builder verification passed at 1,440px and 390px viewports,
  including source-dialog interaction and responsive checks.

## 2026-08-17 — Statistical outlier report

### Added

- Added `reports/statistical-asset-outliers-2026-08-17.md`, a fact-checking
  report for the 143 statistical asset outliers in the successful
  `2026-08-17` snapshot.
- Included declarant names, normalized publication dates, declaration UUIDs,
  source sections, raw values, normalized values, and the full outlier register.

### Verified

- Confirmed all 143 flagged rows join to a declarant name and publication date
  through `declaration_uuid`.

## 2026-08-16

### Added

- Created the billed Google Cloud project `yahatvp-pipeline-eu` in
  `europe-west1`.
- Created the dedicated archive bucket `yahatvp-pipeline-eu-data` with uniform
  bucket-level access, public access prevention, and object versioning.
- Created the `hatvp` Artifact Registry repository.
- Created separate `hatvp-runtime`, `hatvp-scheduler`, and `hatvp-deployer`
  service accounts.
- Created a GitHub Workload Identity Pool and OIDC provider restricted to
  `louispaulet/YAHATVP` on `main`.
- Configured the eight non-secret GitHub repository variables required by
  `.github/workflows/deploy.yml`.
- Deployed the `hatvp-ingestion` Cloud Run Job with BigQuery disabled for the
  first smoke test.

### Changed

- Replaced the README architecture ASCII diagram with a Mermaid flowchart.
- Updated GitHub Actions to build and push the container directly from the
  GitHub runner, avoiding the failing Cloud Build source-staging path.
- Kept the deployer separate from the runtime identity and removed the
  temporary Cloud Build-specific IAM grants after verification.

### Verified

- GitHub Actions run [31971826703](https://github.com/louispaulet/YAHATVP/actions/runs/31971826703)
  passed tests, Ruff, Docker build/push, and Cloud Run deployment.
- Cloud Run execution `hatvp-ingestion-q78jz` completed successfully.
- Snapshot `2026-08-16` wrote raw XML/CSV and metadata, normalized Parquet
  tables, quarantine anomalies, a quality report, and `state/latest.json`.
- The quality report contained zero errors, 3,510 warnings, and 5,763 flagged
  records; those records still need review.

### Pending

- Configure and manually validate the weekly Europe/Paris Cloud Scheduler
  trigger.
- Decide whether to enable and validate BigQuery.
- Run the remaining local hardening tests, including `NO_CHANGE`, failure-state
  preservation, immutable snapshot conflicts, and row-count regression checks.

## 2026-08-16 — Local hardening

### Added

- Added fixtures covering all observed asset DTO sections, liabilities, empty
  optional declaration sections, and missing `general` blocks.
- Added regression tests for changed XML/CSV hashes, BigQuery state-update
  gating, immutable same-date raw snapshots, catastrophic row-count reductions,
  negative asset flags, and required XML top-level structure.

### Changed

- Added streaming checks for the required XML root and top-level declaration
  container before declaration normalization.
- Made row-count checks explicit and limited them to the previous successful
  quality report.
- Documented normalized table grains, important fields, and first-snapshot
  quality triage in the README.

### Verified

- Focused parser, quality, and pipeline tests pass: 17 tests.
- Live quality report review classified repeated names and asset outliers as
  retained review flags, negative bank balances as source-valid-but-flagged,
  and duplicate declaration UUIDs as actionable.

## 2026-08-17

### Added

- Added the versioned `hatvp.scheduler_smoke` task (`1.0.0`) for trigger-only
  validation. It emits one structured success event and does not download HATVP
  data or write pipeline state.
- Enabled Cloud Scheduler in `yahatvp-pipeline-eu` and deployed the separate
  `hatvp-scheduler-smoke` Cloud Run Job from image tag `baa27d8`.
- Created `hatvp-scheduler-smoke-weekly` with an authenticated Cloud Run Jobs
  `:run` target using the dedicated `hatvp-scheduler` service account.

### Verified

- Confirmed the weekly trigger configuration is `0 7 * * 1` with timezone
  `Europe/Paris`, a 180-second attempt deadline, and the expected smoke-job URI.
- Temporarily scheduled two nearby Paris-local test times (`00:02` and
  `00:04`). Scheduler attempts at `2026-08-16T22:02:03Z` and
  `2026-08-16T22:04:00Z` created executions `hatvp-scheduler-smoke-rrdwn` and
  `hatvp-scheduler-smoke-srwmc`; both completed with `succeededCount=1`.
- Confirmed Cloud Logging emitted `scheduler_smoke_task_version=1.0.0` and
  `status=success` for both scheduled executions. The final weekly schedule was
  restored with next run `2026-08-17T05:00:00Z`.

### Pending

- Keep the tested Scheduler trigger on the dummy task until acceptance; point a
  production trigger at `hatvp-ingestion` only in a separate handoff.
- Confirm duplicate-delivery safety and a successful Scheduler-triggered
  ingestion execution after that handoff.
