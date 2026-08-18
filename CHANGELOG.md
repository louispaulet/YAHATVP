# Changelog

## 2026-08-18 — Implement the Silver and Gold analytical layers

### Changed

- Added explicit historical Silver Parquet/BigQuery artifacts with anomaly
  evidence, field-level metric eligibility, deterministic registry links, and
  retry-safe source-row identity.
- Added latest-version Gold artifacts with declarant/role/period ordering,
  child-row alignment, lifecycle state propagation, and current-metric filters.
- Added retained-Bronze backfill, anomaly-registry persistence, and a late-state
  gate so `state/latest.json` advances only after Bronze, Silver, Gold, registry,
  and optional BigQuery loads succeed.
- Migrated the dashboard bridge and explanatory copy from transitional curated
  tables to the Gold contract; historical investigations remain Silver/registry
  oriented.

### Verified

- Full Python suite: 140 passed; Ruff check/format, package build, and module
  line-budget checks passed.
- Forced current-source local run completed with `SUCCESS_WITH_WARNINGS`, zero
  quality errors, Bronze/Silver/Gold counts of 6,611/6,611/74,791/1,157,
  Gold counts of 6,605/6,605/74,730/1,157, and 3,042 registry rows. The
  unchanged replay returned `NO_CHANGE`.
- Dashboard bridge: 31 tests passed. Frontend: 18 tests passed and Vite build
  passed. Worker: 8 tests passed and TypeScript typecheck passed.
- Full source hashes, partition counts, deterministic replay fingerprints, and
  local-only validation scope are recorded in
  `reports/03-validation/2026-08-18-silver-gold-validation.md`.

## 2026-08-18 — Turn declaration detail into a readable interface

### Changed

- Replaced the raw-XML-first declaration detail page with a schema-aware view
  that renders source metadata, public profile fields, mandate date ranges,
  repeated interests and activities, annual amounts, assets, liabilities,
  attachments, and source-marked empty sections.
- Added annual amount bar summaries by year and kept the original XML in a
  collapsed audit panel so every parsed source field remains traceable.
- Added five schema-variant XML fixtures covering interest/activity, asset,
  attachment/company-interest, amended, and empty-section declarations.

### Verified

- Frontend unit tests: 18 passed; Vite production build passed.
- Five seeded live declarations from the current HATVP XML snapshot rendered
  with source coverage counts, no parser errors, and zero horizontal overflow;
  the asset-heavy variant exposed real estate, securities, insurance, bank
  accounts, vehicles, liabilities, events, and asset observations.
- Responsive browser verification passed at 390px and 1280px widths.

## 2026-08-18 — Complete the version-complete Bronze contract

### Changed

- Added deterministic `bronze_record_key` values so repeated or amended HATVP
  declaration occurrences are retained instead of being collapsed by UUID.
- Carried declaration amendment/version metadata, stable source identifiers,
  exact source hashes, raw XML/CSV record evidence, source locations, immutable
  raw object references, snapshot dates, and parser/pipeline versions into the
  normalized Bronze inputs.
- Kept the existing four BigQuery table names, snapshot partition replacement,
  and immutable GCS raw archive behavior unchanged while documenting the
  observed Bronze grain and future Silver/Gold migration boundary.
- Added a repeated-UUID amended-declaration fixture and Bronze contract report.

### Verified

- Focused parser, BigQuery loader/schema, pipeline-output, and structure checks
  pass; Ruff lint/format and the 70–100-line module budget pass.
- The fixture proves both declaration occurrences remain present with distinct
  Bronze keys and source evidence.

## 2026-08-18 — Define the BigQuery Bronze → Silver → Gold anomaly plan

### Changed

- Reclassified the existing four-table BigQuery layer as the planned Bronze
  foundation for version-complete declaration data.
- Added a detailed TODO plan for anomaly detection across all declaration
  versions in Silver and latest-declaration-per-declarant selection in Gold.
- Documented the twelve required anomaly families, anomaly registry fields and
  lifecycle, amended-declaration supersession, regression detection, metric
  eligibility, HATVP reporting scope, backfill, fixtures, and idempotency
  checks.
- Recorded the explicit rule that anomalies are flagged and retained rather
  than automatically corrected, deleted, or silently deduplicated.

### Verified

- `git diff --check`, `uv run pytest -q` (128 passed), `uv run ruff check .`,
  and `uv run ruff format --check .` pass.
- Documentation-only change; no runtime code, source data, or deployed
  infrastructure was modified.

## 2026-08-18 — Expose declaration search in navigation

### Fixed

- Added the translated “Search declarations” link to the dashboard navigation;
  the `/search` route was already deployed but was previously only reachable by
  entering its hash URL directly.

