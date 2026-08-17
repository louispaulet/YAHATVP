# Revenue-stream outliers in the 2026-08-17 HATVP snapshot

> Technical statistical review of the two revenue-like streams requested for manual inspection: `revenuMandatDto` income categories and annual `mandatElectifDto` remuneration values.

## Technical summary

The two streams behave very differently. `revenuMandatDto` is sparse but internally reconciled: the snapshot contains 66 populated numeric category values across 9 declarations, and none crosses the configured robust outlier threshold. The unified `incomes` table therefore contains **74,791 numeric rows**: those 66 category rows plus **74,725** annual elected-mandate remuneration rows. The raw annual elected-mandate output contains 55 outlier rows, but 13 of those rows belong to 11 declarations later corrected by modificative reports. The effective review population therefore contains **42 of 74,594 annual rows (0.0563%) across 21 declarations** as formal outliers.

Stephanie Rist's **€5.92M** row is the clearest example: her latest declaration changes the 2025 value to **€62,730**. The other corrected pairs include Pieyre-Alexandre Anglade, Jean-Luc Warsmann, Brigitte Manzanares, Cécile Barreau, Valérie Dauge, Patricia Bremond, Valérie Guarino, Laurence Porte, and Christèle Willer. The remaining 42 flagged rows represent **€12.18M**, or 1.00% of the effective annual-remuneration total. Repeated exact values across different declarations—especially 27 `Union Cycliste Internationale` rows across 6 declarations—still suggest source duplication, legacy imports, or a unit/period issue are plausible explanations, but this report does not establish which explanation is correct.

The parser fix is therefore doing the right structural thing: it preserves every annual remuneration value instead of collapsing a multi-year series to one scalar. The superseded source rows remain in the immutable normalized snapshot for auditability; only the report's effective review population excludes the 11 corrected declarations. The follow-up needed is source review of the remaining 42 flagged annual rows, not deletion or silent normalization.

## Key findings: the sparse income stream is reconciled, not silently dropped

`revenuMandatDto` has **55 declarations with the section present**, but only **9 declarations with at least one populated income group**. The normalized output contains exactly the 66 numeric elected-person category values present in the source groups.

| Check | Result |
| --- | ---: |
| Declarations in snapshot | 6,611 |
| Declarations with `revenuMandatDto` | 55 |
| Declarations with at least one populated income group | 9 |
| Source income groups | 22 |
| Fixed category slots | 198 |
| Numeric elected-person category values | 66 |
| Normalized `incomes` rows (`revenu_mandat` stream) | 66 |
| Unified normalized `incomes` rows | 74,791 |
| Source `totalElu` aggregates | 22 |
| Sum of category values | €1,098,531 |
| Sum of `totalElu` values | €1,098,531 |
| Reconciliation difference | €0 |

The robust distribution has a median of **€9,000**, a MAD of **€8,218.50**, and a maximum of **€82,023**. The largest review candidate is Charlotte LECOCQ's `Traitements salaires` value for 2025; its robust z-score is 5.99, below the formal threshold of 10. The full category breakdown and manual Rachida Dati bundle remain in [`statistical-income-outliers-2026-08-17.md`](statistical-income-outliers-2026-08-17.md).

## Key findings: the effective annual-remuneration register contains 42 formal outliers

The raw `mandatElectifDto` remuneration output contains **74,725 numeric rows** across **5,850 declarations**, covering remuneration years **2010–2026**. After excluding 11 declarations whose later modificative reports replace their outlier values, the statistics below use **74,594 rows across 5,839 declarations**. All raw rows have a source value and a numeric normalized value. The distribution is highly right-skewed:

| Metric | Annual elected-mandate remuneration |
| --- | ---: |
| Raw normalized snapshot rows | 74,725 |
| Effective report rows | 74,594 |
| Declarations represented in effective view | 5,839 |
| Remuneration years | 2010–2026 |
| `Net` rows in effective view | 72,570 |
| `Brut` rows | 2,024 |
| Zero-valued rows | 12,175 (16.32%) |
| Minimum | €0 |
| 25th percentile | €2,365 |
| Median | €10,865 |
| 75th percentile | €22,888 |
| 95th percentile | €61,749 |
| 99th percentile | €79,430 |
| Maximum | €707,733 |
| Formal robust outliers | 42 rows / 21 declarations |
| Formal outlier share | 0.0563% of effective rows |
| Formal outlier value total | €12,177,799 (1.00% of effective values) |

The 42 effective outliers occur from 2016 through 2023. The largest concentration is the 27 rows whose source description is `Union Cycliste Internationale`; these are spread over 6 declaration UUIDs and include repeated annual values. The next notable pattern is the cluster of exact repeated values across declarations, which should be checked against the raw XML rather than deduplicated in the normalized table.

