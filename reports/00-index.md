# HATVP report index

This directory contains source-linked analysis and review evidence. Start here
before opening a report. Folders are numbered by purpose, and report filenames
use `YYYY-MM-DD-topic` so snapshots sort naturally within each topic.

## Report map

| Folder | Use it for | Current contents |
| --- | --- | --- |
| [`01-quality/`](01-quality/) | Snapshot-wide quality review | [`2026-08-16-quality-triage.md`](01-quality/2026-08-16-quality-triage.md) is the human-readable review; [`2026-08-16-quality-triage.json`](01-quality/2026-08-16-quality-triage.json) is the complete machine-readable register. |
| [`02-outliers/`](02-outliers/) | Statistical and source-pattern investigations | Asset outliers are one analysis in Markdown, portable HTML, and artifact JSON. Income outliers is the detailed `revenuMandatDto` appendix; revenue-stream outliers is the combined effective register for both income streams. |
| [`03-validation/`](03-validation/) | Pipeline and curated-layer validation | [`2026-08-17-bigquery-and-income-validation.md`](03-validation/2026-08-17-bigquery-and-income-validation.md) consolidates the former BigQuery findings and income-coverage recovery notes. |
| [`04-manual-review/`](04-manual-review/) | Small, source-linked declaration bundles | The `2026-08-17/6dcd326d-e076-4d7a-a428-15075a15dddd/` bundle contains a summary, selected XML, and parsed JSON for the Rachida Dati declaration. |

## Recommended reading order

1. Read the snapshot-wide disposition in `01-quality/`.
2. Read the consolidated validation report in `03-validation/` for counts,
   hashes, replay evidence, and curated BigQuery scope.
3. Use the focused reports in `02-outliers/` for source-level investigations.
4. Open a bundle in `04-manual-review/` only when a concrete declaration needs
   XML-to-normalized-row inspection.

## Naming and provenance rules

- Keep related representations under one topic folder and use the same date
  and stem. The asset outlier Markdown, HTML, and artifact JSON are deliberate
  format variants of one analysis, not separate findings.
- Merge overlapping validation notes into the canonical validation report
  before adding another snapshot-level summary.
- Keep report evidence immutable in meaning: retain snapshot dates, source
  hashes, GCS paths, stable declaration identifiers, and supersession notes.
- Suspicious values are review flags; report organization must never imply that
  a row was deleted or corrected in the source or normalized data.