### Verified

- Frontend tests and production build pass with 13 tests.
- Live browser verification shows the navigation link and opens the search page
  at `#/search` with its heading and search input.

## 2026-08-18 — Deploy declaration search and source XML viewer

### Fixed

- Packaged every dashboard bridge Python module in the Cloud Run image so the
  new search and immutable XML routes start successfully in production.

### Deployed

- Cloud Run bridge revision `hatvp-dashboard-api-00009-wx6` is serving 100% of
  traffic; Cloudflare Worker version `a849662a-8564-4c00-a21f-d7441cd24947`
  is live at `hatvp-transparency-api.louispaulet13.workers.dev`.
- GitHub Pages publish commit `aa42c90d3a87443283cfdbd2832cd6d476c56b3b`
  serves the custom domain `yahatvp.thefrenchartist.dev`.

### Verified

- Full repository checks pass: 128 Python tests, Ruff lint/format, package
  build, 8 Worker tests, Worker typecheck, 31 bridge tests, 13 frontend tests,
  and the frontend production build.
- Live health, overview, income, assets, declarations, search, and source XML
  detail routes return successfully; direct bridge access remains 401 without
  its token, and custom-domain CORS is present.

## 2026-08-18 — Add declaration search and source XML detail pages

### Added

- Added a localized `/search` page linked from the navbar that searches public
  declarant/declaration metadata plus curated income and asset labels.
- Added declaration detail routes that read one matching `<declaration>` node
  from the immutable GCS XML snapshot and display it in a dedicated escaped
  source viewer.
- Kept curated contact and address fields out of search and the public metadata
  payload; added the bridge's bucket-reader deployment configuration.

### Verified

- Bridge fixture tests: 30 passed, including parameterized search, UUID-based
  XML extraction, and private-field exclusion.
- Worker tests: 8 passed and TypeScript typecheck passed.
- Frontend tests: 13 passed and the production Vite build passed.

## 2026-08-18 — Modularize the dashboard frontend

### Changed

- Split the React application shell, pages, layout, language switcher, panels,
  feedback states, data displays, and chart modules into focused files.
- Added `I18nContext` and `useResource` modules so localization state and
  cancellable API loading are reusable outside the route entrypoint.
- Kept every dashboard TypeScript source file below the 100-line review budget
  and preserved the existing routes, translations, loading states, and chart
  behavior.

### Verified

- `npm test` passes with 12 tests across four frontend test files.
- `npm run build` passes with the TypeScript check and production Vite build.

## 2026-08-18 — Review HATVP schema and raw snapshot immutability

### Changed

- Added a schema review report covering the current HATVP CSV/XML inventory,
  configured parser boundary, and four observed but intentionally unmodeled XML
  sections.
- Added a fixture for those observed source sections and a parser safety test;
  no normalization logic was changed.
- Marked the schema-review, fixture-guardrail, and historical-raw-immutability
  items complete in `TODO.md`.

### Verified

- The current CSV remains a 16-column semicolon-delimited file with both
  configured identity columns; the latest XML has root `declarations` and
  6,611 direct `declaration` records.
- GCS bucket versioning and immutable generation preconditions are enabled, and
  raw XML/CSV sizes and MD5 checksums match across the three archived snapshots.
- Existing triage tests cover duplicate UUIDs with trailing-whitespace semantic
  equality; the new schema fixture parses without inventing unsupported rows.

## 2026-08-18 — Complete weekly operational monitoring review

### Changed

- Added the source-linked weekly monitoring report for snapshots `2026-08-16`
  through `2026-08-18`.
- Documented recurring duplicate declaration UUID groups and prepared a
  source-correction follow-up packet without changing source or normalized data.
- Marked the weekly quality-report, duplicate-recurrence, and row-count/null-rate
  monitoring items complete in `TODO.md`.

### Verified

- The `2026-08-17` and `2026-08-18` reports have identical monitored row counts
  and null rates, zero quality errors, and no flagged-record regression.
- The six duplicate UUID groups recur twice each in all three raw XML snapshots;
  five are canonically identical and one has identical semantic content with a
  one-byte canonical difference consistent with trailing whitespace.
- BigQuery partition counts and Cloud Logging quality telemetry were checked for
  the two latest snapshots.

## 2026-08-18 — Publish the dashboard custom domain and balance branding

### Changed

- Published the dashboard at `https://yahatvp.thefrenchartist.dev/` with a
  repository `CNAME` and GitHub Pages HTTPS enforcement.
- Replaced the navbar mark and favicon with the ⚖️ balance emoji.
- Configured the Worker CORS origin and frontend deployment defaults for the
  custom domain.

### Verified

