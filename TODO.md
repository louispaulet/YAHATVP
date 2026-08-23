# YAHATVP TODO

This checklist turns the project requirements into an execution plan. The local
pipeline and first Google Cloud deployment are implemented and tested; the
weekly Scheduler trigger is connected to the production ingestion job and has
completed repeat live deliveries. The four-table BigQuery layer is the Bronze
foundation, with explicit Silver, Gold, and anomaly-registry artifacts now
implemented and validated locally. Remaining unchecked items are explicitly
deferred enhancements in the final section. First-snapshot quality triage is
documented and complete.

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
- [x] Keep comparison-chart legend labels visible when the chart panel is narrow.
- [x] Fix declaration annual-value bars collapsing in auto-sized flex columns and add a rendering regression test.
- [x] Add source-preserving typed DOB fields and explicit DOB quality status to Gold people rows.
- [x] Add source-preserving asset acquisition year fields for time-based analysis.
- [x] Add the simple DOB/salary analysis page with youngest/oldest leaderboards and five-year age bins.
- [x] Filter salary analysis to ages 18–100, exclude 0€ salaries by default with a toggle, and chart zero-salary counts by age bin.
- [x] Add the declarant age/year page with a Lecornu example, name search, annual income sources, occupations, and asset timeline.
- [x] Cover the new pipeline, bridge, Worker, and frontend contracts with fixture/unit tests.
- [x] Verify both analysis pages, the Lecornu search flow, responsive layout, and browser console output with Chrome MCP.
- [x] Open, mark ready, and merge PR #31 from the feature branch.
- [x] After merge, replay ingestion before dashboard deployment so the new Gold columns are present in BigQuery.
- [x] Deploy the BigQuery bridge, Cloudflare Worker, and frontend for the new analysis pages.
- [x] Mark ready, resolve, and merge open PRs #34, #33, and #32 into `main`.
- [x] Deploy main commit `ac2996b` through GitHub Actions run `32292468778`.
- [x] Force-replay `hatvp-ingestion-r52xn`; verify all 13 layer tables and
  `state/latest.json` advanced with `SUCCESS_WITH_WARNINGS` and zero quality errors.
- [x] Redeploy the bridge, Worker, and frontend; verify the production health,
  aggregate, analysis, search/detail, and custom-domain routes return HTTP 200.
- [x] Repair the declarant timeline semantic model: rank interest and
  patrimonial filings independently, expose prior versions, show flagged source
  income unchanged, and replace the repeated timeline with the latest asset
  inventory.
- [x] Preserve asset event dates, precision, and source fields through Bronze,
  Silver, Gold, and the schema-evolution contract; verify Lecornu's 2002 value
  is a 21 January life-insurance subscription at age 15, not a 2002 filing.
- [x] Improve declaration search with clearer focus and result states, quick-start examples, and a reset action.
- [x] Replace the explorer placeholder with a bilingual, source-linked
  Highlights page for completed-year income changes, standout assets, and
  amendment history.
- [x] Restrict Highlights income and asset cards to the latest person-level
  declaration and current anomaly-registry records; keep superseded history
  in the audit layers.
- [x] Group the dashboard navbar into Explore, Declarations, and Data & methods
  with bilingual child labels while preserving all existing route URLs.
- [x] Publish the grouped dashboard navigation to GitHub Pages and verify the
  public custom-domain routes.
- [x] Pin frontend and Worker JavaScript dependencies to explicit compatible
  ranges instead of unconstrained `latest` specifications.
- [x] Deploy the current-issue Highlights release and verify the production
  API, latest-version filtering, source links, bilingual copy, and browser
  console output.
- [x] Deploy the approved latest-name+surname Highlights selection and verify
  that only the latest declaration per normalized name is analyzed, including
  the Warsmann and Ruelle regression cases.
- [x] Split official and Wayback/GitHub raw ingestion from retained-source
  processing, preserve source-specific hashes and raw zip bytes, and expose
  reproducible Make targets for each stage.
- [x] Deduplicate by declaration UUID before anomaly detection while retaining
  all source occurrences and provenance in Bronze/Silver history.
