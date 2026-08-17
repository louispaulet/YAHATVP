# `revenuMandatDto` income outliers

> Technical data-quality report for the elected-person income entries embedded in HATVP declarations.

| Field | Value |
| --- | ---: |
| Snapshot date | `2026-08-17` |
| Raw source | `declarations.xml` |
| Raw source SHA-256 | `865261857f88ec6c262558bc115b37b94f97ea3418b6829267aa6cbd1458fdaf` |
| Parser revision | `1000d0b` |
| Detector | Robust median/MAD over populated elected-person category values |
| Review threshold | Absolute robust z-score > 10 |

## Executive summary

There is no evidence that the `revenuMandatDto` parser is dropping the 198 source slots as if they were 198 incomes. The 198 figure is the number of fixed category slots: **22 source groups × 9 categories**. Only **66 slots contain a numeric `revenuElu` value**, and the parser emits exactly those 66 populated category rows.

The full `revenuMandatDto` source-to-normalized funnel is shown below. The unified
`incomes` table also contains annual `mandatElectifDto` remuneration rows; this
report isolates the `income_stream=revenu_mandat` population so its category
reconciliation remains auditable:

| Stage | Count | Interpretation |
| --- | ---: | --- |
| Declarations | 6,611 | All declaration records in the XML snapshot |
| Declarations with `revenuMandatDto` | 55 | The section is sparse: 0.83% of declarations |
| Sections with at least one populated income group | 9 | 46 present sections have no populated category values |
| Source income groups | 22 | Some declarations contain several years/groups |
| Fixed category slots | 198 | 22 groups × 9 `revenuMandatItem*` slots |
| Numeric elected-person category values | 66 | 33.3% of slots; the remaining slots are empty |
| Normalized `incomes` rows (`revenu_mandat` stream) | 66 | Exact one-to-one match with the populated category values |
| Source `totalElu` aggregates | 22 | Retained for reconciliation; not emitted as duplicate income rows when categories are populated |

The 66 category values sum to **€1,098,531**, exactly matching the sum of the 22 source `totalElu` values. This is the key integrity check: the parser is not losing the income amounts shown in the source section, and it is not double-counting the group totals.

The statistical detector finds **zero formal outliers** at the pipeline threshold. The largest category value is **€82,023** for Charlotte LECOCQ (`Traitements salaires`, 2025), with a robust z-score of 5.99; it is a review candidate, but it does not cross the configured >10 threshold. There are also no negative or implausibly huge income values in this snapshot.

## What `revenuMandatDto` represents

Each populated source group has nine fixed categories such as `Indemnités d'élu`, `Traitements salaires`, `Pensions retraites rentes`, and `Revenus fonciers`. Empty XML elements are still category slots, but they are not income observations. For example, the manually reviewable Rachida Dati declaration has nine category slots, six numeric `revenuElu` values, and three empty categories; its six parsed rows total €73,005, equal to `totalElu`.

The source section is unusually sparse in this snapshot: all nine declarations with populated category values are `DSPFM` declarations. This is consistent with the field being an optional declaration section rather than a field expected on every declaration.

## Distribution by source category label

The report preserves the exact labels found in the XML. The comma/no-comma variants are source-label variants, not separate parsing paths.

| Source category label | Populated rows | Sum (€) | Median (€) | Maximum (€) |
| --- | ---: | ---: | ---: | ---: |
| `Pensions, retraites, rentes` | 7 | €297,871 | €50,656 | €52,294 |
| `Indemnités d'élu` | 10 | €296,823 | €19,391 | €60,000 |
| `Traitements salaires` | 8 | €256,048 | €29,439.50 | €82,023 |
| `Traitements, salaires` | 9 | €99,277 | €10,194 | €23,997 |
| `Autres revenus` | 8 | €85,903 | €9,000 | €21,222 |
| `Revenus fonciers` | 11 | €32,338 | €1,378 | €7,240 |
| `Pensions retraites rentes` | 2 | €23,691 | €11,845.50 | €14,691 |
| `Revenus capitaux mobiliers` | 10 | €4,996 | €481 | €879 |
| `Plus-values mobilières` | 1 | €1,584 | €1,584 | €1,584 |

For analysis that needs a canonical taxonomy, the two spelling variants of `Traitements salaires` total €355,325 across 17 rows, and the two variants of `Pensions retraites rentes` total €321,562 across 9 rows. The raw labels remain available for provenance.

## Statistical outlier result