- Cloud Run bridge revision `hatvp-dashboard-api-00007-pw7` and Worker version
  `c939a4fe-9afc-4097-9fa9-c059d1161e47` are serving.
- The custom-domain page returned HTTP 200, the deployed HTML references
  `favicon.svg`, and the live favicon contains ⚖️.
- GitHub Pages reports an approved certificate with `https_enforced=true`; the
  Worker overview slice returned HTTP 200 with the custom-domain CORS origin.

## 2026-08-18 — Expand dashboard navigation

### Changed

- Replaced the pill-style Overview/About page switcher with a text navigation
  bar that uses an active underline and can accommodate additional pages.
- Added a localized Data explorer placeholder route between Overview and About.
- Kept the existing EN/FR language button design unchanged.

### Verified

- `make frontend-test` passes, including the expanded navigation, placeholder
  route, active link state, and French translations.

## 2026-08-18 — Compact large dashboard values

### Changed

- Centralized dashboard number and currency formatting so charts, legends,
  axes, tooltips, metrics, explanatory copy, and accessible descriptions share
  the same readability rule.
- Displayed large monetary values with compact locale-aware units such as
  `€65.6M` and `€506.1K`, while keeping the underlying aggregate values and
  ordinary row counts unchanged.

### Verified

- `make frontend-test` passes: 4 frontend test files and 11 tests, followed by
  a successful TypeScript/Vite production build; `make backend-test`, the 127
  Python tests, Ruff lint/format checks, and `uv build` also pass.

## 2026-08-18 — Prevent source-card badge overflow

### Fixed

- Allowed official-source card headers to wrap and constrained download badges
  to the card width, preventing the “Direct download” labels from painting
  outside their cards at narrow responsive widths.

### Verified

- Frontend unit tests and the production Vite build pass.

## 2026-08-18 — Keep comparison-chart legend values visible

### Fixed

- Removed the comparison legend label truncation that cropped the long income
  label in the pie-chart panel.
- Kept comparison amounts on one line while allowing labels to wrap within the
  available legend width.

### Verified

- `make frontend-test` passes with the legend layout regression assertions and
  a successful production build.

## 2026-08-18 — Count unique dashboard declarants

### Fixed

- Changed the homepage People metric to count distinct non-empty `nom` +
  `prenom` pairs within the latest snapshot instead of counting every
  declaration-linked people row.
- Clarified the metric detail as “unique declarants” in English and French.

### Verified

- Added BigQuery bridge coverage for case-insensitive, whitespace-trimmed name
  pairs and missing-name handling.
- The live `2026-08-18` snapshot resolves to 3,259 unique declarants versus
  6,611 declaration-linked people rows.
- `make backend-test` and `make frontend-test` pass.

## 2026-08-18 — Annualize dashboard income comparison

### Changed

- Updated the dashboard comparison to divide total declared income by the
  distinct reported income years in the latest snapshot.
- Added explanatory copy below the pie chart for the annualization, total
  observed assets, and the indicator’s limitations.
- Exposed aggregate totals and the income-year count from the fixed bridge query
  so the comparison remains accurate as asset sections change.

### Verified

- The current snapshot contains 17 distinct income years (2010–2026), producing
  an average annual income of €73,152,640.05 and a 37.0% income / 63.0% asset
  comparison split.
- `make frontend-test`, `make backend-test`, `uv run pytest`, Ruff, formatting,
  and `uv build` all pass; the new income and asset queries also pass BigQuery
  dry-run validation.
- Deployed Cloud Run revision `hatvp-dashboard-api-00006-gjl` and Cloudflare
  Worker version `79c8519a-5ef6-4739-84ce-2ff5efffa759` with the new aggregate
  fields, then published the frontend to GitHub Pages.
- Live smoke tests returned `yearCount: 17`, income total `1243594880.8`, asset
  total `124440950`, HTTP 200 from GitHub Pages, and the expected production
  CORS/cache headers.

## 2026-08-18 — Compare dashboard incomes and assets

### Changed

- Revised the dashboard donut chart to compare total income amounts against
  total asset amounts, with row counts, percentages, and translated labels.
- Kept the asset-by-section bar chart as the detailed asset breakdown.

### Verified

- `make frontend-test` passes with the English and French comparison labels and
  accessible chart description covered by the frontend fixture tests.

## 2026-08-18 — Fix dashboard asset-panel overflow

### Changed

- Let the asset chart panel include its value legend in normal layout flow so
  the legend cannot overlap the declaration or snapshot panels below it.
- Allow long asset labels to shrink and truncate within their legend cells.

### Verified

- `make frontend-test` passes: 8 frontend tests and a production build.
- GitHub Pages publish commit `48e7290` serves the new frontend bundle.
- Chrome verification confirmed the asset panel's content height matches its
  layout height and the page has no horizontal overflow.

