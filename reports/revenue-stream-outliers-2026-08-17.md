# Revenue-stream outliers in the 2026-08-17 HATVP snapshot

> Technical statistical review of the two revenue-like streams requested for manual inspection: `revenuMandatDto` income categories and annual `mandatElectifDto` remuneration values.

## Technical summary

The two streams behave very differently. `revenuMandatDto` is sparse but internally reconciled: the snapshot contains 66 populated numeric category values across 9 declarations, and none crosses the configured robust outlier threshold. The raw annual elected-mandate output contains 55 outliers, but one was superseded by a later declaration that corrects the value. The effective review population therefore contains **54 of 74,709 annual rows (0.0723%) across 31 declarations** as formal outliers.

The original **€5.92M** Stephanie Rist row is removed from the effective outlier register after checking the latest declaration version: the same 2025 value is **€62,730** in declaration `d9b0bda2-d97b-4983-bf09-ea61c759b7b3`. The remaining 54 flagged rows represent **€27.11M**, or 2.19% of the effective annual-remuneration total. Repeated exact values across different declarations—especially 27 `Union Cycliste Internationale` rows across 6 declarations—still suggest source duplication, legacy imports, or a unit/period issue are plausible explanations, but this report does not establish which explanation is correct.

The parser fix is therefore doing the right structural thing: it preserves every annual remuneration value instead of collapsing a multi-year series to one scalar. The superseded source rows remain in the immutable normalized snapshot for auditability; only the report's effective review population excludes the old declaration. The follow-up needed is source review of the remaining 54 flagged annual rows, not deletion or silent normalization.

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
| Normalized `incomes` rows | 66 |
| Source `totalElu` aggregates | 22 |
| Sum of category values | €1,098,531 |
| Sum of `totalElu` values | €1,098,531 |
| Reconciliation difference | €0 |

The robust distribution has a median of **€9,000**, a MAD of **€8,218.50**, and a maximum of **€82,023**. The largest review candidate is Charlotte LECOCQ's `Traitements salaires` value for 2025; its robust z-score is 5.99, below the formal threshold of 10. The full category breakdown and manual Rachida Dati bundle remain in [`statistical-income-outliers-2026-08-17.md`](statistical-income-outliers-2026-08-17.md).

## Key findings: the effective annual-remuneration register contains 54 formal outliers

The raw `mandatElectifDto` remuneration output contains **74,725 numeric rows** across **5,850 declarations**, covering remuneration years **2010–2026**. After excluding the superseded Stephanie Rist declaration from the report-level effective view, the statistics below use **74,709 rows across 5,849 declarations**. All raw rows have a source value and a numeric normalized value. The distribution is highly right-skewed:

| Metric | Annual elected-mandate remuneration |
| --- | ---: |
| Raw normalized snapshot rows | 74,725 |
| Effective report rows | 74,709 |
| Declarations represented in effective view | 5,849 |
| Remuneration years | 2010–2026 |
| `Net` rows in effective view | 72,677 |
| `Brut` rows | 2,032 |
| Zero-valued rows | 12,176 (16.29%) |
| Minimum | €0 |
| 25th percentile | €2,367 |
| Median | €10,881 |
| 75th percentile | €22,911 |
| 95th percentile | €61,808 |
| 99th percentile | €80,172 |
| Maximum | €4,523,968 |
| Formal robust outliers | 54 rows / 31 declarations |
| Formal outlier share | 0.0723% of effective rows |
| Formal outlier value total | €27,108,954 (2.19% of effective values) |

The 54 effective outliers occur from 2016 through 2024. The largest concentration is the 27 rows whose source description is `Union Cycliste Internationale`; these are spread over 6 declaration UUIDs and include repeated annual values. The next notable pattern is the cluster of exact repeated values across declarations, which should be checked against the raw XML rather than deduplicated in the normalized table.

| Source description pattern | Outlier rows | Declarations | Maximum |
| --- | ---: | ---: | ---: |
| `Union Cycliste Internationale` | 27 | 6 | €495,220 |
| `Maire` | 3 | 3 | €262,488 |
| `Députée` | 3 | 3 | €160,102 |
| `Conseiller Régional` | 3 | 1 | €2,633,305 |
| `Conseillère départementale` | 2 | 2 | €1,853,886 |
| `Vice-présidente` | 2 | 2 | €368,593 |
| Other source-label variants | 14 | 14 | €4,523,968 |

## Supersession check: Stephanie Rist's €5.92M row is removed from the effective register

The raw XML contains both declarations. The later modificative declaration was posted on **21 February 2026** and replaces the 2025 `députée` amount with a normal-scale value. This is a confirmed source correction for this report, not an inferred statistical exclusion.