- [x] Add the bilingual pipeline-health API and frontend page with next-run
  countdown, source coverage, Bronze/Silver/Gold quality counts, and anomaly
  summary.
- [x] Deploy and force-replay the repaired timeline and pipeline-health release;
  record the main
  workflow, ingestion execution, 13-table load, state advancement, bridge
  revision, Worker version, frontend publish, and final Chrome audit.
- [x] Load the one-off Wayback/GitHub archive into production GCS/BigQuery and
  verify that the deployed health page reports both source IDs. The authorized
  ADC replay on 2026-08-23 persisted both raw sources, loaded all 13 tables,
  and Chrome confirmed both source rows on the public health page.
- [x] Link DOB leaderboard quality tags to their source declarations and remove
  the redundant five-year age-bin text summary from the analysis page.
- [x] Ingest the static HF/Wayback 2014 archive, process and deduplicate it with
  the retained-source cascade, and verify its source row on the deployed health
  page. Production replay on 2026-08-23 persisted the archive, loaded all 13
  tables, and Chrome confirmed the English and French source labels.
- [x] Explain the Internet Archive Wayback source and the static Hugging Face
  snapshot, including its `thefrenchartist` provenance, on the public About page.
- [x] Show raw ingested declaration counts beneath each deduplicated source
  count on the public pipeline-health page.

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
- [x] Include every annual `activProfCinqDerniereDto` remuneration in the unified income table.
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
- [x] Redeploy the mixed registry-date serialization fix and complete the forced production replay through Cloud Run execution `hatvp-ingestion-8lnvd`; verify all 13 BigQuery tables and `state/latest.json` advanced after the successful run.
- [x] Configure `HATVP_BUCKET`, `HATVP_PREFIX`, source URLs, pipeline version, and Git SHA.
- [x] Start with `HATVP_ENABLE_BIGQUERY=false` until BigQuery permissions are verified.
- [x] Execute the job manually with `--wait`.
- [x] Confirm the container exits with status 0 for a warning-bearing run (`hatvp-ingestion-q78jz`).
- [x] Confirm the application entrypoint exits non-zero for malformed input or structural quality failure; fixture tests cover both paths and the deployed container uses this entrypoint.
- [x] Confirm Cloud Logging contains structured events for downloads, hashes, quality, and final status (`hatvp-ingestion-hbt9d`).
- [x] Merge PR #27, deploy main commit `2669de9`, and force-replay the
  anomaly-lifecycle fix through Cloud Run execution `hatvp-ingestion-2sfxd`.

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

## 7. Enable and validate the current BigQuery Bronze foundation

- [x] Establish the current BigQuery tables `declarations`, `people`, `incomes`, and `assets` as the initial Bronze layer.
- [x] Confirm every Bronze table includes `snapshot_date` as a `DATE`.
- [x] Confirm Bronze tables are partitioned by `snapshot_date`.
- [x] Run the same snapshot twice and confirm the second load replaces that snapshot rather than duplicating rows.
- [x] Confirm BigQuery remains optional when `HATVP_ENABLE_BIGQUERY=false`.
- [x] Confirm a BigQuery failure prevents the latest state hash from advancing.
- [x] Make BigQuery Bronze loads add new staged columns and insert by explicit
  column name so schema evolution cannot fail on positional ordering.
- [x] Document the current Bronze table schemas and example queries.
- [x] Rebuild the Bronze `incomes` partition from both observed revenue
  streams and verify the annual `mandatElectifDto` rows in BigQuery.
- [x] Keep the Bronze layer version-complete: retain every declaration version
  present in every source snapshot and never collapse initial and amended
  declarations into one Bronze row.
- [x] Preserve the stable source identifiers, declaration-version metadata,
  snapshot provenance, source values, and raw record evidence needed to compare
  versions later.

BigQuery validation evidence for snapshot `2026-08-17`: dataset
`yahatvp-pipeline-eu:hatvp` was created in `europe-west1`; deployment
`1000d0b03` ran through GitHub Actions run `32049058688`; forced executions
`hatvp-ingestion-f6mdg` and `hatvp-ingestion-ts6jb` both succeeded with
`incomes=74,791`; the four partition counts and row fingerprints were identical
across runs; and unchanged execution `hatvp-ingestion-rmclb` emitted
`NO_CHANGE`. The source-linked report is
[`reports/03-validation/2026-08-17-bigquery-and-income-validation.md`](reports/03-validation/2026-08-17-bigquery-and-income-validation.md).

