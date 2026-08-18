# YAHATVP TODO

This checklist turns the project requirements into an execution plan. The local
pipeline and first Google Cloud deployment are implemented and tested; the
weekly Scheduler trigger is connected to the production ingestion job and has
completed repeat live deliveries. The initial four-table BigQuery layer is
enabled and validated; remaining work is operational hardening and later table
expansion. First-snapshot quality triage is documented and complete.

## Current status

- [x] Inspect the live HATVP CSV and XML schemas.
- [x] Start from a single real declaration fixture.
- [x] Add broader fixtures for duplicate names, missing values, and malformed XML.
- [x] Implement streaming XML parsing with `lxml.etree.iterparse`.
- [x] Implement semicolon-delimited CSV parsing.
- [x] Compute separate exact-byte SHA-256 hashes for XML and CSV.
- [x] Implement `NO_CHANGE`, `SUCCESS`, `SUCCESS_WITH_WARNINGS`, and `FAILED` outcomes.
- [x] Implement local artifact storage and `--local-output` mode.
- [x] Implement immutable raw snapshot paths and late state updates.
- [x] Write normalized Parquet tables, anomaly Parquet, and quality JSON reports.
- [x] Implement normalization for French numbers, dates, whitespace, and missing markers.
- [x] Implement schema, referential, duplicate, null-rate, numeric, and MAD-based outlier checks.
- [x] Keep suspicious records and source values available instead of silently deleting them.
- [x] Add optional, idempotent BigQuery loading.
- [x] Add Dockerfile and GitHub Actions deployment workflow using Workload Identity Federation.
- [x] Run the test suite, Ruff, package build, and a live local run against the current HATVP files.
- [x] Modularize every tracked Python module into 70–100 physical lines, add YAML-driven typed configuration, and split fixture tests by behavior.
- [x] Group prefixed Python modules into domain packages and document the complete layout in the main README.
- [x] Deploy the refactored domain-package image and complete a forced production GCS/BigQuery replay.

## Google Cloud project details (completed)

The first deployment uses the following project configuration:

- [x] Google Cloud project `yahatvp-pipeline-eu` with billing enabled.
- [x] Deployment region: `europe-west1`.
- [x] Dedicated archive bucket: `yahatvp-pipeline-eu-data`.
- [x] BigQuery disabled for the first deployment: `HATVP_ENABLE_BIGQUERY=false`.
- [x] GitHub repository condition: `louispaulet/YAHATVP`, branch `main`.

No service-account JSON key is needed or wanted.

Authenticate locally when ready:

```bash
gcloud auth login
gcloud config set project <PROJECT_ID>
gcloud auth application-default login
gcloud auth application-default set-quota-project <PROJECT_ID>
```

ADC is needed for local GCS/BigQuery validation. GitHub Actions will use OIDC
Workload Identity Federation, not a stored key.

## 1. Harden the local implementation before cloud deployment

- [x] Review the current live quality report and decide which warnings are expected versus actionable.
- [x] Add fixtures for each observed asset DTO: real estate, bank accounts, insurance, securities, vehicles, liabilities, and foreign assets.
- [x] Add fixtures for declarations with no assets, no income, no mandate, and missing optional `general` sections.
- [x] Add tests proving a changed XML hash triggers processing and a changed CSV hash triggers processing.
- [x] Add a test proving BigQuery failure cannot advance `state/latest.json`.
- [x] Add a test proving an immutable raw snapshot rejects different bytes for the same snapshot date.
- [x] Add explicit catastrophic row-count reduction checks against the previous successful report.
- [x] Add explicit required top-level XML structure checks before normalization.
- [x] Exclude empty income category slots and report source-aware income coverage.
- [x] Preserve every annual `mandatElectifDto` remuneration in a dedicated normalized table.
- [x] Add a live declaration XML/parsed-data bundle for manual review and exclude placeholder-only DTO rows.
- [x] Add a `revenuMandatDto` income outlier report with source-to-parser reconciliation.
- [x] Add a combined outlier report for `revenuMandatDto` and annual `mandatElectifDto` remuneration values.
- [x] Reconcile superseded declaration versions in the revenue-stream outlier report.
- [x] Decide whether any current negative asset values are source-valid or should remain flagged.
- [x] Document the meaning of each normalized table and important field in the README.

