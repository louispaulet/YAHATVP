# YAHATVP TODO

This checklist turns the project requirements into an execution plan. The local
pipeline and first Google Cloud deployment are implemented and tested; the
weekly Scheduler path is validated against a versioned no-op job, while the
production ingestion handoff, optional BigQuery, quality triage, and operational
hardening remain.

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

- [ ] Review the current live quality report and decide which warnings are expected versus actionable.
- [ ] Add fixtures for each observed asset DTO: real estate, bank accounts, insurance, securities, vehicles, liabilities, and foreign assets.
- [ ] Add fixtures for declarations with no assets, no income, no mandate, and missing optional `general` sections.
- [ ] Add tests proving a changed XML hash triggers processing and a changed CSV hash triggers processing.
- [ ] Add a test proving BigQuery failure cannot advance `state/latest.json`.
- [ ] Add a test proving an immutable raw snapshot rejects different bytes for the same snapshot date.
- [ ] Add explicit catastrophic row-count reduction checks against the previous successful report.
- [ ] Add explicit required top-level XML structure checks before normalization.
- [ ] Decide whether any current negative asset values are source-valid or should remain flagged.
- [ ] Document the meaning of each normalized table and important field in the README.

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
- [ ] If BigQuery is enabled, grant only BigQuery job and dataset write permissions required by the loader.
- [x] Grant the Scheduler account `roles/run.invoker` on the `hatvp-scheduler-smoke` Cloud Run Job; keep `hatvp-ingestion` unconnected until acceptance.
- [ ] Confirm Cloud Audit Logs and Cloud Logging retention meet operational needs.

The deployment commands are documented in the
[Google Cloud deployment section of README.md](README.md#google-cloud-deployment).

## 3. Build and deploy the first Cloud Run Job

- [x] Build and push the image to Artifact Registry from GitHub Actions using the GitHub runner's Docker client.
- [x] Deploy the Cloud Run Job `hatvp-ingestion` with one task, one retry, and a 30-minute task timeout.
- [x] Configure `HATVP_BUCKET`, `HATVP_PREFIX`, source URLs, pipeline version, and Git SHA.
- [x] Start with `HATVP_ENABLE_BIGQUERY=false` until BigQuery permissions are verified.
- [x] Execute the job manually with `--wait`.
- [x] Confirm the container exits with status 0 for a warning-bearing run (`hatvp-ingestion-q78jz`).
- [ ] Confirm the container exits non-zero for malformed input or structural quality failure.
- [ ] Confirm Cloud Logging contains structured events for downloads, hashes, quality, and final status.

Manual smoke-test commands:

```bash
gcloud run jobs execute <JOB_NAME> --region=<REGION> --wait
gcloud run jobs executions list --job=<JOB_NAME> --region=<REGION>
```

## 4. Verify the GCS contract

After the first successful Cloud Run execution:

- [x] Confirm both exact raw files exist under `raw/snapshot_date=.../`.
- [x] Confirm `metadata.json` contains URL, size, SHA-256, timing, Git SHA, and pipeline version.
- [ ] Confirm raw objects cannot be overwritten by a retry with different bytes.
- [x] Confirm every normalized table is written below `silver/<table>/snapshot_date=.../`.
- [x] Confirm anomaly rows are present below `quarantine/snapshot_date=.../`.
- [x] Confirm the machine-readable quality report is present below `quality/snapshot_date=.../`.
- [x] Confirm `state/latest.json` is written only after all required outputs succeed.
- [ ] Confirm a second run with unchanged inputs returns `NO_CHANGE` and does not create a new derived snapshot.
- [ ] Confirm a failed transformation leaves the previous `state/latest.json` unchanged.

The first smoke-test snapshot was `2026-08-16`. Its quality report contained
zero errors, 3,510 warnings, and 5,763 flagged records; quality triage remains
open.

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
- [ ] Point a production trigger at `hatvp-ingestion` after the smoke validation is accepted.
- [ ] Confirm duplicate delivery safety for the real ingestion pipeline.

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

- [ ] Decide the first curated tables: `declarations`, `people`, `incomes`, and `assets` at minimum.
- [ ] Confirm every table includes `snapshot_date`.
- [ ] Confirm tables are partitioned by `snapshot_date` where supported.
- [ ] Run the same snapshot twice and confirm the second load replaces that snapshot rather than duplicating rows.
- [ ] Confirm BigQuery remains optional when `HATVP_ENABLE_BIGQUERY=false`.
- [ ] Confirm a BigQuery failure prevents the latest state hash from advancing.
- [ ] Document the analytical table schemas and example queries.

## 8. Production go-live checklist

- [x] Run one complete manual Cloud Run execution and review the quality report.
- [ ] Review all flagged records from the first snapshot.
- [x] Confirm raw data, Parquet outputs, quarantine, quality report, and state are all present.
- [x] Confirm the Scheduler-triggered smoke execution succeeds; the production ingestion job remains unconnected.
- [ ] Confirm the production Scheduler-triggered ingestion execution succeeds after handoff.
- [ ] Confirm the `NO_CHANGE` path works on a repeat execution.
- [ ] Confirm logs never contain credentials or access tokens.
- [x] Confirm the runtime service account has no unnecessary project-wide roles.
- [x] Confirm the repository branch is clean and CI is green.
- [x] Record the first production snapshot date (`2026-08-16`) and pipeline Git SHA (`f21853d`).

## 9. Ongoing operations

- [ ] Add an alert for failed Cloud Run Job executions.
- [ ] Add an alert for repeated `SUCCESS_WITH_WARNINGS` or an unusual increase in flagged records.
- [ ] Review quality reports after each weekly run.
- [ ] Monitor row counts and null rates for sudden changes.
- [ ] Review HATVP schema changes before changing normalization logic.
- [ ] Add a new fixture before fixing any newly observed source edge case.
- [ ] Keep historical raw snapshots immutable.
- [ ] Periodically review bucket lifecycle/retention policy without deleting required audit history.

## Later, only if needed

- [ ] Add semantic/content hashes after the exact-byte hash path is stable.
- [ ] Add richer schema-drift reporting for new XML sections and fields.
- [ ] Add a small operational dashboard from Cloud Logging and quality reports.
- [ ] Add partition-aware BigQuery retention and cost controls.
- [ ] Add data catalog/documentation for the normalized tables.
