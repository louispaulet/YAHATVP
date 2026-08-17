# HATVP income coverage recovery — 2026-08-17

## Executive summary

The initial BigQuery `incomes` table showed only 66 rows because it represented
only populated `revenuMandatDto` category values. The HATVP XML also contains
annual remuneration values nested under `mandatElectifDto`; those values were
already preserved in the dedicated `mandate_remunerations` table, but were not
included in the curated `incomes` view.

The parser now exposes both observed revenue streams in `incomes`, tagged by
`income_stream`, without collapsing years, dropping explicit zeroes, or
removing raw source context.

## Snapshot results

| Metric | Result |
| --- | ---: |
| Declarations | 6,611 |
| Unified `incomes` rows | 74,791 |
| `mandate_remuneration` rows | 74,725 across 5,850 declarations |
| `revenu_mandat` rows | 66 across 9 declarations |
| Numeric income rows | 74,791 |
| Quality errors | 0 |
| Quality warnings | 3,611 |
| Flagged records retained for review | 5,818 |

The annual remuneration stream covers 88.5% of declarations in this snapshot;
the source does not provide a remuneration item for every declaration. The
sparse `revenuMandatDto` stream remains visible separately: 55 declarations
contain the section, but only 9 contain populated category values.

## Root cause and fix

The 66-row result was a scope mismatch, not a failure to parse the nested XML.
The parser correctly extracted the annual `mandatElectifDto` values into
`mandate_remunerations`, while the curated `incomes` table intentionally read
only `revenuMandatDto`.

The fix:

- emits one unified income row per annual `mandatElectifDto` remuneration;
- adds `income_stream=mandate_remuneration` or `revenu_mandat`;
- preserves source year, raw French-formatted value, normalized numeric value,
  source item index, remuneration index, and `raw_record_json`;
- keeps the detailed `mandate_remunerations` table unchanged as a source-specific
  analytical view;
- retains empty category slots as non-observations and retains zero-valued
  annual remuneration rows as valid source records.

The BigQuery loader was also made schema-evolution safe. It adds newly staged
columns to existing tables and inserts by explicit column names, avoiding
positional `SELECT *` failures when the curated schema grows.

## Production verification

The successful production replay used parser/loader revision
`1000d0b03a6fdcebef75b467fca1cf7a95860d84`, deployed by GitHub Actions run
`32049058688`.

| Check | Evidence |
| --- | --- |
| Forced rebuild | `hatvp-ingestion-f6mdg` succeeded with zero quality errors |
| Repeat forced rebuild | `hatvp-ingestion-ts6jb` produced identical counts and fingerprints |
| Unchanged-input path | `hatvp-ingestion-rmclb` returned `NO_CHANGE` |
| BigQuery `incomes` partition | 74,791 rows for `2026-08-17` |
| BigQuery stream split | 74,725 `mandate_remuneration`; 66 `revenu_mandat` |
| BigQuery row fingerprint | `-2929076836325473210` |
| `snapshot_date` type | `DATE`, used for partitioning |
| New BigQuery columns | `income_stream` (`STRING`), `remuneration_index` (`INT64`) |

The failed first replay stopped at the old 14-column BigQuery insert and did
not advance `state/latest.json`. After the loader migration, both the forced
replay and the repeat-load succeeded. The unchanged replay left the state
record unchanged.

## Local and source evidence

- Full local checks: 39 tests, Ruff, formatting, and package build passed.
- Live local-output run completed with `SUCCESS_WITH_WARNINGS` and zero quality
  errors.
- XML SHA-256:
  `865261857f88ec6c262558bc115b37b94f97ea3418b6829267aa6cbd1458fdaf`
- CSV SHA-256:
  `156463f08b88dd884dcbb0721d9295869c8df7595cf98696162030123938dd29`
- Raw XML:
  `gs://yahatvp-pipeline-eu-data/hatvp/raw/snapshot_date=2026-08-17/declarations.xml`
- Unified income Parquet:
  `gs://yahatvp-pipeline-eu-data/hatvp/silver/incomes/snapshot_date=2026-08-17/data.parquet`
- Quality report:
  `gs://yahatvp-pipeline-eu-data/hatvp/quality/snapshot_date=2026-08-17/report.json`

## Interpretation and follow-up

The recovered count is suitable for year-by-year remuneration analysis, but
the two streams should not be summed without considering their different
semantics. `revenuMandatDto` is a declaration-level income-category stream;
`mandatElectifDto` is an annual remuneration stream tied to elected mandates.

Continue monitoring stream-specific row counts, source labels, zero values,
outliers, and duplicate declaration UUIDs after each weekly snapshot. Suspicious
source values remain flagged and available for review; none were silently
deleted or corrected.