## 2026-08-18 — Merge dashboard and deploy all services

### Deployed

- Merged PR #13 into the dashboard base branch and PR #14 into `main`, leaving
  no open pull requests.
- Deployed Cloud Run bridge revision `hatvp-dashboard-api-00005-5rm` and
  Cloudflare Worker version `027342cf-bc6f-4b36-9164-59766840565e`.
- Published the frontend to GitHub Pages with the live Worker API URL.
- GitHub Actions run `32123761635` deployed the ingestion image for commit
  `ccaf8fdf3ba9bba05dcf207b4c0c51574482e389`.

### Verified

- Worker health and all four dashboard slices returned HTTP 200 with the
  `2026-08-18` snapshot; the production CORS header and cache policy were
  present, and unauthenticated bridge data requests returned HTTP 401.
- GitHub Pages returned HTTP 200.
- Cloud Run execution `hatvp-ingestion-5klps` completed successfully with
  `succeededCount=1` in 1m6.22s.

## 2026-08-18 — Load dashboard plots independently

### Changed

- Split the dashboard API into independent `overview`, `income`, `assets`, and
  `declarations` routes through the Cloudflare Worker and read-only BigQuery
  bridge; each route runs one fixed aggregate query and receives its own cache
  policy.
- Removed the page-wide loading gate in favor of panel-level, slow-blinking
  loading shells and retryable errors, so the dashboard stays useful while
  individual slices are in flight.
- Replaced the CSS-only income pie and asset bars with lazy-loaded Recharts
  charts featuring responsive sizing, animated transitions, tooltips, and
  accessible value lists.

### Verified

- Frontend tests: 8 passed; production Vite build passes with the chart code in
  a deferred chunk (initial bundle 255.65 kB, 80.51 kB gzip).
- Worker tests: 6 passed; Worker typecheck passes.
- BigQuery bridge fixture tests: 23 passed; Ruff lint and formatting pass.

## 2026-08-18 — Clarify official source actions

### Changed

- Updated the dashboard About page so the HATVP open-data page is presented as
  an external-page action, while the CSV and XML feeds are presented as direct
  downloads.
- Added translated action labels, distinct icons, download semantics, and
  aligned card actions for the English and French interfaces.

### Verified

- Frontend unit tests and the production Vite build pass.

## 2026-08-18 — Add generated HATVP brand mark

### Added

- Added a generated 256px WebP HATVP mark with transparent outer pixels.
- Replaced the navbar’s CSS-only badge and added the mark as the browser
  favicon.

### Verified

- Frontend tests and the production Vite build pass.
- Published the generated mark to `gh-pages` (deployment commit `203cd51`);
  the live HTML references `hatvp-mark.webp`, which returns HTTP 200 as
  `image/webp`, and the navbar bundle contains the asset reference.

## 2026-08-18 — Link About page to project source

### Added

- Added translated About-page project cards linking to the YAHATVP GitHub
  repository.

### Verified

- Frontend tests and the production Vite build pass.
- Published the About-page project link to `gh-pages` (deployment commit
  `a803a62`); the GitHub Pages About route returned HTTP 200 and served both
  translated project-link labels with the requested repository URL.

## 2026-08-18 — Add sticky project footer

### Changed

- Made the dashboard shell a flex column so the footer stays at the bottom on
  short pages.
- Added translated English and French links to the YAHATVP GitHub project.

### Verified

- Frontend tests and the production Vite build pass.
- Published the footer update to `gh-pages` (deployment commit `d27770e`);
  the GitHub Pages root returned HTTP 200 and served both translated footer
  labels with the requested project URL.

## 2026-08-18 — Link dashboard to official HATVP sources

### Added

- Added translated About-page source cards linking to the official HATVP
  open-data landing page, declaration index CSV, and declarations XML feed.
- Added fixture coverage for the source-link destinations.

### Verified

- Official HATVP open-data page confirms the CSV list and XML declaration feed;
  frontend checks remain covered by the repository's `frontend-test` target.
- Published the About-page links to `gh-pages` (deployment commit `1bbc44f`);
  the GitHub Pages root returned HTTP 200.

## 2026-08-18 — Harden declaration-type translations

### Fixed

- Made declaration-type locale lookup insensitive to source-label casing,
  accents, apostrophes, spaces, and punctuation, so legacy values such as
  `DéClaration D'IntéRêTs` resolve to the configured human-readable wording.
- Added regression coverage for all nine declaration types in English and the
  French fallback path.

### Verified

- Frontend tests and the production Vite build pass.
- Published the corrected frontend to `gh-pages` (deployment commit
  `3210a4d`); the GitHub Pages root returned HTTP 200.

