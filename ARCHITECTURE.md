# YAHATVP architecture

YAHATVP is a small, auditable pipeline for the public datasets published by the
French Haute Autorité pour la Transparence de la Vie Publique (HATVP). It has
two related products:

1. a source-preserving ingestion and analytical pipeline; and
2. a read-only transparency dashboard built from the analytical outputs.

This document explains how the repository is divided, how data moves through
the system, and where the important safety boundaries are. The root
[`README.md`](README.md) remains the operational quick start and command
reference.

## Architectural principles

- Keep the pipeline HATVP-specific and small. The repository contains an
  in-process cascade, not a general workflow platform.
- Preserve the exact raw bytes, source ID, snapshot date, hashes, and source
  provenance. Normalization must never erase the published value.
- Treat official HATVP data and the GitHub/Wayback archive as separate sources.
  They share the processing cascade but do not share raw paths or ingestion
  state.
- Run quality checks before analytical publication. Suspicious records are
  retained and flagged; they are not silently corrected or deleted.
- Advance `state/latest.json` only after every required processing stage and
  optional BigQuery load succeeds.
- Expose fixed, read-only dashboard slices. The dashboard never accepts
  arbitrary SQL and never receives the full source XML feed.

## System at a glance

The official source is ingested weekly. The Wayback/GitHub archive is a
reproducible one-off input, but after ingestion it follows the same processing
cascade as the official source.

```text
                         WEEKLY OFFICIAL PATH
  +--------------------+       +---------------------+
  | Cloud Scheduler    | ----> | Cloud Run Job       |
  | Monday 07:00 Paris |       | `pipeline-run`      |
  +--------------------+       +----------+----------+
                                          |
                                          v
                              +-----------+-----------+
                              | Official HATVP files |
                              | XML + CSV             |
                              +-----------+-----------+
                                          |
                                          v
  ONE-OFF ARCHIVE PATH          +---------+----------+
  +-------------------------+   | Raw ingestion      |
  | `make pipeline-archive` |-->| hash, validate,    |
  | declarations.xml.zip    |   | retain immutable   |
  +-------------------------+   +---------+----------+
                                          |
                                          v
                              +-----------+-----------+
                              | Latest raw source    |
                              | snapshots in GCS    |
                              +-----------+-----------+
                                          |
                                          v
                              +-----------+-----------+
                              | Processing cascade   |
                              | all latest sources   |
                              +-----------+-----------+
                                          |
             +----------------------------+----------------------------+
             |                            |                            |
             v                            v                            v
      +------+-------+             +------+-------+             +------+-------+
      | Bronze       |             | Silver       |             | Gold         |
      | source rows  |             | flags and    |             | latest       |
      | complete     |             | eligibility  |             | analytical   |
      +------+-------+             +------+-------+             +------+-------+
             |                            |                            |
             +----------------------------+----------------------------+
                                          |
                                          v
                              +-----------+-----------+
                              | Quality report,       |
                              | anomaly registry,     |
                              | BigQuery, state       |
                              +-----------------------+
```

The local CLI uses the same functions as the Cloud Run Job. `--local-output`
selects the filesystem adapter; otherwise `HATVP_BUCKET` selects the GCS
adapter. This keeps fixture tests and production execution on one code path.

## Repository map

```text
YAHATVP/
|-- README.md                         operational guide
|-- ARCHITECTURE.md                   this design reference
|-- agents.md                         repository workflow constraints
|-- TODO.md                           project execution checklist
|-- CHANGELOG.md                      dated user-visible changes
|-- Makefile                          pipeline and dashboard commands
|-- Dockerfile                         Cloud Run Job image
|-- .github/workflows/deploy.yml      CI, image, and Job deployment
|-- src/hatvp/
|   |-- main.py                        CLI entrypoint and stage dispatch
|   |-- config.py                      typed environment/YAML settings
|   |-- pipeline.yml                   observed schema and runtime defaults
|   |-- download/                      HTTP download and response validation
|   |-- parser/                        HATVP XML/CSV parsing components
|   |-- normalize.py                   source-value normalization helpers
|   |-- pipeline/                      ingestion, processing, state, artifacts
|   |-- layers/                        Bronze/Silver/Gold and anomaly rules
|   |-- quality/                       quality checks and telemetry
|   |-- storage/                       local and GCS artifact adapters
|   |-- tables/                        Parquet columns and schemas
|   |-- bigquery/                      staging and partition replacement
|   `-- triage/                        source-linked quality review reports
|-- website/hatvp-transparency-dashboard/
|   |-- frontend/                      React/Vite dashboard
|   `-- backend/
|       |-- worker/                    Cloudflare Worker public API facade
|       `-- bigquery-bridge/           fixed BigQuery/GCS read-only service
|-- tests/                             fixture-only Python contracts
|-- reports/                           quality-triage documentation and evidence
`-- tutorial/                          example SQL and exported analyses
```