The historical validation report calls these tables “curated”; the next
architecture section deliberately reclassifies the existing physical tables as
Bronze inputs for anomaly detection. The report remains valid as evidence of
the current load behavior, partitioning, and idempotency.

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
- [x] Confirm the monitoring email channel delivers a test notification.
- [x] Verify the merged Cloud Run deployment emits the new quality telemetry.
- [x] Review quality reports after each weekly run.
- [x] Monitor recurrence and pursue source correction for the six duplicate declaration UUID groups; one pair differs only by trailing whitespace.
- [x] Monitor row counts and null rates for sudden changes.
- [x] Review HATVP schema changes before changing normalization logic.
- [x] Add a new fixture before fixing any newly observed source edge case.
- [x] Keep historical raw snapshots immutable.
- [x] Periodically review bucket lifecycle/retention policy without deleting required audit history.

The three alert policies and email channel were created and verified in
`yahatvp-pipeline-eu` on `2026-08-17`. Policy resources are recorded in the
monitoring runbook; the notification channel is
`projects/yahatvp-pipeline-eu/notificationChannels/15119347564909849591`.

Post-merge image `d2b4a9b` deployed successfully. Forced executions
`hatvp-ingestion-ff7gs` and `hatvp-ingestion-dqc6b` completed with exit 0; the
second emitted `quality_warning_streak` with `warning_streak=2`, 5,818 flagged
records, and zero quality errors.

Weekly operational monitoring completed on `2026-08-18`: quality reports for
`2026-08-16`, `2026-08-17`, and `2026-08-18` were reviewed; the latest two
snapshots have identical row counts and monitored null rates, zero quality
errors, and no flagged-record regression. Raw XML fingerprinting confirmed that
all six duplicate declaration UUID groups recur in all three snapshots. The
source-correction packet and evidence are in
[`reports/01-quality/2026-08-18-weekly-monitoring.md`](reports/01-quality/2026-08-18-weekly-monitoring.md);
no source or normalized row was altered.

Schema and raw-archive review completed on `2026-08-18`: the current 16-column
CSV header, XML root/top-level structure, and modeled DTO sections remain
compatible with `src/hatvp/pipeline.yml`; four unmodeled XML sections are
documented without changing normalization. The new schema fixture and existing
duplicate/trailing-whitespace fixture cover the observed source edges. GCS
versioning, generation-guarded immutable writes, and identical raw-object
checksums across snapshots `2026-08-16` through `2026-08-18` confirm that no
historical raw snapshot was overwritten. Evidence:
[`reports/05-schema/2026-08-18-schema-review.md`](reports/05-schema/2026-08-18-schema-review.md).

Read-only lifecycle review on `2026-08-18` confirmed the required `400d` rule
for `_Required` objects and the `30d` default rule without deleting or mutating
audit history.

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
- [x] Derive bounded gender values from XML `civilite` and carry them through Silver and Gold people tables.
- [x] Add the homepage male/female ratio pie chart and gender-by-job-position bar chart through a fixed aggregate API slice.
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
- [x] Publish and smoke-test the dashboard at `yahatvp.thefrenchartist.dev`
  with the GitHub Pages custom domain and HTTPS enabled.
- [x] Add a localized declaration search page with parameterized public-field
  matching and result links to source XML detail pages.
- [x] Read one matched declaration node from the immutable GCS XML snapshot and
  render it in a dedicated escaped source viewer; fixture coverage includes the
  UUID match and private-field exclusion.
- [x] Deploy the search/XML bridge, Worker, and frontend changes after merge and
  smoke-test a live declaration search plus source XML detail route.
- [x] Split the frontend monolith into focused pages, components, i18n context,
  and a cancellable resource hook while keeping each TypeScript source file
   below the 100-line review budget.
