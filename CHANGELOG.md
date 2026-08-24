# Changelog

## 2026-08-24 — Exclude anomalous values from dashboard statistics

### Changed

- Applied the existing Gold/Silver `metric_eligible` contract to homepage
  income and asset aggregates, including their clean row counts and year count;
  homepage monetary row cards now use those same eligible counts.
- Updated declarant income-by-year chart totals to exclude flagged values while
  retaining the unchanged source amounts and review metadata for audit.
- Versioned public dashboard statistic requests so browsers do not reuse a
  pre-release cached overview after a metric-policy deployment.
- Documented the dashboard-wide monetary metric policy and added bridge query
  regression coverage.

### Verified

- Focused bridge tests cover eligible-only income and asset aggregates and the
  clean income-by-year calculation.
- GitHub Actions run [32756217418](https://github.com/louispaulet/YAHATVP/actions/runs/32756217418)
  passed for commit `bea7649`.
- Deployed Cloud Run bridge revision `hatvp-dashboard-api-00026-r7f` and
  Worker version `6ffd1f74-0d24-4c81-8138-465ed7191b9c`; published frontend
  commit `ade1378` at https://yahatvp.thefrenchartist.dev/.
- Live income metrics now total €2,459,926,847 across 17 eligible years,
  rendering as €144.7M average annual income; eligible assets total €1,885,901.
  The homepage renders 95,892 eligible income rows and 27 eligible asset rows.
  The Worker slices, `/`, and `/#/analysis` all returned HTTP 200, and fresh
  browser verification found zero warning or error console entries on both
  pages. No ingestion replay was needed because the existing Gold eligibility
  columns were already materialized.

## 2026-08-24 — v1.5 dashboard release

### Changed

- Merged PR #39 for DOB leaderboard declaration links and PR #40 for the
  editorial Explore page redesign into `main`.
- Published the frontend to `gh-pages` commit `0724cea`, deployed bridge
  revision `hatvp-dashboard-api-00024-g65`, and deployed Worker version
  `3dc05b05-bc5f-4ad9-b2e7-27c1ebacf34b`.
- GitHub Actions runs `32672542370`, `32673011394`, and `32673157976` passed;
  the Cloud Run ingestion deployment completed successfully.

### Verified

- Local checks passed: 164 Python tests, 47 bridge tests, 13 Worker tests,
  Worker typecheck, 29 frontend tests, the frontend production build, Ruff,
  formatting, and package build.
- The live local dry-run completed `SUCCESS_WITH_WARNINGS` with zero quality
  errors; the public health API reports snapshot `2026-08-23` with zero
  quality errors and all three retained source IDs.
- Chrome verified Explore, pipeline health, About, analysis, age analysis, and
  a DOB leaderboard click-through to declaration detail with raw XML; all
  audited pages had zero warning/error console entries and no horizontal
  overflow.

## 2026-08-24 — Keep DOB leaderboard links source-loadable

### Changed

- Updated declaration detail lookup to resolve the source-preserving Bronze row
  used by the DOB leaderboards instead of requiring a Gold row.
- Passed each declaration's immutable `source_object` through the bridge so
  official, GitHub/Wayback, and Hugging Face XML snapshots can be opened from
  the same detail route.
- Accepted the `gs://...` URI form stored in BigQuery while validating that it
  points at the configured archive bucket.

### Verified

- `make backend-test` passed 47 bridge tests, 13 Worker tests, and Worker
  TypeScript typecheck.

## 2026-08-23 — Redesign the Explore presentation

### Changed

- Added Lucide icons and semantic surface, border, and card-shadow tokens to
  the dashboard frontend.
- Reworked `/explore` into an editorial two-column hero with structured
  snapshot/method metadata, distinct income/asset/amendment section tones,
  readable rank markers, clearer review badges, source-link CTAs, and
  card-shaped loading skeletons.
- Refined the shared header, language switcher, footer links, error state, and
  responsive card grid while keeping all existing strings, records, routes,
  API requests, and navigation behavior unchanged.

### Verified

- `npm test` passed all 29 frontend tests.
- `npm run build` passed the production TypeScript/Vite build.
- Browser QA covered 1440×1024 English/French, 1024×768, 768×1024,
  390×844 English/French, and 320px layouts with no page-level horizontal
  overflow; a fresh browser tab reported no warning or error console entries.
## 2026-08-23 — Show raw and deduplicated source coverage

### Changed

- Extended the pipeline-health API with a raw Bronze declaration count for
  each source while keeping the headline count deduplicated from Gold.
- Added the raw count beneath each source total in italicized parentheses,
  with bilingual labels and contract tests across the bridge, Worker, and
  frontend.

### Verified

- Backend checks passed: 47 bridge tests, 13 Worker tests, and Worker
  TypeScript typecheck. Frontend checks passed: 29 tests and the production
  build.
- The live health API reports deduplicated/raw pairs of `3,728`/`6,608` for
  HATVP, `8,518`/`14,026` for GitHub/Wayback, and `5,652`/`10,944` for the
  Hugging Face snapshot.
- Deployed bridge revision `hatvp-dashboard-api-00022-9tn`, Worker version
  `36dd9e0f-ab4a-469c-924a-f02693ae915d`, and the frontend at
  https://yahatvp.thefrenchartist.dev/#/pipeline-health.
- GitHub Actions Test and deploy run
  [32664892398](https://github.com/louispaulet/YAHATVP/actions/runs/32664892398)
  passed on the corrected main commit `4449fd2`.
- Chrome verified the public English and French pages with the three raw
  labels rendered beneath their deduplicated values and zero console warnings
  or errors.

## 2026-08-23 — Explain Wayback and Hugging Face provenance on the About page

### Changed

- Added bilingual About-page cards that distinguish the Internet Archive's
  Wayback Machine and its companion GitHub archive from the separate static
  Hugging Face snapshot.
- Identified the Hugging Face snapshot as made by `thefrenchartist`, explained
  that it is not a live feed, and linked directly to the
  [`hatvp_declarations_xml`](https://huggingface.co/datasets/the-french-artist/hatvp_declarations_xml)
  dataset.

### Verified

- `make frontend-test` passed all 29 frontend tests and the production build.
- `make frontend-deploy VITE_API_BASE_URL=https://hatvp-transparency-api.louispaulet13.workers.dev`
  published the frontend from main commit `a1aaaac`.
- Chrome verified the cache-busted public `/about` route in English and French,
  including both archive cards and links, with zero warning or error console
  entries.

## 2026-08-23 — Add the static HF/Wayback archive source

### Changed

- Added the `wayback_hf` source with the same immutable zip retention, XML
  extraction, source-state tracking, Bronze → Silver → Gold processing, UUID
  deduplication, and `NO_CHANGE` behavior as the existing GitHub/Wayback
  archive.
- Added `pipeline-archive-hf` and `pipeline-archive-hf-ingest` targets. They
  download `declarations_from_hf.xml.zip` from the companion archive repository
  when the local sibling file is absent and preserve the requested GitHub
  provenance URL.
- Added bilingual pipeline-health labels and fixture coverage for the new
  source. The archive’s `declarations_from_hf.xml` zip member is accepted as
  the single XML document while the normalized XML artifact remains
  `declarations.xml`.

### Verified

- Fixture replay covered both archive source IDs; the real local Hf replay
  processed 10,944 Bronze declarations, deduplicated to 10,924 unique UUIDs in
  Gold, returned `SUCCESS_WITH_WARNINGS` with zero quality errors, and returned
  `NO_CHANGE` on a second ingestion. Archive SHA-256:
  `5c0c00dca2ecf9749a0491d871ed2829f7ffd9006ca79086b3a55554c3fdcb1d`.
- GitHub Actions Test and deploy run
  [32663428913](https://github.com/louispaulet/YAHATVP/actions/runs/32663428913)
  passed and deployed the ingestion image from commit `76c2662`.
- The authorized production replay persisted `wayback_hf`, loaded all 13
  Bronze/Silver/Gold/registry tables, and advanced `state/latest.json` with
  `SUCCESS_WITH_WARNINGS`, zero quality errors, and 58,672 flagged records.
  The live health API reports `hatvp_website: 3,728`,
  `wayback_github: 8,518`, and `wayback_hf: 5,652` declarations.
- Deployed bridge revision `hatvp-dashboard-api-00021-22b`, Worker version
  `b84bdfdd-16d3-4edb-beba-95344b568c4d`, and the GitHub Pages frontend.
  Chrome verified the English and French `/pipeline-health` pages show the
  Hf source name and detail with zero console warnings or errors.

## 2026-08-23 — Explain official and Wayback source coverage in the dashboard

### Changed

- Expanded the bilingual Sources & methods page with the distinction between
  the current official HATVP publication and historical declarations recovered
  from the Internet Archive's Wayback Machine after HATVP unpublishes them.
- Added a direct link to the companion
  [`hatvp-archive-wayback-machine`](https://github.com/louispaulet/hatvp-archive-wayback-machine)
  project and source-specific explanations to Pipeline health.
- Renamed the source labels to `HATVP official website` and `GitHub / Wayback
  historical` so the recovery stream cannot be mistaken for a current official
  publication.

### Verified

- `make frontend-test` passed 29 frontend tests and the production build.
- Published the frontend from main commit `cfbadf3`; GitHub Pages advanced to
  `830c951b53d4193dd9ef6b25852d585709cb2af3`.
- Chrome verified both public routes in English and French with the new copy,
  live source counts, and zero warning or error console entries.

## 2026-08-23 — Link the companion Wayback archive

### Changed

- Linked the main README to
  [`hatvp-archive-wayback-machine`](https://github.com/louispaulet/hatvp-archive-wayback-machine).
- Explained why preserved historical HATVP source material matters for
  YAHATVP's audit, comparison, recovery, and retained-source replay paths.

### Verified

- Checked the reciprocal GitHub link and confirmed the documentation-only diff
  contains no code, generated data, credentials, or deployment changes.

## 2026-08-23 — Document the project architecture

### Added

- Added [`ARCHITECTURE.md`](ARCHITECTURE.md) with repository structure,
  source-ingestion and processing flows, analytical-layer semantics, dashboard
  boundaries, deployment identities, and ASCII diagrams.
- Linked the detailed architecture reference from the main README architecture
  section.

### Verified

- Checked the new Markdown links and confirmed the documentation-only change
  introduces no code, generated data, credentials, or deployment changes.

## 2026-08-23 — Restore Wayback/GitHub source coverage

### Changed

- Fixed source discovery so a legacy official `state/latest.json` cannot be
  dropped when a `wayback_github` source state is also present.
- Made `pipeline-archive` run archive ingestion and processing in the same
  configured process, with `FORCE=1` support for an authorized replay.
- Force-ingested the GitHub/Wayback `declarations.xml.zip` archive into the
  production raw store while retaining the original zip, extracted XML, hashes,
  and source provenance. The existing frontend source mapping now displays the
  restored source with its human-readable label.

### Verified

- Archive SHA-256: `e8bad9b08c15935321e0ff4c367159c251710f22028462a04c844e47fbe309e7`;
  GCS contains both `hatvp_website` and `wayback_github` raw snapshots and
  `state/latest.json` records both source hashes.
- Production processing completed `SUCCESS_WITH_WARNINGS` with zero quality
  errors; the combined quality stage contained 20,634 declarations and 28,764
  flagged records. BigQuery loaded all 13 Bronze/Silver/Gold/registry tables.
- The live health API reports `Site HATVP: 4,629` and
  `GitHub / Wayback: 11,992`; the quality regression warning is retained because
  the combined source set is larger than the previous official-only snapshot.
- Full Python checks passed: 163 tests, Ruff, format check, and package build;
  `make backend-test` passed 47 bridge tests plus Worker tests/typecheck;
  `make frontend-test` passed 29 tests and the production build. GitHub Actions
  run [32659679713](https://github.com/louispaulet/YAHATVP/actions/runs/32659679713)
  passed and deployed image `97919c3`.
- Chrome verified the public `/pipeline-health` page: both source rows,
  countdown, Bronze → Silver → Gold order, localized top-five anomaly labels,
  and zero browser warning/error logs.

## 2026-08-23 — Show the top reported anomaly categories

### Changed

- Extended the pipeline-health API with a deterministic top-five anomaly
  category aggregate from the current anomaly registry, ordered by frequency.
- Added human-readable English and French labels for the anomaly rule IDs,
  with ranked cards and counts on `/pipeline-health`.
- Versioned the health request contract so browsers do not reuse a cached
  pre-category response after the release.

### Verified

- The live snapshot `2026-08-23` reports: large year-over-year change (2,388),
  digit transcription error (1,578), superseded declaration (333),
  conflicting same-period values (301), and factor-of-ten error (236).
- `make backend-test` passed 13 Worker tests/typecheck and 47 bridge tests;
  `make frontend-test` passed 29 tests and the production build. Full Ruff
  checks, format checks, package build, and GitHub Actions run
  [32658369775](https://github.com/louispaulet/YAHATVP/actions/runs/32658369775)
  passed.
- Deployed Cloud Run bridge revision `hatvp-dashboard-api-00020-j6j`, Worker
  version `0669aaee-f308-43fd-a298-d9a2cbf669ba`, and GitHub Pages revision
  `f33d7fca0df65b7c0859f79fb224a930cd835b0c`. All Worker smoke routes and the
  custom-domain frontend returned HTTP 200.
- Chrome verified the French and English labels, visible countdown, Bronze →
  Silver → Gold layer order, five category cards, and zero warning/error
  console entries. No ingestion replay was needed because this release only
  changes the health aggregate and presentation.

## 2026-08-23 — Order pipeline layers by processing flow

### Changed

- Ordered the pipeline-health layer card deterministically as Bronze, Silver,
  then Gold, even when the API returns the layer rows in another order.

### Verified

- The frontend regression fixture now deliberately scrambles the API order;
  `make frontend-test` still passes all 29 tests and the production build.
- Published the frontend and verified the live French page in Chrome renders
  Bronze at the top, Silver in the middle, and Gold at the bottom with no
  warning or error console entries.

## 2026-08-23 — Restore pipeline countdown card visibility

### Fixed

- Fixed the pipeline-health countdown card rendering white-on-white because the
  shared `.dashboard-card` background overrode its Tailwind background utility.
  The countdown now has an explicit emerald surface, white timer text, and a
  live timer landmark for assistive technology.

### Verified

- `make frontend-test` passed with 29 tests and the production Vite build.
- `make backend-test` passed with 13 Worker tests, typecheck, and 47 bridge
  tests.
- Published the frontend and verified the live cache-busted custom-domain page
  in Chrome: visible countdown, French view, emerald computed background, and
  zero warning/error console entries.

## 2026-08-23 — Split source ingestion and publish pipeline health

### Changed

- Split raw acquisition from retained-source processing. The official HATVP
  source keeps the existing raw path and weekly Cloud Run/Scheduler cascade;
  the `wayback_github` source now retains its original
  `declarations.xml.zip`, extracted XML, source hash state, and provenance.
- Added `pipeline-ingest`, `pipeline-process`, `pipeline-archive-ingest`, and
  `pipeline-archive` Make targets. Higher-layer anomaly input is deduplicated
  by declaration UUID while Bronze and historical Silver retain every source
  occurrence.
- Added the bilingual `/pipeline-health` dashboard route, fixed health API
  slice, source counts, Bronze/Silver/Gold row and review counts, quality
  summary, anomaly registry summary, and Monday 07:00 Europe/Paris countdown.

### Verified

- The local Wayback archive replay processed 14,026 declarations with zero
  quality errors, 13,988 Gold declaration rows, and 13,121 retained review
  flags. A second archive ingestion returned `NO_CHANGE`; a same-date archive
  with different bytes failed the immutable snapshot guard.
- GitHub Actions Test and deploy run
  [32655288176](https://github.com/louispaulet/YAHATVP/actions/runs/32655288176)
  passed the full Python suite, Ruff, package build, and deployed the
  ingestion job image. The forced official execution `hatvp-ingestion-7jz78`
  completed successfully in 4m35s, loaded all 13 Bronze/Silver/Gold/registry
  tables, and ended `SUCCESS_WITH_WARNINGS` with zero quality errors.
- Deployed Cloud Run bridge revision `hatvp-dashboard-api-00018-prz`, Worker
  version `1dd56e6e-dcd0-440e-ae54-b7bcb7559213`, and the GitHub Pages frontend.
  Production health, aggregate, search, and frontend routes returned HTTP 200;
  Chrome verified the hash-routed health page in French and English with no
  warning or error console entries.

### Follow-up

- The production one-off Wayback backfill remains pending because the local
  user-run GCS/BigQuery path needs Application Default Credentials. No
  service-account key was created or requested.

## 2026-08-21 — Select Highlights by latest name+surname declaration

### Changed

- Changed current Highlights selection to choose exactly one latest declaration
  per normalized first-name/surname pair before any income or asset analysis.
- Removed mandate-period, organisation, and date-of-birth partitioning from the
  current-issue selector so later corrective filings replace earlier filings
  for the same displayed name.
- Restricted current income and asset cards to the four review-oriented
  compensation rules; supersession and same-period conflict history remains in
  the audit layers.

### Verified locally

- Read-only BigQuery dry run against snapshot `2026-08-19` selected Warsmann's
  2025-03-31 modificative declaration `d1bb952f-ad78-4d04-b498-915e0995a38a`
  instead of the older `5ef9ca8a-7101-407b-aa8d-8507aa415a52` filing.
- Jean-Luc Ruelle collapsed from two candidate rows to one latest declaration;
  the candidate list was regenerated before deployment.
- `make backend-test`, `make frontend-test`, `uv run pytest`, Ruff, `uv build`,
  and the generated live BigQuery query all passed.

### Deployed and verified

- Cloud Run bridge revision `hatvp-dashboard-api-00017-dpz` and Worker version
  `66a5958a-074e-4a3c-b5f3-6ae8b89cf0b8` serve the approved selector.
- GitHub Actions Test and deploy run
  [32429301099](https://github.com/louispaulet/YAHATVP/actions/runs/32429301099)
  passed for commit `74d580d`.
- Production health, overview, income, assets, declarations, search, and
  frontend routes returned HTTP 200. The live Highlights page shows no old
  Warsmann €2.6M card, one Ruelle candidate, and no browser console errors or
  warnings.

## 2026-08-21 — Restrict Highlights to current review signals

### Changed

- Updated the Highlights bridge query to use the latest person-level
  declaration version for each mandate period and to read current anomaly
  lifecycle records directly from `anomaly_registry`.
- Excluded superseded and resolved income/asset records from the public
  Highlights cards while retaining source values and historical evidence in
  Silver and the registry.
- Updated the bilingual Highlights copy and bridge/frontend regression
  contracts to describe the current-issue selection.

### Verified locally

- The generated BigQuery query ran against snapshot `2026-08-19` and no longer
  returned Nathalie Goulet’s superseded initial declaration
  `81068658-e43c-4bf2-9947-df3a538b8182`.
- `make backend-test` passed with 12 Worker tests, typecheck, and 43 bridge
  tests. `make frontend-test` passed 27 tests and the production build.

### Deployed

- Cloud Run bridge revision `hatvp-dashboard-api-00016-5sc`, Worker version
  `bac39a3f-4b7c-43d1-8e6b-1c33496ccb61`, and GitHub Pages commit
  `808fe9e202e58968578bf38d52296ba69bc7ab07` are serving the release.
- GitHub Actions Test and deploy run
  [32425613102](https://github.com/louispaulet/YAHATVP/actions/runs/32425613102)
  passed for commit `8f70657`.

### Verified in production

- Health, overview, income, assets, declarations, search, and frontend routes
  returned HTTP 200 with cache-busted requests.
- The live Highlights response reports snapshot `2026-08-19`, eight income
  signals, eight asset signals, and eight amendment records; it no longer
  returns Nathalie Goulet’s superseded UUID `81068658-e43c-4bf2-9947-df3a538b8182`.
- Chrome verification found the current-issue copy, no old Nathalie card, and
  no warning or error console entries.

## 2026-08-20 — Fix declaration annual-value chart bars

### Changed

- Fixed the declaration detail annual-values chart so its bars use concrete
  pixel heights instead of percentage heights inside auto-sized flex columns;
  the source-reported amounts, including outliers, remain unchanged.
- Added a regression test covering multi-year annual-value rendering.

### Verified

- The focused frontend Vitest passed and the Vite production build completed.
- The full local frontend suite remains incompatible with the current Node 24
  runtime because its existing jsdom setup exposes no `window.localStorage`;
  this failure occurs before test assertions and is unrelated to the chart.
- Published the frontend to GitHub Pages (`gh-pages` commit `a54cc06`) and
  verified the cache-busted declaration route in Chrome: all 14 annual bars had
  concrete rendered heights and the page reported no console errors.

## 2026-08-20 — Publish grouped dashboard navigation

### Deployed

- Published the committed frontend build from main commit `3002914` to
  GitHub Pages; the `gh-pages` branch advanced to `77d69d1` and contains the
  new `index-DC7XE1jI.js` bundle.

### Verified

- The cache-busted custom-domain page served the new bundle and loaded the
  homepage, Highlights, analysis, search, declarant profiles, sources, data
  quality, and declaration detail routes with the expected active parent and
  child navigation states and no visible error state.
- The initial uncached request briefly served the previous CDN copy during
  propagation; a cache-busted request confirmed the new public deployment.

## 2026-08-20 — Group dashboard navigation by user task

### Changed

- Reorganized the dashboard navbar into Explore, Declarations, and Data &
  methods with contextual child navigation while preserving every existing
  route.
- Replaced ambiguous labels such as “Simple analysis” and “Age / year” with
  “Population & pay” and “Declarant profiles” in English and French.
- Updated the related page eyebrows and route-aware frontend tests.

### Verified

- Frontend Vitest passed all 26 tests, TypeScript checks passed, and the Vite
  production build completed successfully with Node 22.12.0.
- Local Chrome verification covered the homepage, highlights, analysis,
  declaration search, declarant profiles, sources, and data-quality routes in
  the grouped navigation.

## 2026-08-20 — Publish source-linked declaration highlights

### Changed

- Added a fixed read-only Highlights API slice for the largest consecutive
  completed-year income changes, highest absolute asset values, and identities
  with the most retained declaration versions. Identity and asset
  deduplication use source-backed birth dates or UUID fallbacks rather than
  name-only grouping; contact and address fields remain excluded.
- Replaced the `/explore` placeholder with a bilingual editorial page that
  explains each finding, carries review flags forward, and links every card to
  the original declaration viewer. Added Highlights entry points to the main
  navigation and homepage.
- Replaced unconstrained frontend and Worker `latest` dependency declarations
  with compatible ranges derived from the existing lockfiles.

### Deployed

- Deployed Cloud Run bridge revision `hatvp-dashboard-api-00015-vdp`,
  Cloudflare Worker version `750fdfb2-e9b6-497f-b4b9-a19483ceab98`, and
  GitHub Pages commit `5fd9e899520d7512db2081868e10752fc21e493e`.
- Confirmed `https://yahatvp.thefrenchartist.dev` serves the new
  `index-TKAfHDXA.js` bundle over HTTPS. No ingestion replay was performed.

### Verified

- The live Highlights route returned snapshot `2026-08-19` with 8 income
  changes, 8 asset records, and 8 amended identities; the deployed health,
  aggregate, analysis, search/detail, and Highlights routes returned HTTP 200.
- Followed a production highlight into its real source declaration and verified
  the rendered evidence. Desktop and mobile fixture checks covered English and
  French layouts with no horizontal overflow or console errors; production
  desktop rendered all 24 cards without overflow or console errors.
- Bridge, Worker, and frontend suites passed with 43, 12, and 26 tests. The full
  Python suite passed 158 tests; Ruff checks, package build, TypeScript checks,
  Vite build, npm audits, and the live BigQuery Highlights query also passed.
- Main workflow run
  [32310774561](https://github.com/louispaulet/YAHATVP/actions/runs/32310774561)
  passed tests, deployment configuration, image build/push, and Cloud Run Job
  deployment for commit `ed027a7`.

## 2026-08-19 — Merge dashboard PRs and redeploy the frontend only

### Released

- Merged open PRs [#35](https://github.com/louispaulet/YAHATVP/pull/35),
  [#36](https://github.com/louispaulet/YAHATVP/pull/36),
  [#37](https://github.com/louispaulet/YAHATVP/pull/37), and
  [#38](https://github.com/louispaulet/YAHATVP/pull/38), including the draft
  PRs, into `main` one at a time. Conflicts in shared frontend files and
  `CHANGELOG.md` were resolved on the PR branches before merging.
- Published main commit `749ca37` to GitHub Pages; `gh-pages` advanced to
  `7fbe2da`. The custom domain returned HTTP 200 and served the new
  `index-jmw_vcBB.js` bundle.

### Verified

- `make frontend-test` passed with 25 frontend tests and a production Vite
  build.
- The existing Worker health route returned HTTP 200 and the overview route
  reported snapshot `2026-08-19`.
- No bridge or Worker deployment and no ingestion replay were performed
  manually. The existing `main` push workflow also completed its standard
  ingestion image/Cloud Run Job deploy successfully in run
  [32306032957](https://github.com/louispaulet/YAHATVP/actions/runs/32306032957).

## 2026-08-19 — Improve declaration search usability

### Changed

- Strengthened the search input's focus treatment and added an explicit reset action.
- Added localized quick-start search examples and a clearer result summary that preserves the searched term and snapshot context.

### Verified locally

- Frontend tests cover the quick-start and reset flow; the production build completes successfully.

## 2026-08-19 — Redesign the simple analysis dashboard

### Changed

- Reworked the public simple-analysis page into a chart-led editorial layout:
  the average/median salary comparison now leads the page, DOB leaderboards
  are paired in one evidence section, and age-bin details are compact and
  scannable rather than repetitive cards.
- Retained all existing data, localisation, review labels, charts, and the
  zero-salary control. Added a development-only Vite API proxy switch to
  visually verify the frontend against the deployed read-only API.

### Verified

- Frontend fixture suite: 24 tests passed. TypeScript production build passed.
- Browser verification at 1440 × 1024 and 390 × 844 confirmed the loaded
  English analysis route, responsive layout, and zero-salary control. The
  selected design-to-implementation comparison is recorded in
  `website/hatvp-transparency-dashboard/frontend/design-qa.md`.

## 2026-08-19 — Refine dashboard homepage presentation

### Changed

- Rebalanced the dashboard navigation, hero, metric cards, and content spacing
  for a more legible editorial hierarchy while retaining every existing
  dashboard metric and data source.
- Made asset and gender-by-position charts size themselves to their data,
  widened the detailed gender panel, and separated chart summaries with clear
  visual rules to prevent crowded labels and overlapping categories.
- Corrected the snapshot loading markup so the loading indicator is no longer
  nested inside a paragraph element.

### Verification

- `npm run build` completed successfully in
  `website/hatvp-transparency-dashboard/frontend`.
- Visual review covered the refreshed homepage at desktop width; local API
  data requests are unavailable without the separately running Worker.

## 2026-08-19 — Remove the not-yet-ready explorer from navigation

### Changed

- Removed the `/explore` placeholder link from the dashboard navbar to free
  space for the currently available pages.
- Kept the direct `/explore` route and its coverage intact for future work.


## 2026-08-19 — Repair declarant income and asset history

### Changed

- Added source-preserving asset event dates, precision, and source-field names
  through the Parquet, Silver, Gold, and BigQuery schema-evolution contract.
- Rebuilt the declarant analysis on the latest Silver snapshot. Interest and
  patrimonial declaration families are ranked independently; only the newest
  declaration in each family contributes to the primary view, while every
  earlier filing remains available through declaration history links.
- Kept review-flagged annual income visible unchanged in this source-detail
  view and combined each amount with its role, employer, period, net/gross
  basis, eligibility, and review status. Removed the ambiguous occupation row
  counts and cross-version `×N` display.
- Replaced the repeated asset timeline with a localized latest-statement
  inventory. DTO names are confined to an expandable provenance disclosure;
  exact event dates show exact ages and year-only dates show age ranges.

### Verified locally

- The current Lecornu source has three interest and three patrimonial filings.
  The latest interest filing contains seven populated income years; the latest
  patrimonial filing contains nine assets without cross-version repetition.
- The source value `21/01/2002` is `dateSouscription` for the BRED PEPARVIE
  life-insurance policy, producing an exact subscription age of 15 rather than
  a declaration event or a rounded age of 16.
- `make backend-test frontend-test` passed with 11 Worker, 40 bridge, and 24
  frontend tests plus both TypeScript builds. The complete Python suite passed
  158 tests; Ruff, formatting, package builds, and the current-schema Silver
  BigQuery dry-run also passed. Production replay and deployment remain the
  release step recorded in `TODO.md`.

## 2026-08-19 — Merge open dashboard PRs and redeploy production

### Merged

- Marked draft PRs [#34](https://github.com/louispaulet/YAHATVP/pull/34),
  [#33](https://github.com/louispaulet/YAHATVP/pull/33), and
  [#32](https://github.com/louispaulet/YAHATVP/pull/32) ready and merged them
  into `main` at `5e4258b`, `32272ad`, and `ac2996b`. Resolved the overlapping
  `CHANGELOG.md` conflicts on the PR branches before merging.

### Deployed and verified

- GitHub Actions run
  [32292468778](https://github.com/louispaulet/YAHATVP/actions/runs/32292468778)
  passed tests, deployment configuration, image build/push, and Cloud Run Job
  deployment for `main` commit `ac2996b`.
- Forced execution `hatvp-ingestion-r52xn` completed with
  `SUCCESS_WITH_WARNINGS`, 0 quality errors, 4,031 warnings, 6,238 retained
  flags, and `bigquery_load_complete` for all 13 Bronze, Silver, Gold, and
  anomaly-registry tables. `state/latest.json` advanced to snapshot
  `2026-08-19` with pipeline SHA `ac2996b`.
- Deployed Cloud Run bridge revision `hatvp-dashboard-api-00013-cxj`, Worker
  version `45894537-802b-4a9b-9d8a-884eb50077b4`, and the frontend to
  `https://yahatvp.thefrenchartist.dev/`.
- Production smoke tests returned HTTP 200 for health, overview, income,
  assets, declarations, gender, simple-analysis, search, accented
  `Sébastien Lecornu` age-analysis, declaration XML detail, and the custom
  frontend. All dashboard responses reported snapshot `2026-08-19`; the detail
  XML contained the searched declaration UUID.

## 2026-08-19 — Refine salary age analysis and leaderboard readability

### Changed

- Restricted salary age-bin statistics and zero-salary counts to ages 18–100;
  DOB leaderboards continue to retain and label implausible ages.
- Added a checked-by-default localized “exclude 0€ salary” control, with an
  all-values toggle for comparison, and added a zero-salary count chart using
  the same five-year age bins.
- Removed the leaderboard’s horizontal scroll dependency by using visible,
  wrapping fixed-width columns so implausible DOB review badges remain readable.

### Verified

- Bridge tests: 37 passed; frontend tests: 22 passed; Vite production build
  passed; Chrome local fixture checks passed in English and French at desktop
  and 390px widths with no horizontal overflow or console warnings/errors.

## 2026-08-19 — Fix accent-insensitive dashboard search

### Fixed

- Removed combining Unicode marks after BigQuery NFD normalization in the
  shared dashboard search expression, so `Sébastien Lecornu` matches the HATVP
  source spelling `Sebastien Lecornu` in the age-analysis route and declaration
  search.

### Verified

- Bridge fixture tests assert the accent-folding SQL for both analysis and
  declaration search. A read-only BigQuery execution against the current Gold
  snapshot returned one Lecornu profile for `Sébastien Lecornu` and 45 matches
  for the accented declaration-search term.
- `make backend-test`, `make frontend-test`, `uv run pytest` (158 tests), Ruff,
  format checks, and `uv build` pass. The live Worker reproduced the original
  `NOT_FOUND` behavior before this source fix; production deployment remains
  the post-merge release step.

## 2026-08-19 — Add gender aggregates to the transparency homepage

### Added

- Derived a bounded `gender` field from the observed XML `civilite` values and
  carried it into the source-preserving people Parquet, Silver, Gold, and
  BigQuery table contract without changing the original `civilite` value.
- Added a fixed `/gender` bridge and Worker slice with the male/female ratio
  and gender counts by Gold mandate position.
- Added localized homepage pie and bar charts with an explicit note when
  missing or unmapped civilité values are excluded from the ratio.

### Verified

- The full Python suite passes with 158 tests, bridge tests pass with 40 cases,
  frontend tests pass with 23 cases and a production Vite build, and Worker
  tests pass with 10 cases plus TypeScript typecheck.

## 2026-08-19 — Merge analysis PRs and complete production release

### Merged

- Marked draft PRs [#31](https://github.com/louispaulet/YAHATVP/pull/31) and
  [#30](https://github.com/louispaulet/YAHATVP/pull/30) ready for review and
  merged them into `main` at `e0458ec` and `1ccd9d7`. Resolved the #30
  `CHANGELOG.md` conflict by retaining both dated entries in
  `e86e529` before pushing the branch update.

### Deployed

- GitHub Actions runs
  [32270002248](https://github.com/louispaulet/YAHATVP/actions/runs/32270002248)
  and [32271991606](https://github.com/louispaulet/YAHATVP/actions/runs/32271991606)
  passed tests, deployment configuration, image build/push, and Cloud Run Job
  deployment for `main` commits `1ccd9d7` and `93b9be1`.
- Forced execution `hatvp-ingestion-8bgt4` completed successfully with
  `SUCCESS_WITH_WARNINGS`, 0 quality errors, 6,238 retained flags, and all 13
  Bronze, Silver, Gold, and anomaly-registry tables loaded. `state/latest.json`
  advanced to snapshot `2026-08-19` with pipeline SHA `1ccd9d7`.
- Deployed Cloud Run bridge revision `hatvp-dashboard-api-00012-bj8`, Worker
  version `80ee49aa-3c37-45cd-8584-6bbe3a009f05`, and the frontend to
  `https://yahatvp.thefrenchartist.dev/`.

### Fixed and verified

- Fixed the new BigQuery analysis SQL: grouped simple-analysis age bins before
  calculating medians and derived asset relative age from the typed DOB date.
  Added regression assertions; bridge tests (37), Worker tests (9), frontend
  tests (22), TypeScript typecheck, Vite build, BigQuery dry-runs, and live
  simple/age queries pass.
- Public smoke tests return HTTP 200 for all dashboard slices, search/detail,
  both analysis routes, Worker health, and the custom-domain hash routes; all
  API responses report snapshot `2026-08-19`.

## 2026-08-19 — Prepare a current HATVP anomaly handoff shortlist

### Added

- Added [`reports/06-hatvp/2026-08-19-hatvp-anomaly-shortlist.md`](reports/06-hatvp/2026-08-19-hatvp-anomaly-shortlist.md), a BigQuery-backed review of the 2026-08-19 anomaly registry and ten source-linked declarations selected for human HATVP follow-up.
- Added the paired SQL reproduction file, including the all-declarations name+surname latest-version ordering, issue-register exclusions, deduplicated registry-to-Gold joins, and the exact audited shortlist.
- Indexed the new handoff report in [`reports/00-index.md`](reports/00-index.md).

### Verified

- BigQuery profile: 5,026 registry rows, 5,024 linked to Gold, 1,832 active, and 3,194 internally previously reported.
- Exclusion-aware candidate query: 701 deduplicated anomaly IDs across 637 latest normalized name+surname pairs.
- All ten selected declaration UUIDs verified as `name_version_rank = 1`; the live hash-routed public `/#/quality-issues` page showed 10 open and 0 solved issues, and its linked names and issue families were excluded.

## 2026-08-19 — Add DOB quality and age/year analysis pages

### Added

- Added typed `date_naissance_date`, `date_naissance_year`, and explicit
  `date_naissance_quality_status`/reason fields to the source-preserving
  people rows carried into Silver and Gold. Raw DOB values remain unchanged;
  implausible and conflicting values stay visible for review.
- Added `asset_acquisition_year_raw` and `asset_acquisition_year` fields from
  observed asset source fields, preserving the complete raw asset record.
- Added fixed public bridge/Worker routes for snapshot-level
  `/simple-analysis` and parameterized `/age-analysis?q=...` views.
- Added localized `/analysis` and `/age-analysis` frontend pages. The first
  includes youngest/oldest DOB leaderboards and five-year average/median salary
  bins; the second defaults to Sébastien Lecornu and shows annual income
  sources, occupations, and acquisition-year assets with declarant search.

### Verified

- 44 focused pipeline tests, 37 bridge tests, 22 frontend tests plus a Vite
  production build, and 9 Worker tests plus TypeScript typecheck pass.
- Chrome MCP verified `/analysis` and `/age-analysis` locally: the leaderboards,
  five-year salary chart, Lecornu profile, annual income, occupations, asset
  timeline, and accent-insensitive search rendered without console warnings or
  horizontal overflow.
- Opened draft PR [#31](https://github.com/louispaulet/YAHATVP/pull/31) from
  `agent/age-analysis-dob-quality` for review.
- Production replay and dashboard deployment remain intentionally deferred to
  the post-merge release sequence because the new Gold columns must exist before
  the analysis queries are deployed.

## 2026-08-19 — Complete forced production replay with activity remuneration

### Deployed

- GitHub Actions run [32202288517](https://github.com/louispaulet/YAHATVP/actions/runs/32202288517) passed tests, deployment configuration, image build, and Cloud Run Job deployment for commit `004b206`.
- Forced execution `hatvp-ingestion-8lnvd` ran with `--force` and completed successfully with `SUCCESS_WITH_WARNINGS`.

### Verified

- Quality completed with 106,351 income rows, 0 quality errors, 4,031 warnings,
  and 6,238 retained review flags.
- Cloud Logging emitted `bigquery_load_complete` for all 13 Bronze, Silver,
  Gold, and anomaly-registry tables; the 2026-08-19 snapshot is present in
  BigQuery, including 106,351 unified incomes and 5,026 registry rows.
- `hatvp/state/latest.json` was updated at `2026-08-19T00:50:22Z` with
  pipeline commit `004b206` only after the successful layer writes.

## 2026-08-19 — Normalize date-valued provenance fields in registry rows

### Fixed

- Extended Parquet frame normalization to convert every date/datetime value to
  ISO text before schema casting, including `source_snapshot_date`, whose
  registry contract is textual rather than typed `DATE`.

### Verified

- The regression now covers mixed string/date values in both registry date
  fields; the full Python suite passes with 148 tests, Ruff passes, and the
  package builds successfully.
- Production replay `hatvp-ingestion-f2gst` reached quality completion with
  106,351 income rows and zero quality errors, then failed before layer loading
  on this remaining registry field; another forced replay is required.

## 2026-08-19 — Normalize mixed registry snapshot dates before Parquet writes

### Fixed

- Normalize `date` and `datetime` values to ISO date text before Polars builds
  typed Parquet frames, allowing historical registry rows and current string
  snapshot dates to coexist safely.

### Verified

- Added a mixed string/date registry fixture regression; the full Python suite
  passes with 148 tests, Ruff passes, and the package builds successfully.
- The first production replay exposed this issue before any Bronze, Silver,
  Gold, or registry load completed; a fresh forced replay remains required after
  the redeployed fix.

## 2026-08-19 — Include recent professional-activity remuneration in incomes

### Fixed

- Added `income_stream=activity_remuneration` rows for every annual amount in
  the configured `activProfCinqDerniereDto` section, including explicit zeroes.
- Preserved the source activity description, employer, dates, remuneration
  basis, and complete annual amount list in each row's raw evidence.
- Fixed the activity summary row to expose an amount rather than the nested
  source year when remuneration is present.

### Verified

- The live Sébastien Lecornu declaration contains six recent professional
  activities with 15 annual remuneration values; the fixture regression keeps
  every multi-year value as a separate normalized income row.
- Focused parser and income-quality tests pass, including source-stream counts
  and raw-record reconciliation.

## 2026-08-19 — Merge open dashboard PRs and redeploy the frontend

### Deployed

- Merged PR [#28](https://github.com/louispaulet/YAHATVP/pull/28) at
  `499abae` and PR [#29](https://github.com/louispaulet/YAHATVP/pull/29) at
  `fa93e55`, resolving each branch against the current `main` first.
- Published the `fa93e55` frontend with `make frontend-deploy` to the
  `gh-pages` head `b2a1d3f`, using the existing Worker API URL and preserving
  the custom domain `https://yahatvp.thefrenchartist.dev/`.
- The merge-triggered GitHub Actions run
  [32198881494](https://github.com/louispaulet/YAHATVP/actions/runs/32198881494)
  passed tests, deployment configuration, image build/push, and Cloud Run Job
  deployment for `hatvp-ingestion` at image tag `fa93e55`.

### Verified

- Local dashboard preflight passed: backend tests (8 Worker tests and 31 bridge
  tests), frontend tests (19), and frontend production build.
- Worker health and dashboard routes returned HTTP 200, and both GitHub Pages
  fallback and custom-domain HTML served the fresh `index-5U5WzxJB.js` bundle.
- No forced ingestion replay was run because the merged changes are frontend
  only; the automatic main-branch deployment was sufficient.

## 2026-08-19 — Show calendar durations for open issues

### Changed

- Updated the quality-issues table to display unresolved time as calendar years,
  months, and days instead of a raw day count, using Europe/Madrid calendar
  dates to match the source contact dates.

### Verified

- Frontend fixture suite passes with 19 tests and the Vite production build
  succeeds; the fixed-date test covers multi-unit and same-day durations.

## 2026-08-19 — Add a privacy-safe HATVP quality issues page

### Added

- Added a localized `/quality-issues` dashboard page backed by a static local
  JSON register containing only issue type, contact date, public HATVP links,
  and solved state; unresolved durations are calculated from contact dates.
- Kept source CSVs, emails, message contents, HATVP replies, Gmail URLs, and
  message identifiers out of the repository.

### Verified

- Frontend fixture suite passes with 19 tests and the Vite production build
  succeeds.
- The local page renders 10 unresolved rows, and the mobile smoke check reports
  no horizontal overflow.

## 2026-08-19 — Stabilize About-page source cards in both languages

### Fixed

- Made official-source cards use a container-aware header that stacks titles
  and badges when a card is narrow, then returns to a horizontal layout when
  there is room.
- Added word wrapping and a non-shrinking badge so the English source titles
  cannot render underneath their action labels.

### Verified

- Frontend unit tests and the production Vite build pass.

## 2026-08-19 — Merge and production-replay the anomaly lifecycle fix

### Deployed

- Merged PR [#27](https://github.com/louispaulet/YAHATVP/pull/27) into `main`
  at commit `2669de9`; GitHub Actions run
  [32197266958](https://github.com/louispaulet/YAHATVP/actions/runs/32197266958)
  passed tests, deployment configuration, image build/push, and Cloud Run Job
  deployment.
- Forced the production `hatvp-ingestion` replay as execution
  `hatvp-ingestion-2sfxd`; it completed successfully with
  `SUCCESS_WITH_WARNINGS` for snapshot `2026-08-19`.

### Verified

- The deployed job used the `2669de9` image with 4 GiB memory, one task, and a
  30-minute timeout; no replay overlapped the forced execution.
- Cloud Logging emitted `bigquery_load_complete` for all 13 Bronze, Silver,
  Gold, and anomaly-registry tables.
- BigQuery snapshot counts are Bronze 6,611/6,611/74,791/1,157, Silver
  6,611/6,611/74,791/1,157, Gold 6,605/6,605/74,730/1,157, and registry
  3,042 rows for declarations/people/incomes/assets respectively.
- The six `date_naissance` registry rows retain `PERSON_DOB_IMPLAUSIBLE`,
  `known/reported`, and `previously_reported=true`, confirming the production
  BigQuery impact of the fix.
- Reconciled `TODO.md` section 3 with the completed merge, deployment, and
  forced-replay evidence.

## 2026-08-19 — Add direct anomaly lifecycle regression tests

### Added

- Added direct unit coverage for `implausible_birth` reference-date and
  configurable maximum-age boundaries, including future-date behavior.
- Added an explicit `ANOMALY_REGRESSION` registry test proving the original
  `PERSON_DOB_IMPLAUSIBLE` rule, regression status, occurrence count, and
  first/last-seen metadata remain intact.

### Verified

- Focused anomaly, configuration, and module-budget checks pass: 24 tests;
  the full repository suite passes with 146 tests.
- Reconciled `TODO.md` section 12.7 with the completed direct unit coverage.

## 2026-08-19 — Fix DOB plausibility and anomaly registry rule identity

### Fixed

- Added the YAML-backed `person_dob_max_age_years` setting, typed through
  `Settings` and overridable with `HATVP_PERSON_DOB_MAX_AGE_YEARS`; the default
  maximum age is 100 years at the reference date.
- Kept the original anomaly `rule_id` in registry rows when
  `ANOMALY_KNOWN`/`ANOMALY_REGRESSION` lifecycle occurrences are re-emitted;
  lifecycle status, `previously_reported`, `first_seen`, `last_seen`,
  `occurrence_count`, and snapshot idempotency remain intact.
- Kept all observed DOB values unchanged and retained overlapping DOB lifecycle
  signals when more than one rule applies to a source row.

### Verified

- Fixture regressions prove a 101-year-old is flagged, an 80-year-old is not,
  the observed date remains unchanged, and a previously reported anomaly keeps
  its original rule with stable first/last-seen and occurrence metadata.
- Reconciled `TODO.md` section 12.7 with explicit completed items for the
  configurable DOB threshold and original registry rule preservation.
- Local validation passes: `uv sync --locked`, 144 tests, Ruff check/format,
  `uv build`, and the live-source local dry-run, which completed with
  `SUCCESS_WITH_WARNINGS` for snapshot `2026-08-19` and zero quality errors.
- This change is validated locally only. Production BigQuery impact requires
  a later Cloud Run replay; no deployment was performed here.

## 2026-08-19 — Add the repository-local deployment skill

### Added

- Added `skills/yahatvp-deployment/SKILL.md` with the repeatable YAHATVP
  preflight, Cloud Run/Cloudflare/GitHub Pages deployment, Gold replay safety,
  smoke-test, changelog, commit, and tag workflow.
- Linked the skill from the README dashboard deployment section for future
  authorized releases.

### Verified

- The skill-creator `quick_validate.py` check passes, and `git diff --check`
  passes.

## 2026-08-19 — Release v1.0 dashboard and analytical pipeline

### Deployed

- Deployed the current ingestion image and forced a production replay with the
  Silver/Gold analytical layers enabled.
- Deployed Cloud Run bridge revision `hatvp-dashboard-api-00010-rw9` and
  Cloudflare Worker version `156d241d-e978-4306-973d-eada3ac58700`.
- Published the Vite frontend to the GitHub Pages custom domain
  `https://yahatvp.thefrenchartist.dev/`.
- Increased the ingestion Cloud Run Job memory from 2 GiB to 4 GiB and made
  the anomaly-registry `snapshot_date` a typed date for BigQuery partitioning.

### Verified

- GitHub Actions run [32194636486](https://github.com/louispaulet/YAHATVP/actions/runs/32194636486)
  passed the full Python test, lint, format, and package-build workflow and
  deployed the `71f2a77` ingestion image.
- Forced execution `hatvp-ingestion-6hpsr` completed with
  `SUCCESS_WITH_WARNINGS`; the snapshot loaded 6,611/6,611/74,791/1,157
  Bronze rows, 6,611/6,611/74,791/1,157 Silver rows,
  6,605/6,605/74,730/1,157 Gold rows, and 3,042 anomaly-registry rows.
- Worker health and the overview, income, assets, declarations, and search
  routes returned HTTP 200 for snapshot `2026-08-19`; the custom-domain
  frontend also returned HTTP 200.
- Backend fixture checks passed: 8 Worker tests, Worker typecheck, and 31
  bridge tests; frontend checks passed with 18 tests and a production build.

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

## 2026-08-23 — Link DOB leaderboard records to declarations

### Changed

- Made each DOB-quality tag in the youngest and oldest leaderboards an internal
  link to the retained declaration detail route when a declaration UUID is
  available.
- Removed the redundant five-year age-bin text grid below the salary chart;
  the chart and zero-salary breakdown remain available.

### Verified

- Frontend Vitest coverage confirms both leaderboard links and the removed text
  summary, with the existing analysis-page behavior still covered.