| Declaration | Posted | 2025 `députée` value | Report treatment |
| --- | --- | ---: | --- |
| `27c770d6-0e1f-4f7f-bb21-d4c0e003e935` | 25 October 2025 | €5,919,820 | Excluded from effective view as superseded |
| `d9b0bda2-d97b-4983-bf09-ea61c759b7b3` | 21 February 2026 | €62,730 | Retained as latest version |

The latest declaration's `députée` series is **€84,737 (2022), €81,340 (2023), €88,667 (2024), and €62,730 (2025)**. The old declaration's 16 normalized annual rows remain in the raw/silver snapshot; no source data was deleted or rewritten. Only the report-level effective outlier calculation excludes the old UUID.

## Highest-value annual remuneration candidates

These rows are formal outliers under the robust detector. They are review candidates, not confirmed errors. The names and role descriptions below are copied from the normalized source-linked tables; the declaration UUID is the stable key for manual XML lookup.

| # | Declarant | Year | Source description | Value | Robust z | Declaration UUID |
| ---: | --- | ---: | --- | ---: | ---: | --- |
| 1 | M. Pieyre-Alexandre ANGLADE | 2022 | `député` | €4,523,968 | 316.07 | `2b57f4a8-b251-48f7-aba8-56f8407509d1` |
| 2 | M. Jean-Luc WARSMANN | 2023 | `Conseiller Régional` | €2,633,305 | 183.66 | `5ef9ca8a-7101-407b-aa8d-8507aa415a52` |
| 3 | M. Jean-Luc WARSMANN | 2022 | `Conseiller Régional` | €2,575,188 | 179.59 | `5ef9ca8a-7101-407b-aa8d-8507aa415a52` |
| 4 | Mme Brigitte MANZANARES | 2021 | `Conseillère départementale` | €1,853,886 | 129.07 | `c5103c3a-42c3-4072-a65e-4bb5a1e2c1e5` |
| 5 | M. Jean-Luc WARSMANN | 2024 | `Conseiller Régional` | €1,114,495 | 77.29 | `5ef9ca8a-7101-407b-aa8d-8507aa415a52` |
| 6 | M. OLIVIER SERVA | 2019 | `DEPUTE` | €707,733 | 48.80 | `ccbbe015-e353-44d2-abd9-065489122c13` |
| 7 | M. David LAPPARTIENT | 2022 | `Union Cycliste Internationale` | €495,220 | 33.92 | `de4125e1-dcda-40bc-aa3d-88f43887ed69` |
| 8 | M. David LAPPARTIENT | 2022 | `Union Cycliste Internationale` | €495,220 | 33.92 | `1649fd3b-2b26-429f-a675-b3a18db3c045` |
| 9 | M. David LAPPARTIENT | 2022 | `Union Cycliste Internationale` | €495,220 | 33.92 | `1b1569d3-7089-413c-817f-01dab6fc7d7e` |
| 10 | Mme Cécile BARREAU | 2021 | `Conseillère départementale` | €466,728 | 31.92 | `61790b16-cfc4-44b3-8491-7480819c1336` |
| 11 | Mme Isabelle BEARUNE | 2019 | `Elue Province des Iles Loyauté` | €449,444 | 30.71 | `d0b3a081-da34-4305-9869-710bb355ab36` |
| 12 | Mme Isabelle BEARUNE | 2019 | `Elue Province des Iles Loyauté` | €449,444 | 30.71 | `b4e75411-9418-41e4-b5d8-398016f29071` |
| 13 | M. David LAPPARTIENT | 2023 | `Union Cycliste Internationale` | €416,000 | 28.37 | `de4125e1-dcda-40bc-aa3d-88f43887ed69` |
| 14 | M. David LAPPARTIENT | 2023 | `Union Cycliste Internationale` | €416,000 | 28.37 | `1649fd3b-2b26-429f-a675-b3a18db3c045` |
| 15 | M. David LAPPARTIENT | 2023 | `Union Cycliste Internationale` | €416,000 | 28.37 | `1b1569d3-7089-413c-817f-01dab6fc7d7e` |

The repeated-value pattern is material: `€495,220` appears in three declarations for 2022, `€416,000` appears in three declarations for 2023, `€302,928` appears in three declarations for 2021, and `€224,770` appears in six declarations for 2019. These are not duplicates created by the parser: the rows retain different source declaration UUIDs and source item positions.

## Scope and metric definitions

The analysis uses the successful 2026-08-17 GCS snapshot generated by the deployed parser. It treats each numeric normalized value as one observation at its source grain:

- `revenuMandatDto`: one row per populated elected-person income category and year. Empty XML category slots are not observations; `totalElu` is used for reconciliation and is not emitted as a duplicate row when categories are populated.
- `mandatElectifDto`: one row per annual remuneration value nested inside an elected-mandate item. A multi-year source item therefore contributes several rows, preserving its year/value series.
- A value is a **formal outlier** when its absolute robust z-score is greater than 10. A **review candidate** is any high or patterned value selected for inspection even when it does not cross that threshold.
- Currency values are shown in euros as stored after French-number normalization. The source basis (`Net` or `Brut`) is retained and is not mixed into a common net/gross interpretation.

## Methodology and validation

For each stream, the detector computes the median and median absolute deviation (MAD) over numeric normalized values. The robust scale is `1.4826 × MAD`, and the score is:

```text
robust_z = (value - median) / (1.4826 × MAD)
```

The effective annual-remuneration statistics are median **€10,881**, MAD **€9,631**, and robust scale **€14,278.92**. The `revenuMandatDto` statistics are median **€9,000**, MAD **€8,218.50**, and robust scale **€12,184.75**. No negative values or values above €10M were found in either stream.

Validation checks passed for the snapshot:

- `mandatElectifDto` annual rows with source values: 74,725; rows with numeric normalized values: 74,725. The effective report view excludes the 16 rows belonging to superseded declaration `27c770d6-0e1f-4f7f-bb21-d4c0e003e935`.
- `revenuMandatDto` rows with source values: 66; rows with numeric normalized values: 66.
- `revenuMandatDto` category sum equals source `totalElu` sum: €1,098,531 versus €1,098,531.
- Raw XML verification confirms the superseded 2025 value `5 919 820` and the latest 2025 value `62 730` for the two declaration UUIDs.
- The deployed quality report records zero quality errors for the snapshot. Its warning-bearing status is attributable to the broader source review population, not a failed transformation.

Exact distribution charts are intentionally omitted here: the annual stream is so right-skewed that a chart would compress the normal range and obscure the auditable candidate rows. The percentile table, robust statistics, source-label grouping, and UUID-level candidate register are more useful for manual review.

## Limitations, uncertainty, and robustness checks

- A robust outlier is a statistical review signal, not proof of an incorrect declaration. A high amount can be legitimate, can combine multiple periods, or can reflect a different reporting basis.
- The detector is global across positions, years, and `Net`/`Brut` values. A role-specific or basis-specific model could change the candidate set; this report does not claim a role-adjusted threshold.
- Source descriptions are free text and can vary by capitalization, spelling, and declaration. The table preserves the exact source labels and does not merge them into a new taxonomy.
- The effective report view applies one explicit, source-verified supersession rule: Stephanie Rist's 25 October 2025 declaration is replaced by her 21 February 2026 modificative declaration for this report. The pipeline's raw and normalized tables retain both versions.
- Some top-level declaration role fields do not match the nested source description exactly. For example, Jean-Luc WARSMANN's nested `Conseiller Régional` rows sit in a declaration whose top-level mandate type is `Député`. Manual review should inspect the nested XML item, not infer a correction from one field alone.
- Repeated values across declaration UUIDs are retained because UUIDs and source positions differ. Cross-declaration repetition is a review signal, not permission to deduplicate.
- `revenuMandatDto` coverage remains optional and sparse: 46 of its 55 present sections have no populated category rows. This is expected source sparsity unless a separate schema contract says otherwise.

## Recommended next steps

1. Keep Stephanie Rist's superseded UUID out of the effective register while retaining both UUIDs and raw values for audit traceability.
2. Manually inspect the 15 highest-value remaining annual-remuneration rows above in the raw XML, starting with the five values above €1M.
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
| Snapshot pipeline revision | `94d04a4bd0c744dcc61dc43a2fa0b78444e91ec5` |
| Successful force-run | `hatvp-ingestion-4479p` |
| Effective supersession adjustment | Exclude `27c770d6-0e1f-4f7f-bb21-d4c0e003e935`; retain `d9b0bda2-d97b-4983-bf09-ea61c759b7b3` |
| Annual remuneration artifact | `gs://yahatvp-pipeline-eu-data/hatvp/silver/mandate_remunerations/snapshot_date=2026-08-17/data.parquet` |
| Income artifact | `gs://yahatvp-pipeline-eu-data/hatvp/silver/incomes/snapshot_date=2026-08-17/data.parquet` |
| Declaration and person joins | `silver/declarations` and `silver/people` for the same snapshot |
| Quality artifact | `gs://yahatvp-pipeline-eu-data/hatvp/quality/snapshot_date=2026-08-17/report.json` |