## 2026-08-18 — Localize dashboard labels

### Changed

- Added English and French locale configuration files for the dashboard copy,
  with English as the default language and a persistent language switcher.
- Replaced technical asset identifiers such as `immeubleDto` and
  `assuranceVieDto` with readable English/French labels, and translated the
  income-stream and declaration-type labels through the same configuration.
- Localized number, currency, date, navigation, metric, panel, about, and
  accessibility labels for both languages.

### Verified

- Frontend tests cover the default English view and switching to French;
  production Vite build passes.
- Published the frontend build to `gh-pages` (deployment commit `2d0f000`);
  the GitHub Pages root returned HTTP 200 and the branch contains the new
  localized bundle.

## 2026-08-18 — Add two-stream income pie chart

### Changed

- Updated the dashboard's `Income, by stream` panel to use a two-slice pie chart
  when exactly two income streams are present, with labeled amounts, row counts,
  percentages, and an accessible chart description.
- Kept the existing breakdown list for empty, single-stream, or larger
  comparisons.

### Verified

- Frontend fixture tests and the production Vite build pass.

## 2026-08-18 — Fix live dashboard CORS

### Fixed

- Corrected the production `FRONTEND_ORIGIN` from the GitHub Pages path to the
  actual browser origin `https://louispaulet.github.io`; URL paths are not part
  of the CORS origin value.
- Redeployed Cloud Run revision `hatvp-dashboard-api-00004-49f` and Worker
  version `b2450c38-cc3a-48d8-8f46-81b6a5b396e1`.

### Verified

- Chrome now renders the live dashboard instead of `Failed to fetch`.
- The Worker returns `Access-Control-Allow-Origin:
  https://louispaulet.github.io` and the dashboard API returns HTTP 200.

## 2026-08-18 — Deploy HATVP transparency dashboard

### Deployed

- Created Secret Manager secret `hatvp-dashboard-bridge-token` and configured
  the matching encrypted Cloudflare Worker secret without committing the token.
- Deployed the read-only Cloud Run bridge as revision
  `hatvp-dashboard-api-00003-xzr` with the dedicated
  `hatvp-dashboard-reader` service account and dataset-level BigQuery access.
- Deployed Worker version `c3caf8a3-7ee8-47cf-bc3e-52b06db3138f` at
  `https://hatvp-transparency-api.louispaulet13.workers.dev`.
- Published the Vite frontend to the `gh-pages` branch at
  `https://louispaulet.github.io/YAHATVP/`.
- Fixed the declaration-type aggregate ordering alias found during the first
  live smoke test and republished the frontend with an explicit production
  `VITE_API_BASE_URL`; the Makefile now requires that URL for publication.

### Verified

- Live Worker `/healthz`, Worker `/api/dashboard`, authenticated bridge
  `/v1/dashboard`, and GitHub Pages all returned HTTP 200.
- The live dashboard payload contains the `2026-08-18` snapshot and counts of
  6,611 declarations, 6,611 people, 74,791 incomes, and 1,157 assets.

## 2026-08-18 — Add HATVP transparency dashboard foundation

### Added

- Added the isolated `website/hatvp-transparency-dashboard/` workspace with a
  tested Cloudflare Worker proxy, read-only BigQuery Cloud Run bridge, and
  Vite/React/Tailwind HashRouter frontend.
- Added aggregate-only dashboard data for the latest curated snapshot,
  including table counts, income streams, asset sections, and declaration
  types; raw rows and contact fields are not exposed.
- Added Makefile targets for installation, local development, fixture tests,
  bridge/Worker deployment, and GitHub Pages publication through `gh-pages`.

### Verified

- Dashboard backend: 26 fixture/unit tests pass, Worker typechecking passes,
  Ruff lint/format passes, and the frontend tests plus production build pass.
- Repository checks: 127 existing project tests pass, Ruff lint/format passes,
  and `uv build` succeeds.

## 2026-08-18 — Reorganize the report catalog

### Changed

- Grouped reports into numbered quality, outlier, validation, and manual-review
  folders with date-first filenames and a new [`reports/00-index.md`](reports/00-index.md)
  navigation page.
- Consolidated the overlapping BigQuery findings and income-coverage recovery
  notes into [`reports/03-validation/2026-08-17-bigquery-and-income-validation.md`](reports/03-validation/2026-08-17-bigquery-and-income-validation.md).
- Kept the asset outlier Markdown, portable HTML, and artifact JSON together as
  format variants of one analysis, and updated the triage CLI default output
  directory to `reports/01-quality`.
- Updated repository links and manual-review bundle filenames without changing
  raw values, source hashes, declaration identifiers, or review dispositions.

### Verified

