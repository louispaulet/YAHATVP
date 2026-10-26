# Experience note: HATVP refreshes and unpublished declaration search

**Purpose:** project memory for the investigation completed on 2026-10-27. This
is a practical note, not a separate skill or the source of truth for current
configuration. Check the linked code, README, `agents.md`, and current production
state before reusing operational steps.

## Short version

- The scheduled jobs on October 12, 19, and 26 all completed with `NO_CHANGE`.
  HATVP's official XML and CSV bytes had not changed.
- Historical Silver sample counts still went down: 17,898 distinct declarations
  on August 23, 17,884 on August 28, and 17,812 on October 6. So “no new source
  files” was not the whole explanation; the previous result did not meet the
  intended keep-old-public-declarations behavior.
- Searching Gold hid declarations outside the current analytical selection.
  Declaration search and detail now use the latest cumulative Silver partition;
  dashboard counts and metrics use Gold. Search does not scan every snapshot
  partition: the current Silver partition carries the preserved versions.
- The corrected October 27 snapshot has 17,900 distinct declarations in Silver.
  It includes the example below, whose source version is marked unpublished.
- One October 26 interim partition has incorrect publication-status
  assignments. The current API selects the corrected October 27 partition.
  Keep the interim partition visible as historical evidence; do not mistake it
  for the live result or delete it casually.

The complete evidence, source hashes, deployments, and count table are in the
[validation report](../reports/03-validation/2026-10-27-publication-search-validation.md).

## What happened

| HATVP job date | Execution | Result |
| --- | --- | --- |
| 2026-10-12 | `hatvp-ingestion-m4vfp` | `NO_CHANGE` |
| 2026-10-19 | `hatvp-ingestion-92nwm` | `NO_CHANGE` |
| 2026-10-26 | `hatvp-ingestion-wpvpm` | `NO_CHANGE` |

The observed source hashes were XML
`a042d437b9b05f0af0aa93e7e95f18b038fb21c0eb8a3b69f499dc1e66bcd9cb` and CSV
`781fc5e54b20bda1be5b095dcd76bbfee674cee342ec36e694099f6781704597`. The XML
was last captured in the October 5 official source snapshot.

| BigQuery snapshot | Silver rows | Silver distinct UUIDs | Gold rows | Interpretation |
| --- | ---: | ---: | ---: | --- |
| 2026-08-19 | 6,611 | 6,605 | 6,615 | Legacy snapshot |
| 2026-08-23 | 31,578 | 17,898 | 17,899 | Legacy snapshot |
| 2026-08-24 | 31,578 | 17,898 | 17,950 | Legacy snapshot |
| 2026-08-28 | 31,497 | 17,884 | 17,885 | Legacy snapshot |
| 2026-08-30 | 31,497 | 17,884 | 17,957 | Legacy snapshot |
| 2026-10-06 | 30,946 | 17,812 | 17,813 | Legacy snapshot |
| 2026-10-26 | 38,133 | 17,900 | 17,985 | Interim; publication statuses reversed |
| **2026-10-27** | **38,133** | **17,900** | **18,005** | **Corrected current snapshot** |

The word “sample” in count discussions means a distinct `declaration_uuid`.
Silver row counts are larger because Silver retains multiple versions and
source records. Gold is the current analytical selection; its counts are not a
cumulative archive and should not be expected to rise monotonically. Legacy
partitions lacked publication-status fields, so a missing status there is
unknown, not an unpublished-row count of zero.

## Why the result was surprising

1. **The search source was wrong for the question.** Gold represents the
   current analytical selection. A version missing from the latest HATVP
   export can be present in Silver while absent from a current Gold selection.
   This request needed a historical/publication search, so the search and detail
   routes were changed to use Silver. Gold remains the source for current
   dashboard statistics.
2. **The first lifecycle replay classified rows incorrectly.** The arguments
   passed to `publication_snapshot` were reversed at one call site. Fixture
   tests now assert the lifecycle contract; the call was corrected and the
   October 27 partition was produced with the corrected code. The October 26
   interim BigQuery partition remains but is not the maximum snapshot date.
3. **Corrected replay attempts hit a memory limit.** Even at the configured 8
   vCPU / 32 GiB profile, logs showed signal 9 while writing Silver.
   Serialization was changed to lower peak memory by writing layers in
   sequence, releasing large intermediate history, and avoiding redundant
   wide-row copies. Execution `hatvp-ingestion-fzrln` then loaded all 13 BigQuery
   tables and advanced `state/latest.json` to October 27.
4. **A `NO_CHANGE` result only describes the downloaded inputs.** It does not
   prove that older curated partitions are cumulative or that a search route
   queries the appropriate layer. Check source hashes, layer contents, and the
   user-visible query separately.

## Example to retest