### Python package responsibilities

The public package facades in `__init__.py` files keep imports stable. Focused
modules below them hold the implementation so each area can be tested without
turning `main.py` into an application monolith.

| Package | Responsibility | Important entry points |
| --- | --- | --- |
| `download` | Download files with timeouts, retries, status checks, and hashes. | `download_to_path`, dataset validation |
| `parser` | Stream HATVP XML and parse the semicolon-delimited CSV into source-shaped rows. | `parse_sources` |
| `pipeline` | Coordinate ingestion, source materialization, processing, artifacts, and state. | `main.py`, `orchestrator.py`, `processing.py` |
| `layers` | Build Bronze, Silver, Gold, and anomaly-registry rows. | `flow.py`, `gold_selection.py`, anomaly modules |
| `quality` | Check schema, identifiers, coverage, nulls, duplicates, numeric values, and regressions. | `run_quality_checks` |
| `storage` | Provide the same artifact-store contract for local files and GCS. | `LocalArtifactStore`, `GCSArtifactStore` |
| `tables` | Define table columns and write Parquet files. | `write_table`, `write_parquet` |
| `bigquery` | Load Parquet through staging tables and replace one snapshot partition. | `load_parquet_tables` |
| `triage` | Match quality flags back to immutable source evidence and produce review reports. | `python -m hatvp.triage` |

`pipeline/orchestrator.py` is only an in-process coordinator. It does not
introduce Airflow, Composer, Dataflow, or another external orchestrator.

## Source ingestion and processing

### Source-specific raw contracts

Each source has its own latest state and raw namespace:

```text
Official HATVP source
  raw/snapshot_date=YYYY-MM-DD/
    declarations.xml
    liste.csv
    metadata.json
  state/sources/hatvp_website/latest.json

Wayback/GitHub archive
  raw/source=wayback_github/snapshot_date=YYYY-MM-DD/
    declarations.xml
    declarations.xml.zip       original immutable archive bytes
    metadata.json
  state/sources/wayback_github/latest.json

HF/Wayback static archive
  raw/source=wayback_hf/snapshot_date=YYYY-MM-DD/
    declarations.xml
    declarations_from_hf.xml.zip original immutable archive bytes
    metadata.json
  state/sources/wayback_hf/latest.json
```

`source_contract.py` owns these paths and the source IDs. The official source
keeps its historic path for compatibility; non-official sources are namespaced
under `raw/source=<source_id>/`.

### Ingestion flow

```text
  +-------+
  | Start |
  +---+---+
      |
      v
  Load `state/sources/<source>/latest.json`
      |
      v
  Download or read archive and compute exact-byte SHA-256 hashes
      |
      +--------------------------+
      |                          |
      v                          v
  Same hash and no --force       Different/new hash
      |                          |
      v                          v
  NO_CHANGE, no rewrite      Validate XML/archive structure
                                 |
                                 v
                          Write immutable raw objects
                                 |
                                 v
                          Write source state
                                 |
                                 v
                          Return INGESTED
```

The archive stage extracts exactly one `declarations.xml` from the zip and
retains the original zip beside it. An immutable write is idempotent for the
same bytes and fails for different bytes at the same source/date path.

The weekly official `pipeline-run` performs official ingestion first. If the
official input changed, processing reads all latest retained sources, including
the archive source. The explicit `pipeline-archive` target runs archive ingest
and processing in one configured process; `pipeline-archive-hf` applies the same
steps after downloading the static HF archive when needed. Both archive sources
use the same `declaration_uuid` pre-anomaly dedupe and retain all source
occurrences in Bronze and historical Silver; use `FORCE=1` only for an
intentional replay.

### Processing flow

```text
  latest raw source states
           |
           v
  materialize XML, CSV, metadata for every source
           |
           v
  parse each source independently
           |
           v
  combine source-shaped tables while retaining `ingestion_source`
           |
           v
  run quality checks and write quality report
           |
       errors?
       /      \
     yes      no
      |        |
      v        v
  FAILED   build analytical layers
                 |
                 v
      write Parquet, quarantine, registry, and optional BigQuery partitions
                 |
                 v
      write `state/latest.json` as the final commit marker
```

Quality warnings complete the run as `SUCCESS_WITH_WARNINGS`. Structural
errors, missing raw objects, failed writes, or a failed BigQuery load stop the
run and leave the previous processing state intact.

## Analytical layers and provenance

The layers answer different questions and deliberately preserve different
levels of history:

```text
  Raw XML/CSV/archive bytes
              |
              v
  Bronze: every parsed source occurrence
          source IDs, raw values, provenance, snapshot date
              |
              v
  Silver: anomaly metadata and review eligibility
          UUID deduplication happens before anomaly input
              |
              v
  Gold: latest eligible analytical view
        latest declaration/person/version selection
              |
              +----------------------+
              |                      |
              v                      v
  Dashboard aggregates       Anomaly registry
  fixed read-only slices      active/known lifecycle rows
```