- [x] Replace the declaration raw-XML-first detail page with a schema-aware
  interface that renders identity, source metadata, mandates, annual amounts,
  activities, interests, assets, liabilities, attachments, empty sections, and
  a collapsed raw-XML audit view; cover five live schema variants with fixture
  and responsive regression tests.
- [x] Restore accent-insensitive BigQuery matching for the default age-analysis
  query and declaration search; fixture tests cover the generated SQL.
- [x] Add the localized static `/quality-issues` register from a minimal local
  JSON file, keeping only issue type, contact date, public HATVP links, and
  solved state; calculate unresolved duration from the contact date and exclude
  the source CSVs and correspondence.
- [x] Replace the declarant age timeline's cross-version sums and repeated DTO
  cards with independently selected declaration families, source-reported
  income stories, localized asset groups, and expandable declaration history.
- [x] Cover the real Lecornu-shaped payload in bridge, Worker, and frontend
  tests: seven income years, no occupation counts, no visible DTO jargon, exact
  age 15 for the 2002 subscription, and no cross-version asset duplication.
- [x] Add a fixed `/v1/dashboard/highlights` bridge query and public Worker
  route for the largest completed-year income changes, highest absolute asset
  values, and most-amended identities without exposing contact data.
- [x] Turn `/explore` into an editorial Highlights page with localized context,
  review-state labels, and direct links to each immutable declaration source.

Static quality-register evidence (2026-08-19): the frontend fixture suite passes
with 19 tests, the production build succeeds, the local page renders ten rows
with zero solved issues, calendar durations, and no mobile page overflow.

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

Custom-domain deployment evidence (2026-08-18): Cloud Run bridge revision
`hatvp-dashboard-api-00007-pw7` and Worker version
`c939a4fe-9afc-4097-9fa9-c059d1161e47` are serving. GitHub Pages is configured
for `yahatvp.thefrenchartist.dev` with an approved certificate and enforced
HTTPS; the page returned HTTP 200, references the deployed `favicon.svg`, and
the Worker overview slice returned HTTP 200 with the custom-domain CORS header.

Highlights deployment evidence (2026-08-20): Cloud Run bridge revision
`hatvp-dashboard-api-00015-vdp`, Worker version
`750fdfb2-e9b6-497f-b4b9-a19483ceab98`, and GitHub Pages commit
`5fd9e899520d7512db2081868e10752fc21e493e` are serving. The public Highlights
route returned snapshot `2026-08-19` with 8 income changes, 8 asset records, and
8 amended identities. Health, aggregate, analysis, search/detail, and
Highlights smoke routes all returned HTTP 200. Production browser verification
confirmed the new bundle, all 24 cards, source-detail navigation, bilingual
copy, zero desktop overflow, and no console errors. No ingestion replay was
performed for this dashboard-only release. Main workflow run `32310774561`
passed its tests, configuration gate, image build/push, and Cloud Run Job
deployment for commit `ed027a7`.

## 11. BigQuery tutorial

- [x] Add ten atomic BigQuery tutorial queries with matching CSV results for the
  validated `2026-08-18` snapshot.
- [x] Document the query progression, fixed snapshot convention, stable-UUID
  joins, and CSV regeneration commands.

## 12. BigQuery Bronze → Silver → Gold anomaly architecture

This is the implemented analytical model for all declaration versions. It changes
the role of the existing BigQuery tables without deleting or rewriting their
history:

| Layer | Role | Required behavior |
| --- | --- | --- |
| **Bronze** | The existing BigQuery `declarations`, `people`, `incomes`, and `assets` tables. | Version-complete source-shaped records, partitioned by `snapshot_date`, with source identifiers, provenance, and observed values retained. Bronze is not a latest-person table. |
| **Silver** | A cleaned-up and anomaly-annotated representation of every Bronze declaration version. | Run the anomaly rules below across the full history. Keep the observed value and source evidence; add flags and eligibility metadata. Do not repair, replace, silently drop, or deduplicate an anomalous value. |
| **Gold** | The latest declaration for each declarant, derived from Silver. | Select the latest applicable declaration/version for each declarant and role/period grouping. Expose current anomalies for reporting and metric eligibility, while retaining all historical anomalies in Silver. |