- UUID: `1b384fad-9ae2-4cea-a5b3-812244f0628d`
- Declarant: Françoise DUMONT
- Declaration: amended interests and activities, deposited June 29, 2026
- Preserved source snapshot: August 30, 2026; first observed online August 23
- Current status: unpublished, absent from the October 5 official XML
- [Open the production search](https://yahatvp.thefrenchartist.dev/#/search?q=1b384fad-9ae2-4cea-a5b3-812244f0628d)

The exact date HATVP stopped including it is not known. In the production check,
Chrome found one result, showed “Not in latest HATVP extract”, opened the
preserved detail and XML, and had no console errors. The Worker search response
reported `publicationStatus: "unpublished"` and
`sourceSnapshotDate: "2026-08-30"`.

## How to debug the next refresh or missing declaration

### 1. Check the execution and source-change events

Use the repository's Cloud Run instructions in `README.md` / `ops/monitoring/README.md`.
The standard read-only checks are:

```bash
gcloud run jobs executions list \
  --job="$JOB_NAME" \
  --region="$REGION"

gcloud logging read \
  'resource.type="cloud_run_job" AND resource.labels.job_name="hatvp-ingestion"' \
  --limit=50 \
  --format=json
```

Look for `download_complete`, `hash_comparison`, `quality_complete`,
`bigquery_load_complete`, `pipeline_complete`, and `pipeline_failed`. Compare
the exact source hashes and snapshot dates. Only treat a replay as complete if
all required table loads succeeded and `state/latest.json` advanced afterward.
If a job fails, do not infer success from partial GCS output.

For local GCS/BigQuery work use Application Default Credentials. A `gcloud auth
login` session is not a substitute for ADC. Follow the repo's identity policy;
never create or request a long-lived service-account JSON key.

### 2. Count samples and rows separately

For a new audit, query each snapshot partition and group by `snapshot_date`.
This example distinguishes total Silver rows, unique declarations, lifecycle
rows, and null lifecycle values:

```sql
SELECT
  snapshot_date,
  COUNT(*) AS silver_rows,
  COUNT(DISTINCT declaration_uuid) AS declaration_samples,
  COUNTIF(publication_status = 'online') AS online_rows,
  COUNTIF(publication_status = 'unpublished') AS unpublished_rows,
  COUNTIF(publication_status IS NULL) AS lifecycle_unknown_rows
FROM `yahatvp-pipeline-eu.hatvp.silver_declarations`
GROUP BY snapshot_date
ORDER BY snapshot_date;
```

Run a corresponding `COUNT(*)` and `COUNT(DISTINCT declaration_uuid)` against
`gold_declarations` when checking current analytical membership. Do not compare
Gold row totals as if they were a cumulative history. In Silver, online and
unpublished counts are row-level counts; they need not sum to unique UUIDs.

### 3. Check the deployed API, then check the UI

The deployed Worker routes used in this investigation were:

```bash
curl -fsS 'https://hatvp-transparency-api.louispaulet13.workers.dev/api/dashboard/overview?schema=6'
curl -fsS 'https://hatvp-transparency-api.louispaulet13.workers.dev/api/dashboard/search?q=1b384fad-9ae2-4cea-a5b3-812244f0628d&schema=6'
```

The overview should identify the latest snapshot and return current Gold-backed
counts. Search should return the preserved result and its publication/source
snapshot metadata. Then use Chrome on the public website: search the UUID, open
the result, check the publication context, expand “View source XML”, and inspect
the console and network response. A previously open browser tab served a cached
September frontend asset during this incident; a fresh browser context loaded
the current asset from the ordinary site URL. If UI text or badges disagree with
the current API, hard reload or retest in a clean context before debugging the
BigQuery data again.

### 4. Follow the layer's source code and fixtures

- Publication status and timestamps: `src/hatvp/layers/publication.py`.
- Silver history and Gold selection: `src/hatvp/layers/silver.py`,
  `src/hatvp/layers/gold.py`, and `src/hatvp/layers/gold_selection.py`.
- Pipeline build and write ordering: `src/hatvp/pipeline/flow.py` and
  `src/hatvp/pipeline/layers.py`.
- Dashboard search SQL:
  `website/hatvp-transparency-dashboard/backend/bigquery-bridge/query_search.py`.
- Declaration detail SQL and preserved XML retrieval:
  `query_declaration.py` and `raw_xml.py` in that same bridge directory.
- Dashboard aggregate table mapping:
  `website/hatvp-transparency-dashboard/backend/bigquery-bridge/query_support.py`
  maps aggregate table names to `gold_*`.
- Fixture contracts: `tests/test_publication.py`,
  `tests/test_publication_pipeline.py`, and bridge/frontend `test_*.py` files.

Use fixtures for normal tests; tests should not depend on live HATVP, GCS, or
BigQuery. For focused deployment checks, `make backend-test` covers Worker
tests/typecheck and bridge tests; `make frontend-test` runs frontend tests and a
production build. The repository targets `make backend-deploy` and
`make frontend-deploy VITE_API_BASE_URL="https://hatvp-transparency-api.louispaulet13.workers.dev"`
publish the backend/Worker and frontend respectively. Deployment and production
replay are live mutations: use them only when the task calls for that change,
then record the deployed revision, API results, and successful pipeline state.

## Outcome and remaining watch item

The dashboard was deployed with Cloud Run bridge revision
`hatvp-dashboard-api-00037-xrv`, Worker version
`e976a62c-b3cc-4ea9-a17e-bc3cabff1ea5`, and a new frontend asset. CI run
`40416843578` passed; the production replay completed with zero quality errors.
It still reported 40,156 warnings and a 23-run warning streak. Treat warnings
and flagged rows as review signals; do not silently remove or “correct” source
records. The current follow-up is tracked in `TODO.md`.