| Metric | Result |
| --- | ---: |
| Numeric elected-person category rows | 66 |
| Minimum (€) | €78 |
| Median (€) | €9,000 |
| Median absolute deviation (MAD, €) | €8,218.50 |
| Robust scale (1.4826 × MAD, €) | €12,184.75 |
| Maximum (€) | €82,023 |
| Maximum absolute robust z-score | 5.99 |
| Formal outlier rows at z > 10 | 0 |
| Negative values | 0 |
| Values above €10 million | 0 |

The group-level `totalElu` values produce the same conclusion: 22 totals, ranging from €11,423 to €108,483, with a maximum aggregate robust z-score of 1.39 and zero formal aggregate outliers.

## Highest-value review candidates

These are not formal outliers under the configured detector. They are the highest and most distant values in the category-level distribution and are useful starting points for manual source review.

| # | Declarant | Publication date | Declaration UUID | Category | Year | Value (€) | Robust z |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: |
| 1 | Mme Charlotte LECOCQ | 2026-03-03 | `3ae51772-5b1b-4d15-afe8-4f018589442e` | Traitements salaires | 2025 | €82,023 | 5.99 |
| 2 | Mme Marie-Pierre VEDRENNE | 2026-04-05 | `59e40cfb-7b2a-481a-9141-a8e25e028f1f` | Indemnités d'élu | 2024 | €60,000 | 4.19 |
| 3 | Mme Marie-Pierre VEDRENNE | 2026-04-05 | `59e40cfb-7b2a-481a-9141-a8e25e028f1f` | Indemnités d'élu | 2025 | €60,000 | 4.19 |
| 4 | Mme Maud BREGEON | 2026-07-27 | `f2b84cea-cbba-4e05-a6a6-cb656fb4a80e` | Indemnités d'élu | 2025 | €57,645 | 3.99 |
| 5 | Mme Maud BREGEON | 2026-04-30 | `f9e780b3-8763-442c-ba34-50e31f6206e7` | Indemnités d'élu | 2025 | €57,645 | 3.99 |
| 6 | Mme Florence Ribard | 2026-04-14 | `0a10a606-2318-43cf-8fa8-22d392559ff5` | Pensions, retraites, rentes | 2023 | €52,294 | 3.55 |
| 7 | Mme Florence Ribard | 2026-04-14 | `0a10a606-2318-43cf-8fa8-22d392559ff5` | Pensions, retraites, rentes | 2025 | €51,833 | 3.52 |
| 8 | Mme Florence Ribard | 2026-04-14 | `0a10a606-2318-43cf-8fa8-22d392559ff5` | Pensions, retraites, rentes | 2024 | €50,734 | 3.43 |
| 9 | Mme Florence Ribard | 2026-04-14 | `0a10a606-2318-43cf-8fa8-22d392559ff5` | Pensions, retraites, rentes | 2022 | €50,656 | 3.42 |
| 10 | Mme Florence Ribard | 2026-04-14 | `0a10a606-2318-43cf-8fa8-22d392559ff5` | Pensions, retraites, rentes | 2021 | €45,704 | 3.01 |
| 11 | Mme Rachida Dati | 2026-04-22 | `6dcd326d-e076-4d7a-a428-15075a15dddd` | Traitements salaires | 2025 | €41,571 | 2.67 |
| 12 | Mme Florence Ribard | 2026-04-14 | `0a10a606-2318-43cf-8fa8-22d392559ff5` | Pensions, retraites, rentes | 2020 | €37,940 | 2.38 |
| 13 | Mme Maud BREGEON | 2026-07-27 | `f2b84cea-cbba-4e05-a6a6-cb656fb4a80e` | Traitements salaires | 2025 | €32,100 | 1.90 |
| 14 | Mme Maud BREGEON | 2026-04-30 | `f9e780b3-8763-442c-ba34-50e31f6206e7` | Traitements salaires | 2024 | €30,379 | 1.75 |
| 15 | Mme Amélie de Montchalin | 2026-03-14 | `3261cb23-f5cd-4d7f-9622-732629e474b2` | Traitements salaires | 2025 | €28,500 | 1.60 |

## Declarations with the largest category sums

The sums below add the populated category rows within each declaration UUID. They are not additional source totals; they are a convenient declaration-level view of the same 66 values.