Quality triage for the first production snapshot (`2026-08-16`): repeated names
and robust asset outliers remain review flags because they are plausible source
patterns; the nine negative bank-account balances are consistent with
overdrafts, so they remain flagged and retained; six duplicate declaration UUID
groups are actionable source-quality issues. The source-linked register contains
all 5,763 flagged rows with zero unresolved or parser/source-mismatch records;
all six duplicate UUID groups are semantically identical, with one pair
differing only by trailing whitespace.

Required local checks:

```bash
uv sync --locked
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv build
uv run python -m hatvp.main --local-output ./data --dry-run
```

## 2. Bootstrap Google Cloud resources

- [x] Enable Artifact Registry, Cloud Build, IAM, IAM Credentials, Cloud Run, Cloud Storage, and STS APIs.
- [x] Enable Cloud Scheduler and confirm Cloud Logging is available for Scheduler smoke validation.
- [x] Create the dedicated GCS bucket with uniform bucket-level access, public access prevention, and versioning.
- [x] Create the Artifact Registry Docker repository `hatvp` in `europe-west1`.
- [x] Create the Cloud Run runtime service account `hatvp-runtime`.
- [x] Create the Cloud Scheduler invoker service account `hatvp-scheduler`.
- [x] Grant the runtime account object access only to the dedicated HATVP bucket.
- [x] Grant only BigQuery job and dataset write permissions required by the loader (`roles/bigquery.jobUser` on the project and dataset-level `roles/bigquery.dataEditor`).
- [x] Grant the Scheduler account `roles/run.invoker` on the `hatvp-scheduler-smoke` Cloud Run Job; keep `hatvp-ingestion` unconnected until acceptance.
- [x] Confirm Cloud Audit Logs and Cloud Logging retention meet operational needs.

Retention verification on `2026-08-17` confirmed the production `_Required`
audit bucket is locked with 400-day retention, the `_Default` application-log
bucket retains 30 days, and the required audit sinks are present. No retention
settings were changed.