“Cleaned-up” in Silver and “clean data” in Gold mean structurally usable,
traceable data with explicit anomaly flags—not values that the pipeline has
automatically corrected. A future feature-specific clean view may be created
later, but it is outside this phase. An anomaly must remain visible even when a
metric query excludes it.

### 12.1 Bronze contract and migration boundary

- [x] Adopt the existing four physical BigQuery tables as the initial Bronze
  layer for this design; do not treat them as the final Gold output.
- [x] Keep the current exact-snapshot loading and partition replacement
  guarantees while the downstream layers are added.
- [x] Inspect the observed BigQuery schemas and declaration-version fields
  before choosing physical names for the new layers. Prefer an explicit,
  stable convention such as separate Bronze/Silver/Gold datasets or clearly
  prefixed tables; do not rename the existing Bronze tables until readers and
  dashboard queries have a migration path.
- [x] Confirm the Bronze grain for each table and document how a declaration,
  declarant, role, period, amendment, and source snapshot are identified from
  the actual HATVP schema.
- [x] Preserve all source versions across snapshots, including initial,
  amended, and superseding declarations. A later declaration must not erase
  the earlier Bronze record.
- [x] Keep source values, normalized values, raw record JSON where available,
  source file/format, source URL or object, source snapshot date, stable IDs,
  and parser/pipeline versions available to Silver and the anomaly evidence.
- [x] Treat the existing GCS raw archive as immutable provenance behind the
  Bronze input. Never use anomaly processing as a reason to overwrite raw XML,
  CSV, or other source evidence.

### 12.2 Silver: historical anomaly detection and flags

- [x] Build Silver tables from Bronze at the same historical declaration
  version grain. Silver must contain every Bronze version, including versions
  that are later superseded.
- [x] Apply deterministic structural normalization only where already defined
  by the source contract, such as whitespace, missing-marker, date, and French
  number parsing. Preserve the original value beside any normalized value.
- [x] Add row-level and field-level anomaly metadata without changing the
  observed value. At minimum, expose whether the field has an active anomaly,
  whether it is eligible for a metric, the applicable rule IDs, and a link to
  the anomaly registry evidence.
- [x] Run all anomaly rules against all available historical declaration
  versions, not only the latest snapshot and not only the latest declaration.
- [x] Compare a person’s values across years, declaration versions, roles, and
  relevant periods using stable HATVP identifiers and declaration metadata.
  Do not use first-name plus surname as the sole identity key; unresolved
  identity matches must become review flags.
- [x] Compare initial and amended declarations explicitly. Determine whether a
  later declaration supersedes an earlier anomaly, but retain the earlier row
  and anomaly permanently in the historical audit trail.
- [x] Compare CSV, XML, and PDF values when an authoritative representation is
  available. Store the source format, location, and conflicting values in the
  evidence; absence of a source format is not itself a contradiction.
- [x] Keep anomalous rows in Silver. Do not automatically correct a decimal,
  digit, concatenation, salary, geography, date, identifier, or other source
  value; do not silently delete or deduplicate a record because a rule fired.
- [x] Make Silver writes deterministic and idempotent by snapshot and stable
  source identifiers. A retry must not create duplicate anomaly rows.

### 12.3 Gold: latest declaration per declarant

- [x] Define the ordering used to select the latest declaration from the
  observed HATVP amendment/version fields. “Latest” must be evaluated within
  the same declarant plus role/mandate/period context, rather than comparing
  unrelated declarations.
- [x] Resolve the declarant using stable source identifiers wherever available;
  retain an explicit review state when the source does not provide a reliable
  identity key.
- [x] Derive Gold tables or views from Silver so that each declarant has only
  the latest applicable declaration/version for the documented Gold grain.
  Keep child-table joins aligned to that selected declaration version.
- [x] Carry Silver anomaly status into Gold. Gold must show whether an anomaly
  affects the latest declaration and whether the affected field is eligible
  for metrics; Gold must not contain an automatically repaired replacement
  value.
- [x] Make the latest declaration determine whether an anomaly is currently
  active for reporting. If an amended declaration corrects a historical value,
  mark the older anomaly as superseded/resolved in the registry while keeping
  it in Silver and the audit trail.
