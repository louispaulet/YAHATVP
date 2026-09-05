# Changelog

## 2026-09-05 — Improve dashboard reading and accessibility

### Changed

- Added skip navigation, route orientation focus, query-scoped loading, search
  field guidance, snapshot-reading guidance, a declaration section index, and a
  technical-field disclosure across the frontend.
- Improved responsive search/profile navigation and corrected the populated
  asset chart accessible description while preserving the existing API and
  source-data policy.
- Added an Explore table of contents with per-signal result counts and
  removed live countdown announcements from the screen-reader announcement
  channel while retaining a static scheduled timestamp.
- Added locale-backed declaration labels, contextual empty-section disclosures,
  source XML copy support, reusable snapshot context, signal explanations,
  profile match announcements, and text summaries for analysis charts.
- Added responsive quality-register rows, clearer analysis scope/toggle copy,
  shared focus treatment, and Lucide action icons for external and source links.
- Added a keyboard-friendly annual-value table beneath declaration amount bars
  so each chart has an equivalent text reading path.

### Verified

- Frontend tests: 34 passed; TypeScript/Vite production build passed.
- Browser checks covered the local dashboard at 320px and 1024px with no
  horizontal overflow; the deployed dashboard remains the source for loaded
  production data verification.

This live changelog keeps concise release-level information from the recent
development period, 2026-08-19 through 2026-08-30. Detailed implementation,
deployment, and pre-v1.0 history is preserved in
[`documentation_archive/20260826T215722Z_CHANGELOG.md`](documentation_archive/20260826T215722Z_CHANGELOG.md);
long-form validation evidence remains under `reports/`.

## 2026-08-30 — Merge pipeline fixes and replay production

### Changed

- Merged open PRs #46–#51 in order, resolving three tracking-document
  conflicts while preserving the Gold, orchestration, XML validation, income,
  history, and DOB-threshold changes.
- Deployed the final Cloud Run Job image for commit `5352965` and forced a full
  production replay. The replay used a temporary 8 CPU / 32 GiB profile after
  the normal 4 GiB profile reached its memory limit, then restored the normal
  1 CPU / 4 GiB scheduled profile.

### Verified

- Main workflow `33285643477` passed tests, Ruff, formatting, build, and Cloud
  Run deployment; local verification passed all 183 tests.
- Replay `hatvp-ingestion-qhb9x` completed in 12m51.96s with
  `SUCCESS_WITH_WARNINGS`, zero quality errors, 58,502 flagged records, 41,201
  warnings, all 13 BigQuery tables loaded, and `state/latest.json` advanced to
  snapshot `2026-08-30` at commit `5352965`.

Detailed merge and replay evidence is in
[`reports/03-validation/2026-08-30-pr-merge-deployment-replay.md`](reports/03-validation/2026-08-30-pr-merge-deployment-replay.md).

## 2026-08-30 — Honor configured DOB anomaly threshold

### Fixed

- Threaded `HATVP_PERSON_DOB_MAX_AGE_YEARS` from runtime settings through both
  processing paths into Silver anomaly detection.

### Verified

- Added regression coverage proving a configured 110-year threshold does not
  flag a 101-year-old parsed source date; the focused and full local suites pass.

## 2026-08-30 — Preserve mixed historical layer backfill

### Fixed

- Historical processing now loads both retained Bronze partitions and legacy
  Silver-only partitions, so newer Bronze data no longer hides older history
  used for anomaly comparisons and Gold selection.

### Verified

- Added a mixed Bronze/Silver fixture regression test; the full suite passes
  with 173 tests, Ruff, and formatting checks.

## 2026-08-30 — Accept BOM-prefixed XML downloads

### Fixed

- The download validator now accepts valid UTF-8 XML responses with a leading
  byte-order mark instead of rejecting them before parsing.

### Verified

- Added a BOM regression test; the focused parser/download checks pass.

## 2026-08-30 — Reprocess newly ingested sources