- Report inventory contains no root-level report files other than the index;
  all report links resolve to the reorganized paths.

## 2026-08-18 — Add BigQuery tutorial query pack

### Added

- Added ten progressively harder, one-query-per-file BigQuery examples under
  `tutorial/`, covering the curated `declarations`, `people`, `incomes`, and
  `assets` tables and their simple joins.
- Added matching CSV outputs for the fixed `2026-08-18` snapshot and a tutorial
  README with execution, interpretation, and regeneration guidance.
- Linked the tutorial from the main README and recorded the completed work in
  TODO.md.

### Verified

- The checked-in CSVs were generated from read-only BigQuery queries in project
  `yahatvp-pipeline-eu`, dataset `hatvp`, region `europe-west1`.
- Re-executing all ten SQL files produced byte-for-byte identical CSV output;
  `uv run pytest` passed 127 tests, Ruff lint/format checks passed, and
  `uv build` completed successfully.

## 2026-08-18 — Deploy refactored packages and replay production

### Verified

- Built and pushed image `europe-west1-docker.pkg.dev/yahatvp-pipeline-eu/hatvp/hatvp:b25e9c8`; Cloud Build `22512c8c-8000-482e-af39-897e3430db70` completed successfully with image digest `sha256:db8a6fd1cd6649332beed0c7b8bd74b5a300704c4faaf6cc524787d0fcc32906`.
- Updated Cloud Run Job `hatvp-ingestion` to the refactored image and ran forced execution `hatvp-ingestion-84n27`; it completed in 1m22.85s with `succeededCount=1` and container exit 0.
- GCS snapshot `2026-08-18` advanced only after processing completed, with pipeline SHA/version `b25e9c8`, raw CSV/XML objects, all ten silver Parquet tables, quarantine anomalies, and a quality report.
- The quality report contains 0 errors, 3,611 warnings, 5,818 flagged records, and full counts of 6,611 declarations, 6,611 people, 74,791 incomes, and 1,157 assets.
- BigQuery successfully loaded the four curated tables for the new partition: 6,611 declarations, 6,611 people, 74,791 incomes, and 1,157 assets.
- Cloud Logging contains the expected download, hash comparison, quality, BigQuery completion, pipeline completion, and `SUCCESS_WITH_WARNINGS` status events.

## 2026-08-18 — Group Python modules into domain packages

### Changed

- Reorganized prefixed modules into `parser`, `pipeline`, `quality`, `triage`,
  `bigquery`, `storage`, `download`, and `tables` packages.
- Kept `hatvp-ingest`, `python -m hatvp.main`, and the façade package APIs
  working while making the nested modules the canonical internal import paths.
- Updated all repository imports and tests, and documented the complete new
  `src/hatvp` tree and `python -m hatvp.triage` command in the main README.

### Verified

- `uv run pytest`: 127 passed, including the 70–100-line module-budget checks.
- Ruff lint and formatting checks pass; `uv build` packages successfully.
- `python -m hatvp.main --help` and `python -m hatvp.triage --help` both pass.
- No removed prefixed modules remain directly under `src/hatvp`.

## 2026-08-18 — Modular Python boundaries

### Added

- Added packaged `src/hatvp/pipeline.yml` and typed configuration loading with
  YAML defaults, environment overrides, and CLI-level model updates.
- Added focused parser, pipeline, quality, triage, storage, and BigQuery
  components plus direct fixture/fake-client tests for their public boundaries.
- Added the tracked Python line-budget test covering package initializers and
  tests as well as production modules.

### Changed

- Split the oversized parser, orchestration, quality, triage, and test modules
  while preserving `parse_csv`, `parse_xml`, `parse_sources`, `run_pipeline`,
  stable table schemas, provenance, immutable raw artifacts, and late state
  updates.
- Enabled pull-request CI testing while restricting Cloud Run deployment to
  pushes on `main`.
- Replaced the stale README layout sketch with the complete modular source
  tree, including parser, pipeline, quality, triage, storage, and BigQuery
  components plus the stable compatibility façades.

### Verified

- `uv run pytest`: 127 passed.
- Ruff check and format check pass; `uv build` packages `pipeline.yml`; the
  staged line-budget test passes for all tracked Python files; and the local
  fixture pipeline returns `SUCCESS_WITH_WARNINGS` followed by `NO_CHANGE`.
- PR #10 CI is green: test and deployment-config pass, while deployment is
  skipped for the pull-request event as intended. A read-only BigQuery baseline
  for `2026-08-17` confirms partitioned curated tables and counts/fingerprints
  of declarations 6,611/`-5383795550778946119`, people 6,611/
  `-2019889874151548892`, incomes 74,791/`-2929076836325473210`, and assets
  1,157/`-5142282871526498847`.
