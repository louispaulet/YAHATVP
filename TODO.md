# YAHATVP TODO

This checklist turns the project requirements into an execution plan. The local
pipeline is implemented and tested; the main remaining work is connecting it to
Google Cloud and completing a production smoke test.

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

## Next step: provide Google Cloud project details

This is the first step that requires your involvement. Decide or provide:

- [ ] Google Cloud project ID with billing enabled.
- [ ] Deployment region, recommended: `europe-west1`.
- [ ] Dedicated bucket name for HATVP archives.
- [ ] Whether BigQuery should be enabled for the first production deployment.
- [ ] GitHub repository owner/name used by the Workload Identity Federation condition.

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

- [ ] Enable Artifact Registry, Cloud Run, Cloud Scheduler, Cloud Storage, Cloud Logging, and BigQuery APIs if BigQuery is enabled.
- [ ] Create the dedicated GCS bucket with uniform bucket-level access.
- [ ] Create the Artifact Registry Docker repository.
- [ ] Create the Cloud Run runtime service account.
- [ ] Create the Cloud Scheduler invoker service account.
- [ ] Grant the runtime account object access only to the dedicated HATVP bucket.
- [ ] If BigQuery is enabled, grant only BigQuery job and dataset write permissions required by the loader.
- [ ] Grant the Scheduler account `roles/run.invoker` on the specific Cloud Run Job.
- [ ] Confirm Cloud Audit Logs and Cloud Logging retention meet operational needs.

The deployment commands are documented in the
[Google Cloud deployment section of README.md](README.md#google-cloud-deployment).

## 3. Build and deploy the first Cloud Run Job

- [ ] Build and push the image to Artifact Registry.
- [ ] Deploy the Cloud Run Job with one task, bounded retries, and a task timeout.
- [ ] Configure `HATVP_BUCKET`, `HATVP_PREFIX`, source URLs, pipeline version, and Git SHA.
- [ ] Start with `HATVP_ENABLE_BIGQUERY=false` unless BigQuery permissions have already been verified.
- [ ] Execute the job manually with `--wait`.
- [ ] Confirm the container exits with status 0 for a successful warning-bearing run.
- [ ] Confirm the container exits non-zero for malformed input or structural quality failure.
- [ ] Confirm Cloud Logging contains structured events for downloads, hashes, quality, and final status.

Manual smoke-test commands:

```bash
gcloud run jobs execute <JOB_NAME> --region=<REGION> --wait
gcloud run jobs executions list --job=<JOB_NAME> --region=<REGION>
```

## 4. Verify the GCS contract

After the first successful Cloud Run execution:

- [ ] Confirm both exact raw files exist under `raw/snapshot_date=.../`.
- [ ] Confirm `metadata.json` contains URL, size, SHA-256, timing, Git SHA, and pipeline version.
- [ ] Confirm raw objects cannot be overwritten by a retry with different bytes.
- [ ] Confirm every normalized table is written below `silver/<table>/snapshot_date=.../`.
- [ ] Confirm anomaly rows are present below `quarantine/snapshot_date=.../`.
- [ ] Confirm the machine-readable quality report is present below `quality/snapshot_date=.../`.
- [ ] Confirm `state/latest.json` is written only after all required outputs succeed.
- [ ] Confirm a second run with unchanged inputs returns `NO_CHANGE` and does not create a new derived snapshot.
- [ ] Confirm a failed transformation leaves the previous `state/latest.json` unchanged.

## 5. Configure the weekly Scheduler trigger

- [ ] Create a Cloud Scheduler HTTP target for the Cloud Run Jobs `:run` endpoint.
- [ ] Use Monday morning in the `Europe/Paris` timezone.
- [ ] Use OAuth with the dedicated Scheduler service account.
- [ ] Set retry behavior and an appropriate attempt deadline.
- [ ] Trigger the Scheduler job manually once.
- [ ] Confirm the resulting Cloud Run execution is visible in Cloud Logging.
- [ ] Confirm duplicate Scheduler delivery is safe because the pipeline is idempotent.

Recommended initial schedule:

```text
0 7 * * 1
timezone: Europe/Paris
```

## 6. Configure GitHub Actions CI/CD

- [ ] Create a Workload Identity Pool and GitHub OIDC provider.
- [ ] Restrict the provider attribute condition to this repository and the intended branch/event claims.
- [ ] Create a deployment service account separate from the Cloud Run runtime account.
- [ ] Grant the deployment account only Artifact Registry push, Cloud Run deployment, and required service-account impersonation permissions.
- [ ] Configure repository variables used by `.github/workflows/deploy.yml`:
  - [ ] `GCP_PROJECT_ID`
  - [ ] `GCP_REGION`
  - [ ] `ARTIFACT_REPOSITORY`
  - [ ] `CLOUD_RUN_JOB`
  - [ ] `HATVP_BUCKET`
  - [ ] `HATVP_RUNTIME_SERVICE_ACCOUNT`
  - [ ] `GCP_WIF_PROVIDER`
  - [ ] `GCP_DEPLOY_SERVICE_ACCOUNT`
- [ ] Push a small change to `main` and confirm tests run before deployment.
- [ ] Confirm the workflow builds, pushes, and deploys without any JSON credential secret.
- [ ] Confirm the deployed job uses the intended image SHA rather than a floating `latest` tag.

## 7. Enable and validate BigQuery, if wanted

- [ ] Decide the first curated tables: `declarations`, `people`, `incomes`, and `assets` at minimum.
- [ ] Confirm every table includes `snapshot_date`.
- [ ] Confirm tables are partitioned by `snapshot_date` where supported.
- [ ] Run the same snapshot twice and confirm the second load replaces that snapshot rather than duplicating rows.
- [ ] Confirm BigQuery remains optional when `HATVP_ENABLE_BIGQUERY=false`.
- [ ] Confirm a BigQuery failure prevents the latest state hash from advancing.
- [ ] Document the analytical table schemas and example queries.

## 8. Production go-live checklist

- [ ] Run one complete manual Cloud Run execution and review the quality report.
- [ ] Review all flagged records from the first snapshot.
- [ ] Confirm raw data, Parquet outputs, quarantine, quality report, and state are all present.
- [ ] Confirm the Scheduler-triggered execution succeeds.
- [ ] Confirm the `NO_CHANGE` path works on a repeat execution.
- [ ] Confirm logs never contain credentials or access tokens.
- [ ] Confirm the runtime service account has no unnecessary project-wide roles.
- [ ] Confirm the repository branch is clean and CI is green.
- [ ] Record the first production snapshot date and pipeline Git SHA.

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