The deployment commands are documented in the
[Google Cloud deployment section of README.md](README.md#google-cloud-deployment).

## 3. Build and deploy the first Cloud Run Job

- [x] Build and push the image to Artifact Registry from GitHub Actions using the GitHub runner's Docker client.
- [x] Deploy the Cloud Run Job `hatvp-ingestion` with one task, one retry, and a 30-minute task timeout.
- [x] Deploy and force-replay the income coverage fix online; verify the GCS result contains 66 normalized income rows and zero quality errors.
- [x] Deploy and force-replay the year-preserving `mandatElectifDto` remuneration fix; verify 74,725 normalized remuneration rows and zero quality errors.
- [x] Configure `HATVP_BUCKET`, `HATVP_PREFIX`, source URLs, pipeline version, and Git SHA.
- [x] Start with `HATVP_ENABLE_BIGQUERY=false` until BigQuery permissions are verified.
- [x] Execute the job manually with `--wait`.
- [x] Confirm the container exits with status 0 for a warning-bearing run (`hatvp-ingestion-q78jz`).
- [x] Confirm the application entrypoint exits non-zero for malformed input or structural quality failure; fixture tests cover both paths and the deployed container uses this entrypoint.
- [x] Confirm Cloud Logging contains structured events for downloads, hashes, quality, and final status (`hatvp-ingestion-hbt9d`).

Manual smoke-test commands:

```bash
gcloud run jobs execute <JOB_NAME> --region=<REGION> --wait
gcloud run jobs executions list --job=<JOB_NAME> --region=<REGION>
```

## 4. Verify the GCS contract

After the first successful Cloud Run execution:

- [x] Confirm both exact raw files exist under `raw/snapshot_date=.../`.
- [x] Confirm `metadata.json` contains URL, size, SHA-256, timing, Git SHA, and pipeline version.
- [x] Confirm raw objects cannot be overwritten by a retry with different bytes; isolated validation object generation `1786959796746977` rejected the different-byte write with HTTP 412 and retained its SHA-256.
- [x] Confirm every normalized table is written below `silver/<table>/snapshot_date=.../`.
- [x] Confirm anomaly rows are present below `quarantine/snapshot_date=.../`.
- [x] Confirm the machine-readable quality report is present below `quality/snapshot_date=.../`.
- [x] Confirm `state/latest.json` is written only after all required outputs succeed.
- [x] Confirm a second run with unchanged inputs returns `NO_CHANGE` and does not create a new derived snapshot (`hatvp-ingestion-5pzdn`; pre/post object fingerprints and state hash matched).
- [x] Confirm a failed transformation leaves the previous `state/latest.json` unchanged (fixture coverage includes structural-quality and BigQuery failures).

The first smoke-test snapshot was `2026-08-16`. Its quality report contained
zero errors, 3,510 warnings, and 5,763 flagged records; every flagged row is
accounted for in the completed source-linked register.

## 5. Configure the weekly Scheduler trigger

- [x] Add the versioned `hatvp.scheduler_smoke` no-op task (`1.0.0`) that emits a structured success event and exits zero without running ingestion.
- [x] Deploy the `hatvp-scheduler-smoke` Cloud Run Job from image tag `baa27d8`.
- [x] Create the `hatvp-scheduler-smoke-weekly` HTTP target for the Cloud Run Jobs `:run` endpoint.
- [x] Use Monday morning in the `Europe/Paris` timezone: `0 7 * * 1`.
- [x] Use OAuth with the dedicated `hatvp-scheduler` service account.
- [x] Set a 180-second attempt deadline and retain the configured retry policy.
- [x] Validate near-now schedule `2 0 * * *` (`00:02 Europe/Paris`): Scheduler attempt `2026-08-16T22:02:03Z` created execution `hatvp-scheduler-smoke-rrdwn`, which completed with `succeededCount=1`.
- [x] Validate a second near-now schedule `4 0 * * *` (`00:04 Europe/Paris`): Scheduler attempt `2026-08-16T22:04:00Z` created execution `hatvp-scheduler-smoke-srwmc`, which completed with `succeededCount=1`.
- [x] Confirm both executions emitted `scheduler_smoke_task_version=1.0.0` in Cloud Logging.
- [x] Restore the final weekly schedule; next run is `2026-08-17T05:00:00Z` (`07:00 Europe/Paris`).
- [x] Point the production trigger at `hatvp-ingestion` after the smoke validation is accepted; `hatvp-ingestion-weekly` is enabled and the smoke trigger is paused.
- [x] Confirm duplicate delivery safety for the real ingestion pipeline: executions `hatvp-ingestion-c96k4` and `hatvp-ingestion-bbpbj` both completed with `NO_CHANGE` and exit 0.

Recommended initial schedule:

```text
0 7 * * 1
timezone: Europe/Paris
```

## 6. Configure GitHub Actions CI/CD

- [x] Create a Workload Identity Pool and GitHub OIDC provider.
- [x] Restrict the provider attribute condition to `louispaulet/YAHATVP` on `main`.
- [x] Create the deployment service account `hatvp-deployer` separately from the Cloud Run runtime account.
- [x] Grant the deployment account Artifact Registry push, Cloud Run deployment, Service Usage Consumer, and required service-account impersonation permissions.
- [x] Configure all repository variables used by `.github/workflows/deploy.yml`:
  - [x] `GCP_PROJECT_ID`
  - [x] `GCP_REGION`
  - [x] `ARTIFACT_REPOSITORY`
  - [x] `CLOUD_RUN_JOB`
  - [x] `HATVP_BUCKET`
  - [x] `HATVP_RUNTIME_SERVICE_ACCOUNT`
  - [x] `GCP_WIF_PROVIDER`
  - [x] `GCP_DEPLOY_SERVICE_ACCOUNT`
- [x] Push a change to `main` and confirm tests run before deployment.
- [x] Confirm the workflow builds, pushes, and deploys without any JSON credential secret.
- [x] Confirm the deployed job uses the commit SHA image tag rather than a floating `latest` tag.

## 7. Enable and validate BigQuery, if wanted

- [x] Decide the first curated tables: `declarations`, `people`, `incomes`, and `assets` at minimum.
- [x] Confirm every curated table includes `snapshot_date` as a `DATE`.
- [x] Confirm curated tables are partitioned by `snapshot_date`.
- [x] Run the same snapshot twice and confirm the second load replaces that snapshot rather than duplicating rows.
- [x] Confirm BigQuery remains optional when `HATVP_ENABLE_BIGQUERY=false`.
- [x] Confirm a BigQuery failure prevents the latest state hash from advancing.
- [x] Make BigQuery curated loads add new staged columns and insert by explicit
  column name so schema evolution cannot fail on positional ordering.
- [x] Document the analytical table schemas and example queries.
- [x] Rebuild the curated `incomes` partition from both observed revenue
  streams and verify the annual `mandatElectifDto` rows in BigQuery.

BigQuery validation evidence for snapshot `2026-08-17`: dataset
`yahatvp-pipeline-eu:hatvp` was created in `europe-west1`; deployment
`1000d0b03` ran through GitHub Actions run `32049058688`; forced executions
`hatvp-ingestion-f6mdg` and `hatvp-ingestion-ts6jb` both succeeded with
`incomes=74,791`; the four partition counts and row fingerprints were identical
across runs; and unchanged execution `hatvp-ingestion-rmclb` emitted
`NO_CHANGE`. The source-linked report is
[`reports/03-validation/2026-08-17-bigquery-and-income-validation.md`](reports/03-validation/2026-08-17-bigquery-and-income-validation.md).

## 8. Production go-live checklist

- [x] Run one complete manual Cloud Run execution and review the quality report.
- [x] Review all flagged records from the first snapshot and publish the source-linked triage register.
- [x] Confirm raw data, Parquet outputs, quarantine, quality report, and state are all present.
- [x] Confirm the Scheduler-triggered smoke execution succeeds; the smoke trigger is now paused after handoff.
- [x] Confirm the production Scheduler-triggered ingestion execution succeeds after handoff (`hatvp-ingestion-c96k4` and `hatvp-ingestion-bbpbj`).
- [x] Confirm the `NO_CHANGE` path works on a repeat execution (`hatvp-ingestion-5pzdn`).
- [x] Confirm logs never contain credentials or access tokens in the validated execution events.
- [x] Confirm the runtime service account has no unnecessary project-wide roles.
- [x] Confirm the repository branch is clean and CI is green.
- [x] Record the first production snapshot date (`2026-08-16`) and pipeline Git SHA (`f21853d`).

## 9. Ongoing operations

- [x] Keep the report catalog organized by numbered topic folders, consolidate
  overlapping validation notes, and preserve source/provenance links.
- [x] Add an alert for failed Cloud Run Job executions.
- [x] Add an alert for repeated `SUCCESS_WITH_WARNINGS` or an unusual increase in flagged records.
- [ ] Confirm the monitoring email channel delivers a test notification.
- [x] Verify the merged Cloud Run deployment emits the new quality telemetry.
- [ ] Review quality reports after each weekly run.
- [ ] Monitor recurrence and pursue source correction for the six duplicate declaration UUID groups; one pair differs only by trailing whitespace.
- [ ] Monitor row counts and null rates for sudden changes.
- [ ] Review HATVP schema changes before changing normalization logic.
- [ ] Add a new fixture before fixing any newly observed source edge case.
- [ ] Keep historical raw snapshots immutable.
- [ ] Periodically review bucket lifecycle/retention policy without deleting required audit history.

The three alert policies and email channel were created and verified in
`yahatvp-pipeline-eu` on `2026-08-17`. Policy resources are recorded in the
monitoring runbook; the notification channel is
`projects/yahatvp-pipeline-eu/notificationChannels/15119347564909849591`.

Post-merge image `d2b4a9b` deployed successfully. Forced executions
`hatvp-ingestion-ff7gs` and `hatvp-ingestion-dqc6b` completed with exit 0; the
second emitted `quality_warning_streak` with `warning_streak=2`, 5,818 flagged
records, and zero quality errors.

## 10. Transparency dashboard

- [x] Add an isolated Vite/React/Tailwind frontend with HashRouter under `website/hatvp-transparency-dashboard/frontend`.
- [x] Add a Cloudflare Worker API under `website/hatvp-transparency-dashboard/backend/worker`.
- [x] Add a read-only BigQuery Cloud Run bridge under `website/hatvp-transparency-dashboard/backend/bigquery-bridge`.
- [x] Keep the public API aggregate-only and exclude raw rows and personal contact fields.
- [x] Add Worker, bridge, and frontend fixture/unit tests plus Makefile targets.
- [x] Document local development, secret handling, Cloudflare deployment, and GitHub Pages deployment.
- [x] Configure the production bridge token and deploy the Cloudflare Worker.
- [x] Configure the repository GitHub Pages source and publish the frontend `gh-pages` branch.
- [x] Run a live dashboard smoke test against the deployed Worker and review the public aggregate output.
- [x] Split dashboard overview, income, assets, and declaration data into independently cacheable API slices.
- [x] Add slow-blinking loading shells so the dashboard layout renders before any slice completes.
- [x] Use lazy-loaded Recharts pie and bar plots with animation, responsive sizing, tooltips, and accessible value lists.
- [x] Add English/French locale configuration, a language switcher, and readable translations for dynamic dashboard labels.
- [x] Harden declaration-type translation lookup for source-label casing and punctuation variants.
- [x] Add translated About-page links to the official HATVP open-data page and source CSV/XML feeds.
- [x] Add a sticky footer with a translated link to the YAHATVP GitHub project.
- [x] Add a translated About-page link to the YAHATVP GitHub project.
- [x] Add a generated WebP HATVP mark to the navbar and browser favicon.
- [x] Distinguish the external HATVP page from the direct CSV/XML downloads on the About page.
- [x] Keep the asset chart legend inside its panel at desktop widths.
- [x] Compare total income and asset amounts in the dashboard pie chart.
- [x] Compare average annual reported income with total assets and explain the calculation.
- [x] Use compact, locale-aware formatting for large dashboard values.

Deployment evidence (2026-08-18): Cloud Run bridge revision
`hatvp-dashboard-api-00003-xzr` and Worker version
`c3caf8a3-7ee8-47cf-bc3e-52b06db3138f` are serving. The Worker returned 200
for `/healthz` and `/api/dashboard`; the latter returned the latest snapshot
and aggregate counts of 6,611 declarations, 6,611 people, 74,791 incomes, and
1,157 assets. GitHub Pages is configured from `gh-pages` and returned 200.
Chrome verification also confirmed the production CORS header and successful
dashboard rendering after Worker version `b2450c38-cc3a-48d8-8f46-81b6a5b396e1`.

Annual-income comparison deployment evidence (2026-08-18): Cloud Run revision
`hatvp-dashboard-api-00006-gjl` and Worker version
`79c8519a-5ef6-4739-84ce-2ff5efffa759` are serving. The live income slice
returns `yearCount=17` and `totalValue=1243594880.8`; the asset slice returns
`totalValue=124440950`. GitHub Pages returned HTTP 200 with the expected
production API configuration.

## 11. BigQuery tutorial

- [x] Add ten atomic BigQuery tutorial queries with matching CSV results for the
  validated `2026-08-18` snapshot.
- [x] Document the query progression, fixed snapshot convention, stable-UUID
  joins, and CSV regeneration commands.

## Later, only if needed

- [ ] Add semantic/content hashes after the exact-byte hash path is stable.
- [ ] Add richer schema-drift reporting for new XML sections and fields.
- [ ] Add a small operational dashboard from Cloud Logging and quality reports.
- [ ] Add partition-aware BigQuery retention and cost controls.
- [ ] Add data catalog/documentation for the normalized tables.
