# Changelog

The complete earlier release history is preserved in
[`documentation_archive/20261121T192159Z_CHANGELOG.md`](documentation_archive/20261121T192159Z_CHANGELOG.md).

## 2026-11-21 — Reduce ingestion memory and repeated quality alerts

### Changed

- Release Bronze-only parsed rows after Bronze persistence and before Silver
  construction; preserve all source tables in Bronze.
- Make same-date warning-streak processing idempotent and emit repeated-warning
  events only for changed finding fingerprints. Quality checks and Monitoring
  policies are unchanged.
- Updated monitoring guidance and documented the read-only production
  investigation. No production replay, source rewrite, or alert-policy change
  was performed.

### Verified

- Focused regression tests: 15 passed. The full local CI sequence passed:
  `uv sync --locked`, Ruff check, Ruff format check, `uv build`, and
  `uv run pytest` (192 passed on Python 3.14.7). The push-triggered GitHub
  workflow status will be added to
  [`the investigation report`](reports/03-validation/2026-11-21-ingestion-quality-alert-investigation.md).
- Production state remains at 2026-11-02; the next scheduled run is
  2026-11-23 06:00 UTC and requires review after deployment.

## 2026-11-01 — Retain recent pipeline images

- Enabled and verified Artifact Registry cleanup policies for the pipeline and
  dashboard API images. The follow-up storage measurement remains open in
  `TODO.md`; detailed evidence is preserved in the archived changelog.