| Declarant | Publication date | Declaration UUID | Populated rows | Category sum (€) | Maximum category (€) | Years |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Mme Florence Ribard | 2026-04-14 | `0a10a606-2318-43cf-8fa8-22d392559ff5` | 33 | €419,606 | €52,294 | 7 |
| Mme Charlotte LECOCQ | 2026-03-03 | `3ae51772-5b1b-4d15-afe8-4f018589442e` | 6 | €130,570 | €82,023 | 2 |
| Mme Marie-Pierre VEDRENNE | 2026-04-05 | `59e40cfb-7b2a-481a-9141-a8e25e028f1f` | 2 | €120,000 | €60,000 | 2 |
| Mme Maud BREGEON | 2026-07-27 | `f2b84cea-cbba-4e05-a6a6-cb656fb4a80e` | 4 | €118,385 | €57,645 | 2 |
| Mme Maud BREGEON | 2026-04-30 | `f9e780b3-8763-442c-ba34-50e31f6206e7` | 5 | €101,665 | €57,645 | 2 |
| Mme Rachida Dati | 2026-04-22 | `6dcd326d-e076-4d7a-a428-15075a15dddd` | 6 | €73,005 | €41,571 | 1 |
| Mme Amélie de Montchalin | 2026-03-14 | `3261cb23-f5cd-4d7f-9622-732629e474b2` | 5 | €56,747 | €28,500 | 2 |
| M. David Amiel | 2026-04-19 | `2f2a28b3-7cd9-44ab-a086-ea80c0bde58e` | 3 | €42,602 | €23,997 | 2 |
| Mme Marie-Pierre VEDRENNE | 2026-04-26 | `b0e3b825-7c6e-4d84-b858-6e5a029ab1a8` | 2 | €35,951 | €18,096 | 2 |

## Source-to-parser reconciliation

| Check | Result |
| --- | ---: |
| Source category slots | 198 |
| Source numeric elected-person category values | 66 |
| Normalized `incomes` rows with numeric `normalized_value` (`revenu_mandat`) | 66 |
| Difference between source numeric values and normalized rows | 0 |
| Sum of source numeric category values (€) | €1,098,531 |
| Sum of source `totalElu` values (€) | €1,098,531 |
| Aggregate reconciliation difference (€) | €0 |

The manual review bundle contains one raw declaration and its parsed output: [`reports/manual-review/2026-08-17/6dcd326d-e076-4d7a-a428-15075a15dddd/README.md`](manual-review/2026-08-17/6dcd326d-e076-4d7a-a428-15075a15dddd/README.md). It is the Rachida Dati example described above.

## Method and limitations

- The source was read from the immutable XML snapshot identified by the SHA-256 above. The normalized tables were produced with the parser at revision `1000d0b`.
- Category outliers use the median and median absolute deviation (MAD) over numeric elected-person category values. The robust scale is `1.4826 × MAD`; a row is formally flagged only when its absolute robust z-score is greater than 10, matching `src/hatvp/quality.py`.
- `totalElu` is an aggregate consistency field. When at least one category is populated, the parser emits category rows and uses the source total only for reconciliation; emitting both would inflate income counts and sums.
- This report does not assert that a high value is wrong. A high value may reflect legitimate salary, pension, elected-official compensation, or multiple years of reporting. Candidate rows should be checked against the source declaration when needed.
- The source has label variants (`Traitements salaires` versus `Traitements, salaires`, for example). The parser preserves the exact source label; a canonical category mapping would be a separate analytical normalization step.

## Recommended follow-up

1. Keep the current category-level parser behavior and monitor the source-to-normalized count and sum reconciliation on each snapshot.
2. If product analytics needs category rollups, add a tested canonical mapping for label variants without overwriting the raw `income_type`.
3. Use the candidate register above for manual source checks, starting with Charlotte LECOCQ's €82,023 entry and the repeated €60,000/€57,645 entries.

## Source artifacts

- Raw XML snapshot: `gs://yahatvp-pipeline-eu-data/hatvp/raw/snapshot_date=2026-08-17/declarations.xml`
- Unified normalized incomes: `gs://yahatvp-pipeline-eu-data/hatvp/silver/incomes/snapshot_date=2026-08-17/data.parquet` (filter `income_stream=revenu_mandat` for this report)
- Normalized declarations: `gs://yahatvp-pipeline-eu-data/hatvp/silver/declarations/snapshot_date=2026-08-17/data.parquet`
- Pipeline quality report: `gs://yahatvp-pipeline-eu-data/hatvp/quality/snapshot_date=2026-08-17/report.json`
