# Changelog

This live changelog keeps concise release-level information from the recent
development week, 2026-08-19 through 2026-08-25. Detailed implementation,
deployment, and pre-v1.0 history is preserved in
[`documentation_archive/20260826T215722Z_CHANGELOG.md`](documentation_archive/20260826T215722Z_CHANGELOG.md);
long-form validation evidence remains under `reports/`.

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