- [x] Report only anomalies attached to the latest applicable declaration in
  Gold to HATVP. Use Silver for historical anomaly reports, recurrence
  analysis, source-correction evidence, and auditability.
- [x] Ensure Gold selection is repeatable, partition-aware, and idempotent;
  rerunning the same source snapshot must produce the same latest-declarant
  rows and anomaly statuses.
- [x] Update the dashboard and analytical examples to read Gold for current
  declarant metrics after Gold is validated. Historical trend and anomaly
  investigations must read Silver or the anomaly registry explicitly.

### 12.4 Anomaly rules to implement between Bronze and Silver

Each rule must emit a flag and evidence, never an automatic correction. The
following rule IDs are the implemented stable identifiers; keep them stable once
reports or external follow-up refer to them.

1. **`COMP_YOY_CHANGE` — abnormally large year-over-year compensation change**

   - Flag compensation that is multiplied or divided by approximately 10 or
     more compared with the person’s historical value.
   - Flag a sudden jump or drop inconsistent with the person’s own history.
   - Flag an abrupt break after several stable years.
   - Record the comparison years, prior values, ratio, absolute change, role,
     and period. Thresholds must be configurable and reviewed against the
     observed HATVP distribution so legitimate changes are not silently
     treated as errors.

2. **`COMP_IMPLAUSIBLE_AMOUNT` — obviously implausible compensation amount**

   - Flag annual compensation in the hundreds of thousands or millions when
     that amount is highly unlikely for the role.
   - Compare against the person’s previous years and comparable office holders
     where a defensible comparison group exists.
   - Preserve the observed amount and the expected range or comparison basis;
     do not cap, winsorize, or replace it.

3. **`COMP_FACTOR_ERROR` — factor-of-10 or missing-decimal-separator error**

   - Test whether multiplying or dividing the observed value by 10, 100, or
     another configured decimal factor produces a value close to the person’s
     historical values or a defensible comparison range.
   - The candidate corrected value is evidence only. Never write it back as the
     value used by default.
   - Preserve the locale-aware raw text so a French decimal/thousands separator
     issue can be distinguished from a source-entry error.

4. **`COMP_CONCATENATED_VALUE` — accidental concatenation of values**

   - Flag unusually long numeric values that may contain two fields joined
     together.
   - Test whether a plausible salary prefix or suffix is followed by unrelated
     digits, using source field widths, neighboring fields, historical values,
     and raw source text as evidence.
   - Keep the entire observed value and the candidate segments in the anomaly
     evidence; never split it automatically.

5. **`COMP_DIGIT_EDIT` — extra or missing digit**

   - Flag a value that is one digit-edit away from a historically plausible
     amount, especially an inserted or deleted `0`.
   - More generally test one-digit insertion, deletion, substitution, and
     transposition candidates where the comparison is explainable.
   - Store the candidate value and edit operation as evidence only; do not
     replace the observed value.

6. **`COMP_CONFLICT_SAME_PERIOD` — conflicting values for the same year**

   - Flag the same person, role, and year/period when different compensation
     values appear across declarations.
   - Explicitly compare initial and amended declarations and retain every
     observed value with its declaration identifier and source snapshot.
   - Let the latest applicable declaration decide current Gold status; keep the
     conflict and all earlier values in Silver.

7. **`COMP_SUPERSEDED_DECLARATION` — historical error corrected by amendment**

   - Do not treat every anomalous historical declaration as an active current
     error.
   - Identify the latest declaration for the same person, role, and period.
   - Keep the historical anomaly in the audit trail, link it to the replacing
     declaration, and mark it superseded/resolved when the latest evidence
     supports that conclusion.
   - If the latest declaration remains anomalous, keep the anomaly active in
     Gold and report it through the latest-version workflow.

8. **`GEO_DEPARTMENT_MUNICIPALITY` — department inconsistent with municipality or office**

   - Flag a department code that does not match the declared municipality,
     office, or other authoritative geography.
   - Compare geographic information across CSV, XML, and PDF representations
     when present, retaining each source value and the reference used for the
     mismatch.
   - Do not infer or overwrite a department merely because a municipality has
     a likely match.

