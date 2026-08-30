# Changelog

This live changelog keeps concise release-level information from the recent
development week, 2026-08-19 through 2026-08-28. Detailed implementation,
deployment, and pre-v1.0 history is preserved in
[`documentation_archive/20260826T215722Z_CHANGELOG.md`](documentation_archive/20260826T215722Z_CHANGELOG.md);
long-form validation evidence remains under `reports/`.

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
