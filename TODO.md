# YAHATVP TODO

This is the concise active execution plan. Completed pre-v1.0 setup, deployment,
validation, architecture, and dashboard checklists are preserved in
[`documentation_archive/20260826T215722Z_TODO.md`](documentation_archive/20260826T215722Z_TODO.md).

## Current status

The ingestion pipeline, Google Cloud deployment, Bronze → Silver → Gold and
anomaly-registry layers, source archives, and v1.5 transparency dashboard are
implemented, deployed, and covered by local and production verification. The
latest dashboard work is the story-first homepage, balanced supporting
evidence, and canonical website design and tone guides.

## Open work

- [ ] Complete human source-document review and any external HATVP follow-up;
  the repository report does not assert that a flagged value is erroneous.
- [ ] Add semantic/content hashes after the exact-byte hash path is stable.
- [ ] Add richer schema-drift reporting for new XML sections and fields.
- [ ] Add a small operational dashboard from Cloud Logging and quality reports.
- [ ] Add partition-aware BigQuery retention and cost controls.
- [ ] Add data catalog/documentation for the normalized tables.

## Recurring operations

- Review the quality report after each weekly ingestion run.
- Monitor row counts, null rates, warning streaks, and recurring source-quality
  flags; preserve source evidence when follow-up is needed.
- Review HATVP schema changes before changing normalization logic, and add a
  fixture before fixing a newly observed source edge case.
- Keep historical raw snapshots immutable and periodically review retention
  settings without deleting required audit history.

## Recent completed work (2026-08-19 through 2026-08-27)

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
- [x] Verified recent frontend, Worker, bridge, ingestion, and browser releases
  through the production deployment workflow.
- [x] Fixed namespace-safe preservation of general mandate rows with quality
  metadata but no mandate label.