- The requested live replay is blocked before mutation: ADC is unavailable
  (`google.auth.exceptions.DefaultCredentialsError: Your default credentials
  were not found`) and the local HATVP GCS/BigQuery environment variables are
  unset. PR #10 remains open and unmerged pending ADC/resource access.

## 2026-08-17 — Add operational retention verification and alerting

### Added

- Added structured quality telemetry for warning streaks and flagged-record
  regressions above 10% from the previous successful snapshot.
- Added the monitoring and retention runbook at
  [`ops/monitoring/README.md`](ops/monitoring/README.md) and three versioned
  Cloud Monitoring policy manifests for failed executions, repeated warnings,
  and flagged-record regressions.

### Verified

- Confirmed project `yahatvp-pipeline-eu` has a locked 400-day `_Required` audit
  bucket, a 30-day `_Default` application-log bucket, and the required audit
  sinks; no retention settings were changed.
- Created email notification channel
  `projects/yahatvp-pipeline-eu/notificationChannels/15119347564909849591` for
  the configured operator email.
- Created and enabled policies `6502266148116163647`, `11520248707029483720`,
  and `6502266148116161328`, each attached to the email channel.
- Focused telemetry checks pass: 10 tests, Ruff lint, and formatting.

### Follow-up

- Confirm receipt of a test notification email.

### Post-merge verification

- GitHub Actions run `32067593336` passed its tests, image build, and Cloud Run
  deployment for image `d2b4a9b`.
- Forced executions `hatvp-ingestion-ff7gs` and `hatvp-ingestion-dqc6b`
  completed successfully. The second emitted the real
  `quality_warning_streak` event with `warning_streak=2`, 5,818 flagged
  records, and zero quality errors; the deployed job uses the expected
  `cloud_run_job` resource labels.

## 2026-08-17 — Add income coverage recovery report

### Added

- Added the income-coverage recovery findings, now consolidated in [`reports/03-validation/2026-08-17-bigquery-and-income-validation.md`](reports/03-validation/2026-08-17-bigquery-and-income-validation.md), documenting the root cause, unified stream counts, production BigQuery validation, source hashes, and remaining interpretation limits.

### Verified

- The report reconciles the successful production results: 74,791 unified income rows, zero quality errors, identical repeat-load fingerprints, and a post-refresh `NO_CHANGE` execution.

## 2026-08-17 — Refresh BigQuery with annual mandate incomes

### Verified

- Deployed commit `1000d0b03a6fdcebef75b467fca1cf7a95860d84` through GitHub
  Actions run `32049058688`.
- Successful forced execution `hatvp-ingestion-f6mdg` rebuilt the snapshot;
  the curated `incomes` partition now contains 74,791 rows: 74,725 annual
  `mandate_remuneration` rows and 66 `revenu_mandat` rows, with zero quality
  errors.
- The loader migrated the existing BigQuery `incomes` table to include
  `income_stream` and `remuneration_index`; `snapshot_date` remains a
  partitioning `DATE`.
- Repeat forced execution `hatvp-ingestion-ts6jb` produced the same four table
  row counts and fingerprints, including incomes fingerprint
  `-2929076836325473210`.
- Unchanged execution `hatvp-ingestion-rmclb` returned `NO_CHANGE`; GCS state
  remains pinned to the successful `1000d0b03` snapshot.
- Updated the BigQuery, revenue-stream, and category-income reports with the
  unified row counts and deployment evidence.

## 2026-08-17 — Make BigQuery curated loads schema-evolution safe

### Changed

- Updated the BigQuery loader to detect new staged columns, add them to an
  existing curated table, and insert by explicit column names rather than
  relying on positional `SELECT *` alignment.
- Kept the existing snapshot delete/insert order and null-filled any target
  columns absent from a future staged schema.
- Added fixture coverage for both first-table creation and an existing-table
  schema migration.

### Verified

- Focused BigQuery and pipeline checks pass: 16 tests.
- The first production replay of commit `e50eb09` reached quality completion
  with `incomes=74,791` and zero quality errors, then failed only at the old
  14-column BigQuery insert; the job log confirms `state/latest.json` was not
  advanced.

### Follow-up

- Resolved by the successful `hatvp-ingestion-f6mdg` replay recorded above.

## 2026-08-17 — Include annual mandate remuneration in curated incomes

### Changed

- Extended the unified `incomes` parser output to include every annual numeric
  value nested in `mandatElectifDto`, while retaining the detailed
  `mandate_remunerations` table and immutable source record.
- Added `income_stream` tags for `revenuMandatDto` versus
  `mandatElectifDto`, preserving explicit zero values and source years in the
  normalized Parquet schema.