### Fixed

- The official pipeline no longer returns `NO_CHANGE` when a new archive source
  has been ingested since the previous processed state. Source sets must now
  match exactly before the processing short-circuit is allowed.

### Verified

- Added an end-to-end regression covering official processing followed by
  Wayback ingestion; the full local suite passes 172 tests, Ruff checks, and
  the package build.

## 2026-08-30 — Keep clean Gold rows active

### Fixed

- Gold now marks selected, non-superseded rows as active so clean values remain
  available to the documented Gold metrics; anomaly eligibility still excludes
  flagged values from aggregates.

### Verified

- The focused layer regression test and the full 170-test Python suite pass;
  Ruff, formatting, and package build checks also pass.

## 2026-08-28 — Enable Cloud Billing pricing export

### Changed

- Retried the Cloud Billing pricing-export save for billing account
  `01B02E-7B96C5-47715B` and enabled it for the EU `billing_export` dataset in
  `yahatvp-pipeline-eu`.

### Verified

- The `Pricing BigQuery Transfer` configuration exists in `europe` with the
  expected billing account parameter and destination dataset; its initial run
  is `RUNNING`.
- `cloud_pricing_export` is not populated yet. Google documents that initial
  pricing export propagation can take up to 48 hours, so table and net-EUR
  reporting verification remain pending.

## 2026-08-30 — Ignore whitespace-only income values

### Fixed

- Income coverage now treats whitespace-only declared and spouse values as
  empty, matching normalized income-row parsing.

### Verified

- Added a whitespace-income fixture regression test; the full Python suite and
  Ruff checks pass.

## 2026-08-28 — Merge parser/pipeline fixes and replay production data

### Changed

- Merged open PRs #42–#45 into `main`, resolving the overlapping parser and
  tracking-document conflicts while preserving the CSV, XML, and dry-run fixes.
- Deployed Cloud Run Job image `215c48a` and forced a production replay. The
  replay needed a temporary 8 CPU / 32 GiB profile after 4 GiB and 16 GiB
  attempts were terminated by the platform; the scheduled job was restored to
  1 CPU / 4 GiB after success.

### Verified

- Main workflow run `33121159432` passed tests, Ruff, build, and Cloud Run job
  deployment; local verification passed 170 tests, Ruff, formatting, and build.
- Execution `hatvp-ingestion-hrrp5` completed successfully in 8m41s with
  `SUCCESS_WITH_WARNINGS`, zero quality errors, 41,201 warnings, and 58,502
  flagged records. All 13 BigQuery tables and the 2026-08-28 Parquet/report
  artifacts loaded, and `state/latest.json` advanced to commit `215c48a`.

## 2026-08-28 — Configure project billing export and cost reporting

### Changed

- Created the EU `billing_export` BigQuery dataset in `yahatvp-pipeline-eu` and
  enabled detailed Cloud Billing usage-cost export for billing account
  `01B02E-7B96C5-47715B`.
- Enabled BigQuery Data Transfer support and pre-provisioned the documented
  pricing-export service account access. Pricing export could not be saved
  because the Cloud Billing console returned a Google server error (request
  ID `10702517473792787587`).

### Verified

- The filtered Cloud Billing report for `yahatvp-pipeline-eu` shows €0.24 of
  Cloud Run usage for 1–27 August 2026, offset by €0.24 of discounts, for
  €0.00 net; the project total is €0.48 including Artifact Registry and
  Cloud Storage.
- The detailed export dataset is in `EU`; its tables are not populated yet,
  consistent with the normal export propagation delay.

## 2026-08-27 — Preserve namespaced general mandate rows

### Fixed

- Made the general-mandate presence check namespace-safe so quality-only rows
  are retained when parsing namespaced HATVP XML.

### Verified

- Added a namespaced parser regression test; the full Python suite passes.

## 2026-08-27 — Preserve fallback CSV source identities

### Fixed