| Source description pattern | Outlier rows | Declarations | Maximum |
| --- | ---: | ---: | ---: |
| `Union Cycliste Internationale` | 27 | 6 | €495,220 |
| `Députée` | 3 | 3 | €160,102 |
| `Maire` | 2 | 2 | €262,488 |
| `conseiller Départemental` | 2 | 2 | €207,110 |
| `Conseillère Régionale` | 2 | 2 | €277,224 |
| `Conseillère Régionale des Hauts-de-France` | 2 | 2 | €341,441 |
| `Elue Province des Iles Loyauté` | 2 | 2 | €449,444 |
| `DEPUTE` | 1 | 1 | €707,733 |
| `maire` | 1 | 1 | €219,862 |

## Source-version check: 13 corrected rows removed; unchanged later values retained

I checked every raw annual-remuneration outlier against later declarations for the same person, declaration context, remuneration year, and source description. Raw XML verification confirmed 11 older declaration UUIDs whose later modificative reports replace 13 outlier rows with lower values. These are source-verified supersessions for this report, not inferred statistical exclusions.

| Declarant | Older declaration UUID(s) | Later declaration UUID | Corrected annual value(s) |
| --- | --- | --- | ---: |
| Stephanie Rist | `27c770d6-0e1f-4f7f-bb21-d4c0e003e935` | `d9b0bda2-d97b-4983-bf09-ea61c759b7b3` | 2025: €5,919,820 → €62,730 |
| Pieyre-Alexandre Anglade | `2b57f4a8-b251-48f7-aba8-56f8407509d1` | `cef858f7-04e8-4c37-bf71-7431e8689de8` | 2022: €4,523,968 → €41,517 |
| Jean-Luc Warsmann | `5ef9ca8a-7101-407b-aa8d-8507aa415a52` | `d1bb952f-ad78-4d04-b498-915e0995a38a` | 2022–2024: €2,575,188 / €2,633,305 / €1,114,495 → €25,751 / €26,333 / €11,144 |
| Brigitte Manzanares | `c5103c3a-42c3-4072-a65e-4bb5a1e2c1e5` | `6df418e1-41bf-4058-8b67-edcc96883e79` | 2021: €1,853,886 → €18,538 |
| Cécile Barreau | `61790b16-cfc4-44b3-8491-7480819c1336` | `ad25fb18-5646-4899-af53-047ccb9a6a08` | 2021: €466,728 → €4,667 |
| Valérie Dauge | `34ae39cf-6c7c-4e3c-bbc5-19ad624c4d0f`; `a92b7a3b-85db-4413-b5d3-8d602e40ba2b` | `740eb8df-7134-4049-b176-b067d2a3dcdb` | 2021: €368,593 → €21,610 |
| Patricia Bremond | `5ba8ff83-10cd-4529-9737-1e8a80735de4` | `22f9a2d3-3a75-4e8a-9596-ec0c2122c41e` | 2021: €335,760 → €5,082 |
| Valérie Guarino | `5780abd5-3647-48a6-9a86-3417df1d4238` | `0cc7df46-359e-4d36-87f5-267f83703488` | 2018: €298,012 → €29,012 |
| Laurence Porte | `a161eef1-eb77-4779-99d5-3eade1e2541b` | `e1efec96-dd69-496a-9083-e69fe1c4b114` | 2017: €219,862 → €21,862 |
| Christèle Willer | `047a0380-18c7-4c36-9ad0-8343efa902a6` | `e43e40b3-c214-4436-894a-f3bdb9b8765d` | 2020: €172,765 → €17,276 |

The 11 older declarations contribute 131 normalized annual rows, all of which remain in the raw and silver artifacts for auditability. The report-level effective calculation excludes only those 11 older UUIDs and retains the later versions. The Barreau latest declaration also contains a spelling-variant source description with a non-outlier value; that variant was preserved and was not merged into the exact-label replacement. The other 12 older outlier declarations with later same-context matches retain the same high value in the later version, so they remain flagged rather than being removed.

## Highest-value annual remuneration candidates

These rows are formal outliers under the robust detector after the source-version reconciliation above. They are review candidates, not confirmed errors. The names and role descriptions below are copied from the normalized source-linked tables; the declaration UUID is the stable key for manual XML lookup.