9. **`PERSON_DOB_IMPLAUSIBLE` — impossible or highly implausible date of birth**

   - Flag a future date, a clearly anomalous year, or an age incompatible with
     holding the relevant public office.
   - Compare dates of birth across declarations for the same person and flag
     conflicting values.
   - Preserve the source date, parsed date, declaration version, and evidence
     used for the plausibility decision.

10. **`SOURCE_CROSS_FORMAT` — CSV/XML/PDF inconsistency**

    - Flag contradictory identifiers, geography, dates, mandates, or
      compensation values for the same record across CSV, XML, and PDF.
    - Record all conflicting representations and source locations, with a
      clear indication of which declaration/version each value belongs to.
    - Do not choose a winning format automatically; source precedence must be a
      documented review decision.

11. **`ANOMALY_KNOWN` — previously detected or reported anomaly**

    - Maintain a persistent anomaly registry keyed, where possible, by
      `person_id + field + period + anomalous_value`, supplemented by
      declaration/version and rule identifiers when needed to prevent false
      matches.
    - Link a new occurrence to the known anomaly instead of generating an
      indistinguishable duplicate alert after every refresh.
    - Do not hide known anomalies from Silver or Gold; suppress only redundant
      notifications while retaining occurrence counts and last-seen evidence.

12. **`ANOMALY_REGRESSION` — a previously corrected anomaly reappears**

    - If an anomalous value disappears in a later declaration/version and then
      reappears, flag the new occurrence as a regression.
    - Link the regression to the original anomaly, the intervening corrected
      declaration, and the new source snapshot.
    - Reactivate the issue for Gold reporting when the reappearing value is in
      the latest applicable declaration.

### 12.5 Anomaly registry contract and lifecycle

Each anomaly record should contain at least:

```text
rule_id
severity
person_id
field
period
observed_value
expected_value_or_range
evidence
first_seen
last_seen
is_latest_declaration
superseded_by
previously_reported
status
```

The implementation should also retain the following provenance and lifecycle
fields where available:

```text
anomaly_id
anomaly_key
declaration_id
declaration_version
declarant_key
role_or_mandate
source_snapshot_date
source_format
source_uri_or_object
source_location
candidate_value_or_range
metric_eligible
active_in_gold
detected_at
reviewed_at
```

- [x] Define a deterministic `anomaly_key` and registry upsert behavior so
  repeated weekly snapshots update `last_seen` rather than creating duplicate
  alerts.
- [x] Define the lifecycle statuses at minimum as active, superseded/resolved,
  known/reported, and regression. Keep status transitions explainable from
  declaration-version evidence.
- [x] Set `is_latest_declaration` and `active_in_gold` from the same version
  ordering used by Gold; do not maintain two competing definitions of latest.
- [x] Set `previously_reported` from the registry and preserve first/last-seen
  dates across snapshots.
- [x] Store enough evidence to reproduce each flag from immutable source bytes,
  including source locations and the compared values.
- [x] Keep historical anomaly records even after they are superseded. A
  superseded anomaly may stop being an active Gold alert, but it must remain
  queryable in Silver and the registry.
- [x] Make registry updates part of the required processing gate. If anomaly
  detection or registry persistence fails, do not advance `state/latest.json`.

### 12.6 Metric eligibility and reporting policy

- [x] Treat anomaly detection as a flagging system, not an automatic correction
  system. No rule may silently change, impute, cap, round, split, or delete a
  source value.
- [x] Add field-level metric eligibility so a metric can exclude an anomalous
  compensation, date, geography, or identifier without discarding unrelated
  fields from the same declarant.
- [x] Define the default policy that unresolved or active anomalies affecting a
  metric make that field ineligible for the metric. Keep the row available for
  audit and anomaly counts.
- [x] Make Gold-facing metric queries filter by the explicit eligibility/status
  fields rather than reimplementing anomaly logic ad hoc.
- [x] Report current anomalies from the latest Gold declaration/version to
  HATVP. Report historical and superseded anomalies from Silver and the
  registry for auditability and source-correction follow-up.
