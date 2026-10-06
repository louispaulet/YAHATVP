# YAHATVP TODO

This is the concise active execution plan. Completed pre-v1.0 setup, deployment,
validation, architecture, and dashboard checklists are preserved in
[`documentation_archive/20260826T215722Z_TODO.md`](documentation_archive/20260826T215722Z_TODO.md).

## Current status

The ingestion pipeline, Google Cloud deployment, Bronze → Silver → Gold and
anomaly-registry layers, source archives, and v1.5 transparency dashboard are
implemented, deployed, and covered by local and production verification. The
latest dashboard release repairs section navigation and cancelled-request races,
following the story-first homepage and canonical website design and tone guides.
Production ingestion recovered on 2026-10-06: the 8 vCPU / 32 GiB job completed
all 13 BigQuery loads and advanced the snapshot to 2026-10-06 with zero quality
errors and no flagged-record regression. The pipeline now prefers Bronze
history per snapshot while retaining Silver-only legacy history.
The cumulative publication-lifecycle change is fixture-tested locally; its
first production load remains an explicit verification follow-up below.

## Open work

- [ ] Verify the first production ingestion after the publication-lifecycle
  release: all 12 Bronze/Silver/Gold tables should load cumulative snapshot
  partitions, with status timestamps and the unpublished Gold inclusion rule.
- [ ] Complete human source-document review and any external HATVP follow-up;
  the repository report does not assert that a flagged value is erroneous.
- [ ] Review the 20-run quality-warning streak reported by snapshot 2026-10-06;
  its 40,156 warnings had zero errors and no flagged-record regression.
- [ ] Add semantic/content hashes after the exact-byte hash path is stable.
- [ ] Add richer schema-drift reporting for new XML sections and fields.
- [ ] Add a small operational dashboard from Cloud Logging and quality reports.
- [ ] Add partition-aware BigQuery retention and cost controls.
- [ ] Add data catalog/documentation for the normalized tables.
- [ ] Verify `cloud_pricing_export` and resource-level net-EUR reporting after
  initial pricing-export propagation; the export is enabled and its first
  transfer run is still in progress.

## Recurring operations

- Review the quality report after each weekly ingestion run.
- Monitor row counts, null rates, warning streaks, and recurring source-quality
  flags; preserve source evidence when follow-up is needed.
- Review HATVP schema changes before changing normalization logic, and add a
  fixture before fixing a newly observed source edge case.
- Keep historical raw snapshots immutable and periodically review retention
  settings without deleting required audit history.

## Recent completed work (2026-08-19 through 2026-10-06)

- [x] Recovered production ingestion from repeated Cloud Run memory-limit
  failures by raising the scheduled profile to 8 vCPU / 32 GiB and avoiding
  duplicate Bronze/Silver history loads. CI run `37518534872` passed; execution
  `hatvp-ingestion-pjq2w` loaded all 13 BigQuery tables in 11m30s and advanced
  `state/latest.json` to snapshot `2026-10-06`. Quality status is
  `SUCCESS_WITH_WARNINGS`, with zero errors and no regression. The 20-run
  warning streak remains open for review; see the
  [recovery report](reports/03-validation/2026-10-06-ingestion-memory-recovery.md).

- [x] Fixed hash-router section navigation and cancelled-request races in PR
  #52, merged and deployed the frontend on 2026-09-14. All 45 frontend tests,
  production build, backend checks, CI, Pages deployment, and live navigation
  checks pass; the published bundle matches the local build byte for byte.

- [x] Deployed the miscellaneous-asset highlights release: Cloud Run revision
  `hatvp-dashboard-api-00036-hrv`, Worker version
  `2589073d-560a-4081-953e-88152d522bc1`, and the custom frontend domain;
  production smoke tests passed and the €30,000 “diamant solitaire” row is
  present in the ranked response.
- [x] Replaced the empty asset-review slot with a source-linked top-10 ranking
  of positive-valued `bienDiverDto` items, including the “diamant solitaire”
  fixture example; frontend and backend checks pass.