| # | Declarant | Year | Source description | Value | Robust z | Declaration UUID |
| ---: | --- | ---: | --- | ---: | ---: | --- |
| 1 | M. OLIVIER SERVA | 2019 | `DEPUTE` | €707,733 | 48.84 | `ccbbe015-e353-44d2-abd9-065489122c13` |
| 2 | M. David LAPPARTIENT | 2022 | `Union Cycliste Internationale` | €495,220 | 33.95 | `de4125e1-dcda-40bc-aa3d-88f43887ed69` |
| 3 | M. David LAPPARTIENT | 2022 | `Union Cycliste Internationale` | €495,220 | 33.95 | `1649fd3b-2b26-429f-a675-b3a18db3c045` |
| 4 | M. David LAPPARTIENT | 2022 | `Union Cycliste Internationale` | €495,220 | 33.95 | `1b1569d3-7089-413c-817f-01dab6fc7d7e` |
| 5 | Mme Isabelle BEARUNE | 2019 | `Elue Province des Iles Loyauté` | €449,444 | 30.74 | `d0b3a081-da34-4305-9869-710bb355ab36` |
| 6 | Mme Isabelle BEARUNE | 2019 | `Elue Province des Iles Loyauté` | €449,444 | 30.74 | `b4e75411-9418-41e4-b5d8-398016f29071` |
| 7 | M. David LAPPARTIENT | 2023 | `Union Cycliste Internationale` | €416,000 | 28.39 | `de4125e1-dcda-40bc-aa3d-88f43887ed69` |
| 8 | M. David LAPPARTIENT | 2023 | `Union Cycliste Internationale` | €416,000 | 28.39 | `1649fd3b-2b26-429f-a675-b3a18db3c045` |
| 9 | M. David LAPPARTIENT | 2023 | `Union Cycliste Internationale` | €416,000 | 28.39 | `1b1569d3-7089-413c-817f-01dab6fc7d7e` |
| 10 | Mme Faustine MALIAR | 2019 | `Conseillère Régionale des Hauts-de-France` | €341,441 | 23.17 | `84725c82-db89-4dd1-92af-5efffdf76b3e` |
| 11 | Mme Faustine MALIAR | 2019 | `Conseillère Régionale des Hauts-de-France` | €341,441 | 23.17 | `31e1bba4-d39b-463f-b310-6db2cc20d239` |
| 12 | M. David LAPPARTIENT | 2021 | `Union Cycliste Internationale` | €302,928 | 20.47 | `de4125e1-dcda-40bc-aa3d-88f43887ed69` |
| 13 | M. David LAPPARTIENT | 2021 | `Union Cycliste Internationale` | €302,928 | 20.47 | `1649fd3b-2b26-429f-a675-b3a18db3c045` |
| 14 | M. David LAPPARTIENT | 2021 | `Union Cycliste Internationale` | €302,928 | 20.47 | `1b1569d3-7089-413c-817f-01dab6fc7d7e` |
| 15 | Mme eliane JARYCKI | 2016 | `Conseillère Régionale` | €277,224 | 18.67 | `10f24658-bdb9-490f-8882-83ce757aaaee` |

The repeated-value pattern is material: `€495,220` appears in three declarations for 2022, `€416,000` appears in three declarations for 2023, `€302,928` appears in three declarations for 2021, and `€224,770` appears in six declarations for 2019. These are not duplicates created by the parser: the rows retain different source declaration UUIDs and source item positions.

## Scope and metric definitions

The analysis uses the successful 2026-08-17 GCS snapshot generated by the deployed parser. It treats each numeric normalized value as one observation at its source grain:

- `revenuMandatDto`: one row per populated elected-person income category and year. Empty XML category slots are not observations; `totalElu` is used for reconciliation and is not emitted as a duplicate row when categories are populated.
- `mandatElectifDto`: one row per annual remuneration value nested inside an elected-mandate item. A multi-year source item therefore contributes several rows, preserving its year/value series.
- The curated `incomes` table contains both streams and tags them with `income_stream`; the detailed `mandate_remunerations` table remains the remuneration-specific source view.
- A value is a **formal outlier** when its absolute robust z-score is greater than 10. A **review candidate** is any high or patterned value selected for inspection even when it does not cross that threshold.
- Currency values are shown in euros as stored after French-number normalization. The source basis (`Net` or `Brut`) is retained and is not mixed into a common net/gross interpretation.

## Methodology and validation

For each stream, the detector computes the median and median absolute deviation (MAD) over numeric normalized values. The robust scale is `1.4826 × MAD`, and the score is:

```text
robust_z = (value - median) / (1.4826 × MAD)
```

The effective annual-remuneration statistics are median **€10,865**, MAD **€9,624**, and robust scale **€14,268.54**. The `revenuMandatDto` statistics are median **€9,000**, MAD **€8,218.50**, and robust scale **€12,184.75**. No negative values or values above €10M were found in either stream.