- [x] Do not report a historical anomaly as a current issue when a later
  declaration has superseded it, unless the later declaration still carries
  the anomaly or it has regressed.
- [x] Keep future feature-specific clean versions out of this phase. If they are
  later needed, build them as explicitly named derived views/tables with the
  original observed value, anomaly links, and transformation rules preserved.

### 12.7 Implementation, backfill, and acceptance checks

- [x] Add a schema/version design note before changing the physical BigQuery
  layout. Include the Bronze-to-Silver field mapping, Gold grain, identity and
  amendment ordering, anomaly registry key, and retention policy.
- [x] Implement the anomaly rules behind small, testable HATVP-specific
  components. Do not introduce a general-purpose orchestrator.
- [x] Make the `PERSON_DOB_IMPLAUSIBLE` maximum age threshold YAML-configured,
  typed, environment-overridable, and source-preserving.
- [x] Add fixtures for stable historical compensation, factor-of-10 errors,
  concatenated values, digit edits, same-period conflicts, amended
  declarations, geography mismatches, impossible/conflicting birth dates,
  cross-format conflicts, known anomalies, and regressions.
- [x] Test that every fixture is flagged without changing its observed value and
  that all source/provenance fields remain available.
- [x] Test that a corrected amended declaration supersedes the historical
  anomaly, while the historical row remains in Silver and the registry.
- [x] Test that a reappearing value is marked as a regression and is active in
  Gold when it is the latest applicable declaration.
- [x] Test anomaly-registry idempotency across repeated snapshots and retries;
  repeated input must update occurrence metadata rather than duplicate alerts.
- [x] Preserve each anomaly’s original `rule_id` when known or regression
  lifecycle aliases are emitted, while retaining their lifecycle status.
- [x] Add direct unit coverage for DOB reference-date boundaries and both
  known and regression registry lifecycle aliases.
- [x] Test Gold uniqueness: one latest applicable declaration per declarant at
  the documented grain, with child records joined to that version.
- [x] Test metric queries exclude flagged values through eligibility fields and
  never depend on silently corrected values.
- [x] Backfill Silver and the anomaly registry from every retained Bronze
  snapshot before enabling Gold reporting. Record the backfill range and
  source hashes.
- [x] Build Gold from the backfilled Silver history, then compare current Gold
  row counts and latest-version choices against source-linked review evidence.
- [x] Run a forced replay and an unchanged-input replay. Confirm Bronze,
  Silver, Gold, registry contents, partition counts, anomaly statuses, and
  `state/latest.json` behavior are deterministic and idempotent.
- [x] Update README, code/module names, dashboard queries, permissions, and
  validation reports from the transitional “curated” terminology to the final
  Bronze/Silver/Gold terminology once the implementation is deployed.

Acceptance evidence is recorded in
[`reports/03-validation/2026-08-18-silver-gold-validation.md`](reports/03-validation/2026-08-18-silver-gold-validation.md),
including the forced live-source run, unchanged replay, retained-Bronze
backfill, layer counts, registry counts, and dashboard/build checks.

## 12.8 HATVP anomaly handoff

- [x] Query the 2026-08-19 BigQuery Gold and anomaly-registry snapshot and
  preserve the SQL used for the review.
- [x] Exclude current issue-register names, the generic same-period conflict
  family, the DOB issue family, superseded-declaration flags, and registry rows
  already marked `previously_reported`.
- [x] Prepare ten source-linked declarations using the latest version per
  normalized declarant name+surname and record the evidence in
  [`reports/06-hatvp/2026-08-19-hatvp-anomaly-shortlist.md`](reports/06-hatvp/2026-08-19-hatvp-anomaly-shortlist.md).
- [ ] Complete human source-document review and any external HATVP follow-up;
  this repository report does not assert that a flagged value is erroneous.

## Later, only if needed

- [ ] Add semantic/content hashes after the exact-byte hash path is stable.
- [ ] Add richer schema-drift reporting for new XML sections and fields.
- [ ] Add a small operational dashboard from Cloud Logging and quality reports.
- [ ] Add partition-aware BigQuery retention and cost controls.
- [ ] Add data catalog/documentation for the normalized tables.