- CSV parsing now skips blank and normalized missing identity candidates before
  selecting the next configured fallback, preserving stable source linkage.

### Verified

- Added a regression test covering a blank `id_origine` with a valid
  `url_dossier`; the focused parser tests, full Python suite, and Ruff checks
  pass.

## 2026-08-27 — Publish the story-first homepage and website guides

### Changed

- Rebuilt the dashboard homepage as a story-first civic snapshot with staged
  loading, responsive sections, bilingual copy, declarant search, snapshot
  context, and supporting evidence.
- Balanced and published the supporting-evidence layout with a snapshot-
  coverage panel and mobile-safe declaration table.
- Added canonical [`design_style.md`](design_style.md) and
  [`tone_of_voice.md`](tone_of_voice.md) guides for future dashboard work.
- Fixed `--dry-run` propagation for the split ingest, archive-ingest, and
  process CLI stages so they do not require storage or mutate state.

### Verified

- Frontend tests, production builds, responsive browser QA, and homepage
  deployment checks passed; reviewed desktop and mobile layouts had no
  horizontal overflow or console warnings/errors.
- Split-stage dry-run regression tests and Ruff checks passed.

## 2026-08-26 — Archive historical tracking documentation

### Changed

- Condensed the live TODO and changelog files to current follow-ups and recent
  release information.
- Preserved the previous full files with the archive timestamp prefix
  `20260826T215722Z_`.

## 2026-08-25 — Explain chart ordering

### Changed

- Added bilingual copy below the women’s-share chart explaining that the bars
  run from the most popular to least popular position across the top ten.

## 2026-08-24 — Release dashboard metric and gender-chart updates

### Changed

- Released the v1.5 dashboard updates for eligible income and asset statistics,
  current anomaly-policy presentation, source-loadable declaration links, and
  the grouped public navigation.
- Reworked the gender-by-position view to show women’s percentage among all
  people in each of the ten most common positions, with a parity guide,
  responsive labels, and explicit totals.

### Verified

- Recent frontend and bridge tests, production builds, Cloud Run and Worker
  deployments, GitHub Pages publication, and browser checks passed; public
  routes returned HTTP 200 with no warning or error console entries.

## 2026-08-23 — Expand source coverage and pipeline transparency

### Changed

- Added the static Hugging Face/Wayback archive source alongside official and
  GitHub/Wayback coverage, retaining source-specific hashes and raw bytes.
- Added pipeline-health source coverage with both raw and deduplicated counts,
  bilingual archive provenance, and layer quality summaries.
- Refined the Explore presentation and linked DOB-quality leaderboard records
  to source-preserving declaration details.

### Verified

- Fixture and production archive replays loaded the Bronze, Silver, Gold, and
  anomaly-registry tables with zero quality errors; the public health and
  dashboard routes were browser-verified.

## 2026-08-21 — Select current Highlights signals

### Changed

- Updated Highlights to select the latest declaration per normalized name and
  surname and to show current review signals while retaining superseded history
  in the audit layers.
- Verified the Warsmann and Ruelle regression cases and the deployed bilingual
  Highlights flow.

## 2026-08-20 — Improve dashboard navigation and analysis

### Changed

- Grouped navigation into Explore, Declarations, and Data & methods while
  preserving existing route URLs.
- Published source-linked Highlights and repaired annual-value chart rendering
  in declaration details.

### Verified

- Frontend tests, production builds, responsive checks, and public deployment
  smoke tests passed for the updated routes.

## 2026-08-19 — Complete the first dashboard release

### Changed

- Released the first production dashboard analysis pages for salary, age, and
  declarant history, including accent-insensitive search, DOB quality metadata,
  source-preserving asset dates, and gender aggregates.
- Completed the v1.0 production ingestion replay and loaded all 13
  Bronze/Silver/Gold/anomaly-registry tables.

### Verified

- Local test suites, Ruff, package/build checks, BigQuery dry-runs, production
  smoke routes, and browser checks passed for the release.