Validation checks passed for the snapshot:

- `mandatElectifDto` annual rows with source values: 74,725; rows with numeric normalized values: 74,725. The effective report view excludes 131 rows belonging to 11 source-verified superseded declaration UUIDs and retains the later versions.
- `revenuMandatDto` rows with source values: 66; rows with numeric normalized values: 66.
- Unified `incomes` rows with numeric normalized values: 74,791 (`mandate_remuneration=74,725`, `revenu_mandat=66`).
- `revenuMandatDto` category sum equals source `totalElu` sum: €1,098,531 versus €1,098,531.
- Raw XML verification confirms all 11 older/later declaration pairs in the supersession table, including Stephanie Rist's `5 919 820` → `62 730` replacement.
- The deployed quality report records zero quality errors for the snapshot. Its warning-bearing status is attributable to the broader source review population, not a failed transformation.

Exact distribution charts are intentionally omitted here: the annual stream is so right-skewed that a chart would compress the normal range and obscure the auditable candidate rows. The percentile table, robust statistics, source-label grouping, and UUID-level candidate register are more useful for manual review.

## Limitations, uncertainty, and robustness checks

- A robust outlier is a statistical review signal, not proof of an incorrect declaration. A high amount can be legitimate, can combine multiple periods, or can reflect a different reporting basis.
- The detector is global across positions, years, and `Net`/`Brut` values. A role-specific or basis-specific model could change the candidate set; this report does not claim a role-adjusted threshold.
- Source descriptions are free text and can vary by capitalization, spelling, and declaration. The table preserves the exact source labels and does not merge them into a new taxonomy.
- The effective report view applies 11 explicit, source-verified supersession rules covering 13 corrected outlier rows. The pipeline's raw and normalized tables retain all 11 older declarations and their later versions.
- Some top-level declaration role fields do not match the nested source description exactly. For example, Jean-Luc WARSMANN's nested `Conseiller Régional` rows sit in a declaration whose top-level mandate type is `Député`. Manual review should inspect the nested XML item, not infer a correction from one field alone.
- Repeated values across declaration UUIDs are retained because UUIDs and source positions differ. Cross-declaration repetition is a review signal, not permission to deduplicate.
- `revenuMandatDto` coverage remains optional and sparse: 46 of its 55 present sections have no populated category rows. This is expected source sparsity unless a separate schema contract says otherwise.

## Recommended next steps

1. Keep the 11 superseded declaration UUIDs out of the effective register while retaining every UUID and raw value for audit traceability.
2. Manually inspect the 15 highest-value remaining annual-remuneration rows above in the raw XML, starting with Olivier Serva and the repeated David Lappartient values.
3. Review the repeated `Union Cycliste Internationale` and repeated-value clusters across declaration UUIDs for source duplication, period duplication, or unit issues.
4. Monitor the two reconciliation counts and the effective annual-remuneration outlier count after each snapshot. A sudden change in the outlier count or in the repeated-value clusters should trigger a source review.

## Further questions

- Should a future detector compare values within a normalized mandate category and remuneration basis (`Net` versus `Brut`) rather than across the full annual stream?
- Are the high repeated values present verbatim in the corresponding HATVP XML declarations, or are they introduced by an upstream export/import process?
- Should the product expose a separate review status for confirmed source anomalies, distinct from statistical outlier flags?

## Reproducibility record

| Item | Value |
| --- | --- |
| Snapshot date | `2026-08-17` |
| Raw XML SHA-256 | `865261857f88ec6c262558bc115b37b94f97ea3418b6829267aa6cbd1458fdaf` |
| Snapshot pipeline revision | `1000d0b03a6fdcebef75b467fca1cf7a95860d84` |
| Successful force-runs | `hatvp-ingestion-f6mdg`, `hatvp-ingestion-ts6jb` |
| Effective supersession adjustment | Exclude 11 corrected declaration UUIDs (131 annual rows; 13 corrected outlier rows); retain 12 unchanged later-version patterns |
| Annual remuneration artifact | `gs://yahatvp-pipeline-eu-data/hatvp/silver/mandate_remunerations/snapshot_date=2026-08-17/data.parquet` |
| Income artifact | `gs://yahatvp-pipeline-eu-data/hatvp/silver/incomes/snapshot_date=2026-08-17/data.parquet` |
| Declaration and person joins | `silver/declarations` and `silver/people` for the same snapshot |
| Quality artifact | `gs://yahatvp-pipeline-eu-data/hatvp/quality/snapshot_date=2026-08-17/report.json` |