- Added stream-level quality coverage metrics and fixture regressions for
  multi-year and zero-value remuneration series.
- Updated the README and TODO to document the curated income contract and the
  pending BigQuery replay.

### Verified

- Full local checks pass: 38 tests, Ruff lint, and parser/quality regressions.
- Live local-output run against the current HATVP files completed with zero
  quality errors and `SUCCESS_WITH_WARNINGS`.
- The resulting snapshot contains 74,791 numeric `incomes` rows: 74,725
  `mandate_remuneration` rows across 5,850 declarations and 66
  `revenu_mandat` rows across 9 declarations.

### Follow-up

- Resolved by the successful `hatvp-ingestion-f6mdg` and
  `hatvp-ingestion-ts6jb` replays recorded above.

## 2026-08-17 — Enable and validate the initial BigQuery curated layer

### Changed

- Added an explicit four-table BigQuery allowlist for `declarations`, `people`,
  `incomes`, and `assets`; other normalized tables remain GCS-only.
- Removed runtime dataset creation, added regional BigQuery configuration, and
  made empty and null-only curated Parquet fields use stable types, including a
  `DATE` `snapshot_date`.
- Updated the deployment workflow to enable BigQuery after the dataset and
  least-privilege runtime IAM were configured.
- Added loader, table-selection, idempotency-order, and stable-schema tests.

### Verified

- Full local checks pass: 36 tests, Ruff, formatting, and package build.
- Created dataset `yahatvp-pipeline-eu:hatvp` in `europe-west1`; granted
  `roles/bigquery.jobUser` to `hatvp-runtime` at project scope and dataset-level
  `roles/bigquery.dataEditor` access.
- GitHub Actions run `32038454470` deployed commit `ca9d19a` through Workload
  Identity Federation with `HATVP_ENABLE_BIGQUERY=true`.
- Forced executions `hatvp-ingestion-74pqj` and `hatvp-ingestion-7vgcm`
  succeeded. Partition row counts were 6,611 declarations, 6,611 people, 66
  incomes, and 1,157 assets; all four tables use `snapshot_date` as a `DATE`.
- The replay produced identical `BIT_XOR(FARM_FINGERPRINT(...))` row
  fingerprints, and unchanged execution `hatvp-ingestion-bzqvw` emitted
  `NO_CHANGE`. The weekly Scheduler trigger was restored to `ENABLED`.
- Published the consolidated technical findings report at
  `reports/03-validation/2026-08-17-bigquery-and-income-validation.md`.

### Follow-up

- Add operational alerts and monitor the first weekly BigQuery partitions
  before expanding the curated table set.

## 2026-08-17 — Complete first production snapshot quality triage

### Added

- Added the source-linked triage generator in `src/hatvp/quality_triage.py`,
  with fixture coverage for repeated names, duplicate declaration UUIDs,
  whitespace-semantic duplicate handling, negative bank-account values,
  source-linked asset outliers, and exact count reconciliation.
- Added the complete Markdown review report and machine-readable register for
  the `2026-08-16` production snapshot under `reports/`.

### Verified

- Reconciled all 5,763 quarantine anomaly rows to the canonical GCS quality
  report: 5,599 expected identity collisions, 143 source-consistent asset
  outliers, 9 source-valid overdraft-style values, and 12 duplicate-UUID rows
  across 6 groups.
- Matched every flagged row to the immutable raw XML and persisted normalized
  record. All six duplicate UUID groups contain semantically identical XML;
  one pair differs only by trailing whitespace in the source.
- Recorded raw XML SHA-256
  `865261857f88ec6c262558bc115b37b94f97ea3418b6829267aa6cbd1458fdaf` and
  pipeline revision `f21853de13c236400d3fc9f9b8da34ce16ad7bb2` in the register.
- Fixture triage tests pass: 3 tests. The production report has zero
  unresolved or parser/source-mismatch records.

### Follow-up

- Monitor recurrence and pursue source correction for the six duplicate
  declaration UUID groups; the canonical-byte difference is whitespace-only.

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

- Updated `reports/02-outliers/2026-08-17-revenue-stream-outliers.md` after checking all
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

- Added `reports/02-outliers/2026-08-17-revenue-stream-outliers.md`, covering both sparse
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

- Added `reports/02-outliers/2026-08-17-income-outliers.md` with the full
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
  `reports/04-manual-review/2026-08-17/6dcd326d-e076-4d7a-a428-15075a15dddd/`.
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
  `reports/02-outliers/2026-08-17-asset-outliers.artifact.json` and
  `reports/02-outliers/2026-08-17-asset-outliers.html`.
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

- Added `reports/02-outliers/2026-08-17-asset-outliers.md`, a fact-checking
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
