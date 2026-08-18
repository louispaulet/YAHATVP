# Weekly operational monitoring — HATVP snapshots 2026-08-16 to 2026-08-18

> Source-linked review of the weekly quality reports, recurring duplicate
> declaration UUIDs, and row-count/null-rate stability.

## Outcome

The three available production snapshot reports were reviewed. The latest
validated baseline (`2026-08-17`) and the next snapshot (`2026-08-18`) have the
same normalized row counts, the same monitored null rates, zero quality errors,
and no flagged-record regression. The warning status is expected because the
known source-quality findings remain retained and visible.

The six duplicate declaration UUID groups recur in all three raw XML snapshots.
They remain source-quality issues; no raw or normalized data was corrected or
deleted. This report is the source-correction follow-up packet for the next
operator contact with HATVP and the next weekly review.

## Weekly quality report review

| Snapshot | Pipeline SHA | Status | Errors | Warnings | Flagged records | Warning streak | Quality regression |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `2026-08-16` | `f21853d` | `warning` | 0 | 3,510 | 5,763 | 1 | n/a |
| `2026-08-17` | `3c64994` | `warning` | 0 | 3,611 | 5,818 | 2 | false |
| `2026-08-18` | `b25e9c8` | `warning` | 0 | 3,611 | 5,818 | 3 | false |

The `2026-08-18` report records `missing_required_fields=0`,
`catastrophic_row_count_reductions=0`, `duplicate_declaration_ids=6`,
`negative_assets=9`, and `statistical_asset_outlier=143`. Cloud Logging also
contains the expected `quality_warning_streak` event for the third consecutive
warning-bearing snapshot. No `quality_regression` event was emitted.

The large `2026-08-16` to `2026-08-17` income-count change is the documented
deployment transition that restored annual `mandatElectifDto` remuneration
rows, not an unreviewed weekly source drift. The `2026-08-17` validation report
records the forced replay and the resulting stable `74,791` unified income rows.

## Row counts and null rates

The ongoing comparison baseline is `2026-08-17`, because that is the first
snapshot after the validated income/remuneration correction. The following
counts are identical in both `2026-08-17` and `2026-08-18`:

| Table | Rows |
| --- | ---: |
| `declarations` | 6,611 |
| `people` | 6,611 |
| `incomes` | 74,791 |
| `assets` | 1,157 |
| `mandate_remunerations` | 74,725 |
| `activities` | 23,342 |
| `participations` | 52,812 |
| `liabilities` | 109 |

The monitored null rates were also identical between the two snapshots:

| Table | Monitored fields and null rate |
| --- | --- |
| `declarations` | `declaration_uuid=0.000000`, `declaration_type_id=0.000000`, `date_depot=0.000000` |
| `people` | `declaration_uuid=0.000000`, `nom=0.000000`, `prenom=0.000000` |
| `incomes` | `declaration_uuid=0.000000`, `income_year=0.000000`, `normalized_value=0.000000` |
| `mandate_remunerations` | `declaration_uuid=0.000000`, `remuneration_year=0.000000`, `normalized_value=0.000000` |
| `assets` | `declaration_uuid=0.000000`, `asset_name=0.044944`, `normalized_value=0.000864` |

The same row-count and null-rate values were confirmed in the curated BigQuery
partitions for `declarations`, `people`, `incomes`, and `assets` on both
snapshot dates. No sudden change requires investigation.

## Duplicate UUID recurrence and source-correction packet

The raw XML source is
`https://www.hatvp.fr/livraison/merge/declarations.xml`. Each of the following
groups occurs twice in each of the `2026-08-16`, `2026-08-17`, and `2026-08-18`
raw XML snapshots, for 6 groups and 12 rows per snapshot:

| Declaration UUID | Recurrence | XML comparison |
| --- | --- | --- |
| `23a569db-f01d-406b-9d49-d77062d16c0b` | 2 in all 3 snapshots | Canonically identical; semantic SHA-256 `efee790e5c0b3c999cb5eb14f82b0e4842788920313e501069b3ac3e5965b958` |
| `3cc80dd4-5497-4119-ae82-bf748f3cf34e` | 2 in all 3 snapshots | Canonically identical; semantic SHA-256 `3e82c74fad74697318b744f536aa6d05f6438b1a7f85adec04eb5049498d5b3e` |
| `64076b58-0b72-43ed-9d06-3421ed2ad7cf` | 2 in all 3 snapshots | Canonically identical; semantic SHA-256 `91902b398e3aa9e753dbf9ca7e59daf22f562fe7dcf96338df9fe42532735e2f` |
| `918bed9f-21cc-46fd-a13a-0f3e07b4b9ce` | 2 in all 3 snapshots | Canonically identical; semantic SHA-256 `e80df913ef38e16ac27db73a841b32f049ec3815bd2e847f13bc281c06b2f7d4` |
| `9ccaaa4b-93bd-4ac3-b99c-e8e5835be9f3` | 2 in all 3 snapshots | Canonical lengths 9,912 and 9,913 bytes; identical semantic SHA-256 `9ceaa37380386bfb449e1f5398d1ddab80a4cc70d673a5bdfcffd92c06e5319d`; consistent with trailing whitespace |
| `fe395431-4550-4b8d-9251-50bd4cfd5eb0` | 2 in all 3 snapshots | Canonically identical; semantic SHA-256 `f0a6dc74105c4b68b7fb273497e36e2c618f74b8169c28b2f65adb72f22d8667` |

The correction packet preserves the exact source identifiers, recurrence
counts, semantic fingerprints, and immutable GCS evidence paths:

- `gs://yahatvp-pipeline-eu-data/hatvp/raw/snapshot_date=2026-08-16/declarations.xml`
- `gs://yahatvp-pipeline-eu-data/hatvp/raw/snapshot_date=2026-08-17/declarations.xml`
- `gs://yahatvp-pipeline-eu-data/hatvp/raw/snapshot_date=2026-08-18/declarations.xml`
- `gs://yahatvp-pipeline-eu-data/hatvp/quality/snapshot_date=2026-08-18/report.json`

The repository retains both occurrences and does not attempt to invent a
canonical declaration. An external HATVP source correction remains outside the
authority of this code change; the next operator contact should attach this
packet and verify the six groups on the next weekly snapshot.

## Verification evidence

- GCS quality reports were read for all three snapshot dates.
- Raw XML duplicate fingerprints were recomputed with the repository's
  `hatvp.triage.fingerprints.declaration_xml_fingerprints` implementation.
- BigQuery partition counts and monitored null rates were queried for the two
  latest snapshot dates.
- Cloud Logging was checked for `quality_warning_streak` and
  `quality_regression` events.
