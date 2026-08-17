# Changelog

## 2026-08-17 — Validate production pipeline contracts and Scheduler handoff

### Added

- Added fixture-backed regression coverage for malformed and invalid-top-level
  XML CLI failures, structural-quality failures, structured status events, and
  immutable GCS writes.
- Added state-preservation assertions proving failed transformations leave the
  previous `state/latest.json` unchanged.

### Verified

- Focused pipeline tests pass: 11 tests.
- Forced Cloud Run execution `hatvp-ingestion-hbt9d` completed successfully
  with `quality_complete` reporting 0 errors, 3,556 warnings, and 5,763 flagged
  records, followed by `SUCCESS_WITH_WARNINGS`.
- Scheduler deliveries `hatvp-ingestion-c96k4` and `hatvp-ingestion-bbpbj`
  both completed with exit 0 and `NO_CHANGE`. Repeat execution
  `hatvp-ingestion-5pzdn` left all raw, derived, quality, and state object
  fingerprints unchanged.
- The isolated GCS immutable-write check rejected a different-byte overwrite
  with HTTP 412 while preserving generation `1786959796746977` and the
  original SHA-256.
- `HATVP_ENABLE_BIGQUERY=false` remains unchanged. No credentials or access
  tokens appeared in the validated structured log events.

### Follow-up

- Docker is not installed in the current workstation, so the local
  `docker build` and containerized malformed-fixture run remain to be verified
  by CI or on a machine with a container runtime. The deployed image already
  uses the tested `python -m hatvp.main` entrypoint.

## 2026-08-17 — Reconcile superseded annual-remuneration outliers

### Changed

- Updated `reports/revenue-stream-outliers-2026-08-17.md` after checking all
  55 raw annual-remuneration outlier rows against later same-person,
  same-context declaration versions.
- Excluded 11 older declaration UUIDs covering 13 corrected outlier rows and
  131 annual rows from the report's effective view. Raw XML verification
  confirmed the corrections, including Stephanie Rist's 2025 `députée` value
  changing from `5 919 820` to `62 730`.
- Retained the 12 later-version matches whose high value was unchanged, so
  they remain flagged for manual review.

### Verified

- The effective register now contains 42 outliers across 21 declarations;
  the raw normalized snapshot remains unchanged at 74,725 rows, with 74,594
  rows represented in the effective view.
- Recomputed the effective median/MAD statistics and refreshed the candidate
  table. No raw or normalized source rows were deleted.

## 2026-08-17 — Add combined revenue-stream outlier report

### Added

- Added `reports/revenue-stream-outliers-2026-08-17.md`, covering both sparse
  `revenuMandatDto` income categories and annual `mandatElectifDto`
  remuneration values.

### Verified

- Recomputed the report from the successful 2026-08-17 GCS snapshot using the
  immutable XML SHA-256 and pipeline revision recorded in `state/latest.json`.
- Confirmed 66 income rows reconcile exactly to the 22 source `totalElu`
  aggregates, with zero formal income outliers.
- Confirmed 74,725 annual remuneration rows, 55 robust outliers across 32
  declarations, and zero quality errors in the deployed snapshot.

## 2026-08-17 — Preserve elected-mandate remuneration history

### Added

- Added the `mandate_remunerations` normalized table with one row per annual
  value nested in `mandatElectifDto`.
- Added parser and quality coverage for repeated annual remuneration values,
  including zero values and French number formatting.

### Changed

- Elected mandate rows no longer expose the final annual amount as if it were a
  scalar total when an item contains multiple years. They retain the complete
  source series in `raw_record_json`, expose `remuneration_count`, and leave
  scalar remuneration fields null for multi-year items.
- Documentation now distinguishes `revenuMandatDto` category incomes from
  elected-mandate remuneration and reports separate coverage metrics.

### Verified

- Full local checks pass: Ruff, 25 tests, and `uv build`.
- A live local-output run against the 2026-08-17 HATVP source wrote 74,725
  `mandate_remunerations` rows across 5,850 declarations, with zero quality
  errors.

### Operational follow-up

- Increased the Cloud Run Job memory limit to `2Gi` after the first deployed
  force replay reached the previous `512Mi` limit while writing the expanded
  normalized outputs.
- Redeployed through GitHub Actions run `31982811358` and force-ran execution
  `hatvp-ingestion-4479p` successfully. The resulting GCS snapshot contains
  74,725 `mandate_remunerations` rows, zero quality errors, and
  `state/latest.json` records pipeline commit `94d04a4`.

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