- [x] Removed the empty paused asset-anomaly signal from Explore and its
  navigation link; the frontend test suite and production build pass.
- [x] Added a small gap between dark hero sections and white search/profile
  cards so adjacent surfaces remain visually distinct.
- [x] Changed the homepage women’s-share chart from a manual disclosure to a
  one-shot viewport-triggered expansion that loads the plot and keeps it open.
- [x] Deployed the dashboard UI/UX release: Cloud Run bridge revision
  `hatvp-dashboard-api-00033-dwg`, Worker version
  `6aebe78c-4325-4fb1-b3fd-75d9ea68da45`, and the custom GitHub Pages domain;
  public route smoke tests passed without running an ingestion replay.
- [x] Improved dashboard UI/UX with skip navigation, route focus, clearer
  search loading and guidance, snapshot-reading disclosure, declaration
  section navigation, technical-field disclosure, and corrected chart
  accessibility labels; the follow-up pass adds locale-backed declaration
  labels, empty-section disclosures, source XML copy support, snapshot context,
  signal explanations, profile announcements, and chart text summaries.
  Quality-register rows, action icons, responsive navigation, and metric scope
  copy were also polished without changing data contracts; declaration amount
  bars now include an equivalent annual-value table and publication-history
  context for original and later public versions.

- [x] Merged open PRs #46–#51, resolved tracking-document conflicts, deployed
  commit `5352965`, and forced a successful production replay; the scheduled
  Cloud Run Job profile was restored after the temporary high-memory retry.
- [x] Fixed income coverage counting whitespace-only values as populated; added
  a fixture regression test.
- [x] Fixed historical layer loading so legacy Silver partitions remain
  available when newer Bronze partitions also exist for the same table.
- [x] Released v1.0 through v1.5 dashboard functionality, including analysis,
  declarant search, Highlights, pipeline health, and grouped navigation.
- [x] Added source-linked declaration details, DOB quality links, Wayback and
  Hugging Face archive coverage, and raw/deduplicated source counts.
- [x] Applied the current anomaly and metric-eligibility policy to public
  income and asset statistics while retaining audit evidence.
- [x] Added the top-10 gender-by-position chart showing women’s percentage,
  responsive legend behavior, and explicit popularity ordering.
- [x] Redesigned the homepage as a story-first civic snapshot with staged
  loading, bilingual copy, reusable sections, and responsive browser QA.
- [x] Balanced and published the homepage supporting-evidence layout with a
  snapshot-coverage panel and mobile-safe declaration table.
- [x] Added canonical repository-level design and tone-of-voice guides for
  future dashboard work.
- [x] Fixed Gold membership flags so clean selected rows remain active in
  documented metrics while anomalous values stay ineligible.
- [x] Fixed split-stage `--dry-run` handling so ingest, archive-ingest, and
  process do not require storage or mutate state.
- [x] Verified recent frontend, Worker, bridge, ingestion, and browser releases
  through the production deployment workflow.
- [x] Fixed CSV source-identity fallback when the first configured candidate is
  blank or a normalized missing marker.
- [x] Fixed the official cascade short-circuit so newly ingested archive
  sources are processed even when the official source is unchanged.
- [x] Fixed namespace-safe preservation of general mandate rows with quality
  metadata but no mandate label.
- [x] Fixed download validation for valid UTF-8 XML responses with a leading
  byte-order mark.
- [x] Merged open PRs #42–#45, resolved parser/test conflicts, deployed commit
  `215c48a`, forced a successful production replay, and restored the normal
  Cloud Run resource profile.
- [x] Created the EU billing export dataset, enabled detailed usage-cost
  export, and verified the current project’s Cloud Billing report.
- [x] Enabled Cloud Billing pricing export after retrying the Google-side save;
  the `Pricing BigQuery Transfer` config exists in `europe` and its first run
  is `RUNNING`. The `cloud_pricing_export` table remains pending propagation.
