# YAHATVP TODO

This is the active execution plan. Superseded status and completed work are in
[`documentation_archive/20261121T192159Z_TODO.md`](documentation_archive/20261121T192159Z_TODO.md)
and earlier TODO archives.

## Current status

The latest fully processed production snapshot is 2026-11-02. The changed
2026-11-16 HATVP source files are safely archived, but that run exhausted the
32 GiB Cloud Run limit before Silver and BigQuery. `state/latest.json` remains
at 2026-11-02. The targeted repairs pass the full local CI sequence; review
the [investigation report](reports/03-validation/2026-11-21-ingestion-quality-alert-investigation.md)
for evidence and follow-up.

## Open work

- [ ] Review the normal scheduled execution on 2026-11-23 (06:00 UTC): all 13
  BigQuery tables, `pipeline_complete`,
  `state/latest.json` advancing after full success, preserved Silver
  publication/search behavior, and no new memory failure. Do not start a
  manual replay without explicit production approval.
- [ ] Continue human review of duplicate declaration IDs, repeated names,
  negative values, and statistical outliers. Preserve source evidence and
  follow up with HATVP where warranted.
- [ ] Verify Artifact Registry cleanup and daily layer collection after the
  2026-11-01 purge; current report has 16 pipeline versions at 37,517.529 MB.
- [ ] Verify `cloud_pricing_export` and resource-level net-EUR reporting after
  pricing-export propagation.
- [ ] Add semantic/content hashes after exact-byte hashing is stable; improve
  schema-drift reporting; and evaluate partition-aware BigQuery retention,
  data catalog coverage, and a small Cloud Logging/quality dashboard.

## Recurring operations

- Review each weekly quality report and quarantine record; distinguish source
  warnings from processing failures and investigate changed fingerprints.
- Review HATVP schema changes before changing normalization; add fixtures for
  newly observed source edge cases.
- Keep raw source bytes, historical records, and provenance immutable.

## Recent completed work

- [x] Investigated Cloud Run failures through 2026-11-16; fixed avoidable
  parsed-table retention during Silver construction and duplicate warning
  alerts for unchanged findings. Full local CI passed: 192 tests, Ruff,
  formatting, and package build; GitHub Actions run `44941647862` passed and
  deployed image SHA `f67575622f7c26012ad9673653c59ee7707d8e2b`. The
  investigation report records the deployed image digest and evidence.
- [x] Recorded the 2026-11-16 quality report: zero errors, 40,357 warnings,
  57,622 flagged records, and no flagged-record regression.