Bronze retains source occurrences, including duplicates across the official and
Wayback inputs. Deduplication by `declaration_uuid` is applied before anomaly
detection so one declaration does not inflate its anomaly input, while source
provenance remains available for audit. Gold applies the latest-version and
eligibility rules used by dashboard metrics.

GCS materializes the complete pipeline output, including supporting tables such
as `liste`, mandates, activities, participations, and liabilities. BigQuery
loads the canonical dashboard set through snapshot replacement:

- Bronze: `declarations`, `people`, `incomes`, `assets`;
- Silver: `silver_declarations`, `silver_people`, `silver_incomes`,
  `silver_assets`;
- Gold: `gold_declarations`, `gold_people`, `gold_incomes`, `gold_assets`; and
- Registry: `anomaly_registry`.

The BigQuery loader stages one Parquet file at a time, evolves the target schema
when needed, deletes only the requested `snapshot_date` partition, inserts the
new rows, and removes the staging table. It does not replace historical
partitions.

### State as a commit marker

`state/latest.json` is intentionally written last:

```text
  raw source state  --->  derived artifacts  --->  BigQuery load
         |                         |                    |
         |                         |                    v
         +-------------------------+------------> state/latest.json
                                                   (only on success)
```

The file records the processing snapshot, pipeline version/Git SHA, official
compatibility hashes, and `source_snapshots` for every source used. A raw-only
success therefore cannot masquerade as a fully processed snapshot.

## Dashboard architecture

The public frontend is static and does not hold cloud credentials. Its API
requests pass through the Worker and a protected bridge:

```text
  Browser
     |
     | GET /api/dashboard/health?schema=2
     | GET /api/dashboard/overview, /search, /declarations/<uuid>
     v
  GitHub Pages React/Vite app
     |
     v
  Cloudflare Worker
     | validates fixed route, adds CORS/cache headers
     | forwards an authenticated request
     v
  Cloud Run BigQuery bridge
     | fixed SQL only
     +--------------------+--------------------+
     |                                         |
     v                                         v
  BigQuery Gold/Silver tables              GCS quality report/XML
     |                                         |
     +--------------------+--------------------+
                          v
                   JSON dashboard slice
```

The bridge exposes fixed routes for overview, income, assets, declarations,
gender, highlights, simple analysis, age analysis, search, and pipeline health.
The declaration detail route accepts a public UUID and returns only the matching
XML declaration node. The full XML feed is never sent to the browser.

The `/pipeline-health` page obtains the current snapshot, source coverage,
layer counts, review load, anomaly statuses, top categories, and next Monday
07:00 Europe/Paris countdown from one validated health response. The frontend
sorts layer rows into Bronze, Silver, Gold order even if the API query returns a
different order.

## Deployment and identity boundaries

```text
  Git push to `main`
          |
          v
  GitHub Actions
    | tests, Ruff, build
    | Workload Identity Federation (OIDC)
          |
          +----------------------+
          |                      |
          v                      v
  Artifact Registry       dashboard deployment commands
  versioned Job image      bridge / Worker / GitHub Pages
          |
          v
  Cloud Run Job
  runtime service account
          ^
          |
  Cloud Scheduler
  authenticated weekly trigger
```

Identity is intentionally separated:

- local GCS/BigQuery work uses Application Default Credentials;
- the Cloud Run Job uses its runtime service account;
- GitHub Actions uses Workload Identity Federation;
- the dashboard bridge uses a read-only service account and a shared secret
  between the Worker and bridge; and
- no long-lived service-account JSON keys are created or committed.

## Operational navigation

| Need | Start here |
| --- | --- |
| Run the full official local cascade | `make pipeline-run LOCAL_OUTPUT=/tmp/yahatvp-output` |
| Ingest only official raw files | `make pipeline-ingest` |
| Process retained latest sources | `make pipeline-process` |
| Replay the GitHub/Wayback archive | `make pipeline-archive WAYBACK_ARCHIVE_ZIP=... PIPELINE_SNAPSHOT_DATE=YYYY-MM-DD` |
| Replay the static HF/Wayback archive | `make pipeline-archive-hf WAYBACK_HF_ARCHIVE_ZIP=... PIPELINE_SNAPSHOT_DATE=YYYY-MM-DD` |
| Run Python checks | `uv run pytest`, `uv run ruff check .`, `uv build` |
| Run dashboard checks | `make backend-test` and `make frontend-test` |
| Review source-linked quality evidence | `uv run python -m hatvp.triage ...` |
| Deploy the ingestion image | push `main`; see `.github/workflows/deploy.yml` |
| Deploy the dashboard | `README.md` dashboard deployment section and the repository deployment skill |

For storage paths, environment variables, Google Cloud setup, and detailed
smoke-test commands, use the operational sections in [`README.md`](README.md).
