# Statistical asset outliers

> Technical review report for fact-checking flagged HATVP asset records.

| Field | Value |
| --- | ---: |
| Snapshot date | `2026-08-17` |
| Detector | Robust median/MAD asset outlier check |
| Review threshold | Absolute robust z-score > 10 |
| Flagged asset rows | 143 |
| Distinct declarations | 69 |
| Matched declarant names | 143 / 143 |
| Matched publication dates | 143 / 143 |

## Executive summary

The pipeline flagged **143 asset rows** as statistical outliers among **1,156 numeric asset rows** (12.4%). All 143 are high-side outliers: the smallest flagged value is €192 252 and the largest is €6 719 662.

The flagged rows sum to **€99 617 179**, compared with €124 440 950 across all numeric asset values. This is 80.1% of numeric row-value total; it is **not** a share of household wealth because rows may represent partial interests, overlapping declarations, or different valuation concepts.

Every flagged row was joined to the normalized `people` and `declarations` tables using `declaration_uuid`, so the register below includes the declarant and publication date for fact-checking.

## Key metrics

| Metric | Result |
| --- | ---: |
| Total asset rows | 1,376 |
| Numeric asset rows | 1,156 |
| Median asset value | €12 000 |
| Median absolute deviation (MAD) | €11 878 |
| Robust scale (1.4826 × MAD) | €17 610 |
| High-side cutoff | €188 103 |
| Low-side cutoff | €-164 103 |
| Minimum flagged value | €192 252 |
| Median flagged value | €410 000 |
| Maximum flagged value | €6 719 662 |
| Missing asset names | 5 |

## Outliers by asset section

| Asset section | Flagged rows | Share of outliers | Flagged value sum |
| --- | ---: | ---: | ---: |
| Real estate | 86 | 60.1% | €57 222 895 |
| Life insurance | 30 | 21.0% | €16 934 782 |
| Other assets | 9 | 6.3% | €2 969 706 |
| Bank accounts | 4 | 2.8% | €1 076 068 |
| SCI / property company | 4 | 2.8% | €1 649 802 |
| Unlisted securities | 4 | 2.8% | €14 379 268 |
| Foreign assets | 3 | 2.1% | €1 790 363 |
| Listed securities | 3 | 2.1% | €3 594 295 |

Real estate dominates the count and value of the flags. The detector is distribution-based, so a plausible high-value property can be flagged simply because it is far from the snapshot median; a flag is a review signal, not an accusation or an automatic data error.

## Outliers by value band

| Value band | Flagged rows | Flagged value sum |
| --- | ---: | ---: |
| €188k–€250k | 29 | €6 280 554 |
| €250k–€500k | 52 | €18 337 276 |
| €500k–€1m | 37 | €25 802 776 |
| €1m–€2m | 18 | €23 485 226 |
| €2m–€5m | 5 | €12 272 023 |
| >€5m | 2 | €13 439 324 |

## Highest-value declarations

Grouped by declarant, normalized publication date, and declaration UUID. These are useful starting points for source-level fact checks.

| Declarant | Publication date | Declaration UUID | Flagged rows | Flagged value sum | Maximum flagged value |
| --- | --- | --- | ---: | ---: | ---: |
| M. Serge Papin | 2025-12-05 | `bd19a0d5-eb22-4649-bb6b-e8d77ff89118` | 4 | €9 007 307 | €6 719 662 |
| M. Serge Papin | 2026-02-17 | `307a6524-c8a6-4e5c-92b0-731029d15b19` | 4 | €8 382 307 | €6 719 662 |
| Mme Rachida Dati | 2026-04-22 | `6dcd326d-e076-4d7a-a428-15075a15dddd` | 3 | €5 785 673 | €3 133 135 |
| M. Jean-Noel Barrot | 2025-12-05 | `302d9e1f-7835-4269-b775-261e0a04fc8a` | 7 | €4 262 487 | €1 634 267 |
| Mme Monique BARBUT | 2025-11-13 | `b9c1be04-63ac-4f31-a7c2-4f9edcfc52b3` | 5 | €4 202 897 | €2 250 000 |
| Mme Monique BARBUT | 2026-03-22 | `0e8fdc5f-1425-4a4f-9243-8ed3e1f3fb0b` | 5 | €4 153 061 | €2 250 000 |
| M. Jean-Noel Barrot | 2026-02-25 | `c0ed614c-26a5-4531-ad13-f826e37cba6c` | 6 | €4 006 021 | €1 623 013 |
| M. Roland Lescure | 2025-10-19 | `2bd08f0f-8aba-4e87-b2f4-d564a963a79a` | 3 | €3 646 000 | €2 225 000 |
| Mme alice rufo | 2025-10-20 | `6ca782ee-be24-42c2-976c-57d78c8988cc` | 2 | €2 636 000 | €1 700 000 |
| M. jean-pierre farandou | 2026-02-28 | `cee1589c-81bd-4dcc-9431-58dd9d72f2c0` | 3 | €2 381 011 | €1 000 000 |
| M. jean-pierre farandou | 2025-11-13 | `f327ee29-29a8-43a9-ad66-ba2cf59e9c86` | 3 | €2 381 011 | €1 000 000 |
| M. Rémi Bouchez | 2024-01-23 | `6e136e04-b5b7-4087-93c2-ae8dba947e9f` | 2 | €1 982 935 | €1 764 000 |
| M. Rémi Bouchez | 2024-02-28 | `8947c42d-6ed0-4c5c-b2d0-6d34399230ca` | 2 | €1 982 935 | €1 764 000 |
| Mme francine levon-guerin | 2026-01-27 | `9a3fd717-92d6-4dcb-8bcc-877aaa95dec3` | 2 | €1 870 000 | €1 400 000 |
| Mme Aurore Bergé | 2025-12-04 | `52ff5cc4-e4ad-41be-9368-fa09f9885101` | 3 | €1 675 010 | €750 000 |
| M. Fabrice MELLERAY | 2023-10-28 | `00ccc47c-9a67-4b79-a0ed-d3d2cc584d2b` | 1 | €1 600 000 | €1 600 000 |
| Mme Amélie de Montchalin | 2026-03-14 | `3261cb23-f5cd-4d7f-9622-732629e474b2` | 2 | €1 510 000 | €1 160 000 |
| Mme Florence Ribard | 2026-04-14 | `0a10a606-2318-43cf-8fa8-22d392559ff5` | 2 | €1 504 631 | €904 631 |
| Mme Aurore Bergé | 2026-05-13 | `ec589d51-7664-4638-bef7-809b1e318273` | 3 | €1 444 459 | €695 000 |
| Mme Catherine Brouard-Gallet | 2024-05-20 | `324849c0-3a42-4a8f-b470-c27f5fe33cfa` | 2 | €1 348 111 | €1 000 000 |

## Highest-value individual rows

| Declarant | Publication date | Asset section | Asset name | Value | Declaration UUID |
| --- | --- | --- | --- | ---: | --- |
| M. Serge Papin | 2026-02-17 | Unlisted securities | FINAPA | €6 719 662 | `307a6524-c8a6-4e5c-92b0-731029d15b19` |
| M. Serge Papin | 2025-12-05 | Unlisted securities | FINAPA | €6 719 662 | `bd19a0d5-eb22-4649-bb6b-e8d77ff89118` |
| Mme Rachida Dati | 2026-04-22 | Listed securities | CIC Market Solution | €3 133 135 | `6dcd326d-e076-4d7a-a428-15075a15dddd` |
| Mme Rachida Dati | 2026-04-22 | Life insurance | Dati Rachida | €2 413 888 | `6dcd326d-e076-4d7a-a428-15075a15dddd` |
| Mme Monique BARBUT | 2026-03-22 | Real estate | Appartement | €2 250 000 | `0e8fdc5f-1425-4a4f-9243-8ed3e1f3fb0b` |
| Mme Monique BARBUT | 2025-11-13 | Real estate | Appartement | €2 250 000 | `b9c1be04-63ac-4f31-a7c2-4f9edcfc52b3` |
| M. Roland Lescure | 2025-10-19 | Real estate | Appartement | €2 225 000 | `2bd08f0f-8aba-4e87-b2f4-d564a963a79a` |
| M. Rémi Bouchez | 2024-01-23 | Real estate | Appartement | €1 764 000 | `6e136e04-b5b7-4087-93c2-ae8dba947e9f` |
| M. Rémi Bouchez | 2024-02-28 | Real estate | Appartement | €1 764 000 | `8947c42d-6ed0-4c5c-b2d0-6d34399230ca` |
| Mme alice rufo | 2025-10-20 | Real estate | Maison individuelle | €1 700 000 | `6ca782ee-be24-42c2-976c-57d78c8988cc` |
| M. Jean-Noel Barrot | 2025-12-05 | Life insurance | Jean-Noël Barrot | €1 634 267 | `302d9e1f-7835-4269-b775-261e0a04fc8a` |
| M. Jean-Noel Barrot | 2026-02-25 | Life insurance | Jean-Noël Barrot | €1 623 013 | `c0ed614c-26a5-4531-ad13-f826e37cba6c` |
| M. Fabrice MELLERAY | 2023-10-28 | Real estate | Appartement | €1 600 000 | `00ccc47c-9a67-4b79-a0ed-d3d2cc584d2b` |
| Mme francine levon-guerin | 2026-01-27 | Real estate | Appartement | €1 400 000 | `9a3fd717-92d6-4dcb-8bcc-877aaa95dec3` |
| M. Serge Papin | 2025-12-05 | Real estate | Appartement | €1 250 000 | `bd19a0d5-eb22-4649-bb6b-e8d77ff89118` |
| Mme Dominique Dujols | 2022-02-04 | Real estate | Appartement | €1 210 000 | `06572e52-2668-484b-8b44-c3ab52ccc447` |
| M. Philippe Baptiste | 2025-11-04 | Real estate | Appartement | €1 180 000 | `6c96dc98-91e8-4a0a-98c2-1a9111932600` |
| Mme Amélie de Montchalin | 2026-03-14 | Real estate | Maison individuelle | €1 160 000 | `3261cb23-f5cd-4d7f-9622-732629e474b2` |
| Mme Catherine Pégard | 2026-07-03 | Life insurance | PEGARD Catherine | €1 086 077 | `30a4d227-58b7-4272-bb02-7b184261a28f` |
| Mme Catherine Pégard | 2026-02-12 | Life insurance | PEGARD Catherine | €1 086 077 | `bcc2575f-b226-44ae-865f-964fd60f129e` |

## Full outlier register

The publication date is the normalized `declarations.date_depot` value. The raw source deposit timestamp remains available in `date_depot_raw` in the declarations table. `Source item index` identifies the item position within its source XML section.

| # | Declarant | Publication date | Declaration UUID | Asset section | Asset name | Normalized value | Raw source value | Source item index |
| ---: | --- | --- | --- | --- | --- | ---: | --- | ---: |
| 1 | M. Serge Papin | 2026-02-17 | `307a6524-c8a6-4e5c-92b0-731029d15b19` | Unlisted securities | FINAPA | €6 719 662 | `6719662` | 0 |
| 2 | M. Serge Papin | 2025-12-05 | `bd19a0d5-eb22-4649-bb6b-e8d77ff89118` | Unlisted securities | FINAPA | €6 719 662 | `6719662` | 0 |
| 3 | Mme Rachida Dati | 2026-04-22 | `6dcd326d-e076-4d7a-a428-15075a15dddd` | Listed securities | CIC Market Solution | €3 133 135 | `3133135` | 2 |
| 4 | Mme Rachida Dati | 2026-04-22 | `6dcd326d-e076-4d7a-a428-15075a15dddd` | Life insurance | Dati Rachida | €2 413 888 | `2413888` | 0 |
| 5 | Mme Monique BARBUT | 2026-03-22 | `0e8fdc5f-1425-4a4f-9243-8ed3e1f3fb0b` | Real estate | Appartement | €2 250 000 | `2250000` | 0 |
| 6 | Mme Monique BARBUT | 2025-11-13 | `b9c1be04-63ac-4f31-a7c2-4f9edcfc52b3` | Real estate | Appartement | €2 250 000 | `2250000` | 0 |
| 7 | M. Roland Lescure | 2025-10-19 | `2bd08f0f-8aba-4e87-b2f4-d564a963a79a` | Real estate | Appartement | €2 225 000 | `2225000` | 1 |
| 8 | M. Rémi Bouchez | 2024-01-23 | `6e136e04-b5b7-4087-93c2-ae8dba947e9f` | Real estate | Appartement | €1 764 000 | `1764000` | 0 |
| 9 | M. Rémi Bouchez | 2024-02-28 | `8947c42d-6ed0-4c5c-b2d0-6d34399230ca` | Real estate | Appartement | €1 764 000 | `1764000` | 0 |
| 10 | Mme alice rufo | 2025-10-20 | `6ca782ee-be24-42c2-976c-57d78c8988cc` | Real estate | Maison individuelle | €1 700 000 | `1700000` | 1 |
| 11 | M. Jean-Noel Barrot | 2025-12-05 | `302d9e1f-7835-4269-b775-261e0a04fc8a` | Life insurance | Jean-Noël Barrot | €1 634 267 | `1634267` | 1 |
| 12 | M. Jean-Noel Barrot | 2026-02-25 | `c0ed614c-26a5-4531-ad13-f826e37cba6c` | Life insurance | Jean-Noël Barrot | €1 623 013 | `1623013` | 1 |
| 13 | M. Fabrice MELLERAY | 2023-10-28 | `00ccc47c-9a67-4b79-a0ed-d3d2cc584d2b` | Real estate | Appartement | €1 600 000 | `1600000` | 0 |
| 14 | Mme francine levon-guerin | 2026-01-27 | `9a3fd717-92d6-4dcb-8bcc-877aaa95dec3` | Real estate | Appartement | €1 400 000 | `1400000` | 2 |
| 15 | M. Serge Papin | 2025-12-05 | `bd19a0d5-eb22-4649-bb6b-e8d77ff89118` | Real estate | Appartement | €1 250 000 | `1250000` | 0 |
| 16 | Mme Dominique Dujols | 2022-02-04 | `06572e52-2668-484b-8b44-c3ab52ccc447` | Real estate | Appartement | €1 210 000 | `1210000` | 0 |
| 17 | M. Philippe Baptiste | 2025-11-04 | `6c96dc98-91e8-4a0a-98c2-1a9111932600` | Real estate | Appartement | €1 180 000 | `1180000` | 0 |
| 18 | Mme Amélie de Montchalin | 2026-03-14 | `3261cb23-f5cd-4d7f-9622-732629e474b2` | Real estate | Maison individuelle | €1 160 000 | `1160000` | 0 |
| 19 | Mme Catherine Pégard | 2026-07-03 | `30a4d227-58b7-4272-bb02-7b184261a28f` | Life insurance | PEGARD Catherine | €1 086 077 | `1086077` | 0 |
| 20 | Mme Catherine Pégard | 2026-02-12 | `bcc2575f-b226-44ae-865f-964fd60f129e` | Life insurance | PEGARD Catherine | €1 086 077 | `1086077` | 0 |
| 21 | M. Jean-Noel Barrot | 2025-12-05 | `302d9e1f-7835-4269-b775-261e0a04fc8a` | Real estate | Maison individuelle | €1 027 792 | `1027792` | 4 |
| 22 | M. jean-pierre farandou | 2026-02-28 | `cee1589c-81bd-4dcc-9431-58dd9d72f2c0` | Real estate | Appartement | €1 000 000 | `1000000` | 0 |
| 23 | M. jean-pierre farandou | 2025-11-13 | `f327ee29-29a8-43a9-ad66-ba2cf59e9c86` | Real estate | Appartement | €1 000 000 | `1000000` | 0 |
| 24 | Mme Catherine Brouard-Gallet | 2024-05-20 | `324849c0-3a42-4a8f-b470-c27f5fe33cfa` | Real estate | Appartement | €1 000 000 | `1000000` | 0 |
| 25 | Mme Catherine Brouard-Gallet | 2024-06-14 | `4d231832-72b6-460a-8485-c073ba7bf767` | Real estate | Appartement | €1 000 000 | `1000000` | 0 |
| 26 | M. benjamin haddad | 2025-12-15 | `4a26227d-f73c-42af-9fd5-fcb2f1d01192` | Foreign assets | Bien immobilier | €970 363 | `970363` | 0 |
| 27 | M. Rémi Bouchez | 2025-03-11 | `31e7cefd-5945-415f-a881-6244f95ff7b9` | Real estate | Appartement | €970 200 | `970200` | 0 |
| 28 | M. Rémi Bouchez | 2024-09-07 | `4cbb3f5d-bed9-4870-b22b-4f3f76450a03` | Real estate | Appartement | €970 200 | `970200` | 0 |
| 29 | Mme alice rufo | 2025-10-20 | `6ca782ee-be24-42c2-976c-57d78c8988cc` | Real estate | Appartement | €936 000 | `936000` | 0 |
| 30 | M. Jean-Noel Barrot | 2026-02-25 | `c0ed614c-26a5-4531-ad13-f826e37cba6c` | Real estate | Maison individuelle | €922 400 | `922400` | 4 |
| 31 | Mme Florence Ribard | 2026-04-14 | `0a10a606-2318-43cf-8fa8-22d392559ff5` | Life insurance | Ribard Florence | €904 631 | `904631` | 0 |
| 32 | M. PHILIPPE TABAROT | 2025-12-03 | `2fd25bf5-de0b-473e-8613-0f0f4adb5027` | Real estate | Maison individuelle | €830 000 | `830000` | 1 |
| 33 | M. jean-pierre farandou | 2026-02-28 | `cee1589c-81bd-4dcc-9431-58dd9d72f2c0` | Real estate | Appartement | €790 000 | `790000` | 1 |
| 34 | M. jean-pierre farandou | 2025-11-13 | `f327ee29-29a8-43a9-ad66-ba2cf59e9c86` | Real estate | Appartement | €790 000 | `790000` | 1 |
| 35 | M. Roland Lescure | 2025-10-19 | `2bd08f0f-8aba-4e87-b2f4-d564a963a79a` | Real estate | Maison individuelle | €771 000 | `771000` | 3 |
| 36 | M. Sebastien LECORNU | 2025-11-13 | `b6ff5941-142a-4075-9c06-482c2eaccbfb` | Real estate | Maison individuelle | €770 000 | `770000` | 0 |
| 37 | M. Sebastien LECORNU | 2026-02-27 | `c9a75061-21bc-44ee-8589-e07899a1e4d8` | Real estate | Maison individuelle | €770 000 | `770000` | 0 |
| 38 | M. Sebastien LECORNU | 2026-06-04 | `d832921b-f94c-4e3e-8a4a-34418517b4ac` | Real estate | Maison individuelle | €770 000 | `770000` | 0 |
| 39 | Mme Aurore Bergé | 2025-12-04 | `52ff5cc4-e4ad-41be-9368-fa09f9885101` | Real estate | Maison individuelle | €750 000 | `750000` | 0 |
| 40 | M. Jean-Didier Berger | 2026-04-02 | `45e264fc-64a8-4d13-9ad7-102fcb15e667` | Real estate | Maison individuelle | €742 500 | `742500` | 0 |
| 41 | M. Jean-Didier Berger | 2026-04-02 | `b2afdbfb-63b1-444f-b3c2-7f48f42033b9` | Real estate | Maison individuelle | €742 500 | `742500` | 0 |
| 42 | Mme Aurore Bergé | 2025-12-04 | `52ff5cc4-e4ad-41be-9368-fa09f9885101` | Real estate | Maison individuelle | €695 000 | `695000` | 1 |
| 43 | Mme Aurore Bergé | 2026-05-13 | `ec589d51-7664-4638-bef7-809b1e318273` | Real estate | Maison individuelle | €695 000 | `695000` | 1 |
| 44 | M. Roland Lescure | 2025-10-19 | `2bd08f0f-8aba-4e87-b2f4-d564a963a79a` | Real estate | Appartement | €650 000 | `650000` | 0 |
| 45 | M. Serge Papin | 2026-02-17 | `307a6524-c8a6-4e5c-92b0-731029d15b19` | Real estate | Appartement | €625 000 | `625000` | 0 |
| 46 | Mme Monique BARBUT | 2025-11-13 | `b9c1be04-63ac-4f31-a7c2-4f9edcfc52b3` | Other assets | SC [Données non publiées] | €604 000 | `604000` | 0 |
| 47 | Mme Catherine Chabaud | 2026-02-24 | `b28ed874-b615-41e0-85a0-e968dd6f452b` | Real estate | Maison individuelle | €600 000 | `600000` | 0 |
| 48 | Mme Catherine Chabaud | 2025-11-08 | `f1b39514-b457-4a13-be34-49e87d297d20` | Real estate | Maison individuelle | €600 000 | `600000` | 0 |
| 49 | Mme Florence Ribard | 2026-04-14 | `0a10a606-2318-43cf-8fa8-22d392559ff5` | Real estate | Maison individuelle | €600 000 | `600000` | 0 |
| 50 | M. jean-pierre farandou | 2026-02-28 | `cee1589c-81bd-4dcc-9431-58dd9d72f2c0` | Life insurance | CNP ONE | €591 011 | `591011` | 7 |
| 51 | M. jean-pierre farandou | 2025-11-13 | `f327ee29-29a8-43a9-ad66-ba2cf59e9c86` | Life insurance | CNP ONE | €591 011 | `591011` | 7 |
| 52 | Mme Monique BARBUT | 2026-03-22 | `0e8fdc5f-1425-4a4f-9243-8ed3e1f3fb0b` | SCI / property company | — | €583 000 | `583000` | 0 |
| 53 | Mme Monique BARBUT | 2025-11-13 | `b9c1be04-63ac-4f31-a7c2-4f9edcfc52b3` | SCI / property company | — | €583 000 | `583000` | 0 |
| 54 | M. Mathieu LEFEVRE | 2026-02-19 | `0d112243-6618-4335-9fa0-872c27194b23` | Real estate | Appartement | €573 000 | `573000` | 2 |
| 55 | M. Mathieu LEFEVRE | 2025-10-29 | `5382331f-88ab-4089-99e3-e2f1e9a7289f` | Real estate | Appartement | €573 000 | `573000` | 2 |
| 56 | M. Serge Papin | 2026-02-17 | `307a6524-c8a6-4e5c-92b0-731029d15b19` | Life insurance | SERGE PAPIN | €567 673 | `567673` | 0 |
| 57 | M. Serge Papin | 2025-12-05 | `bd19a0d5-eb22-4649-bb6b-e8d77ff89118` | Life insurance | SERGE PAPIN | €567 673 | `567673` | 0 |
| 58 | Mme Monique BARBUT | 2026-03-22 | `0e8fdc5f-1425-4a4f-9243-8ed3e1f3fb0b` | Other assets | SC [Données non publiées] | €554 164 | `554164` | 0 |
| 59 | Mme catherine vautrin | 2025-11-02 | `443aca59-8b1d-4cd0-a38e-ddaac448d82a` | Real estate | Maison individuelle | €545 450 | `545450` | 0 |
| 60 | Mme Sabrina ROUBACHE | 2026-05-10 | `56492a1d-8aab-4423-9593-11be3baeb4ef` | Real estate | Maison individuelle | €540 000 | `540000` | 0 |
| 61 | Mme Sabrina ROUBACHE | 2026-03-24 | `a3f9180d-82df-470e-a281-d6fe8543dd15` | Real estate | Maison individuelle | €540 000 | `540000` | 0 |
| 62 | Mme Aurore Bergé | 2026-05-13 | `ec589d51-7664-4638-bef7-809b1e318273` | Real estate | Maison individuelle | €525 000 | `525000` | 0 |
| 63 | Mme Anne Le Hénanff | 2025-11-16 | `69f2d720-c3de-4a9e-9cae-970b0bceee66` | Real estate | Maison individuelle | €470 000 | `470000` | 1 |
| 64 | Mme francine levon-guerin | 2026-01-27 | `9a3fd717-92d6-4dcb-8bcc-877aaa95dec3` | Real estate | Appartement | €470 000 | `470000` | 0 |
| 65 | M. Serge Papin | 2026-02-17 | `307a6524-c8a6-4e5c-92b0-731029d15b19` | Unlisted securities | FINAPA | €469 972 | `469972` | 1 |
| 66 | M. Serge Papin | 2025-12-05 | `bd19a0d5-eb22-4649-bb6b-e8d77ff89118` | Unlisted securities | FINAPA | €469 972 | `469972` | 1 |
| 67 | Mme Monique BARBUT | 2026-03-22 | `0e8fdc5f-1425-4a4f-9243-8ed3e1f3fb0b` | Life insurance | BARBUT MONIQUE | €459 082 | `459082` | 1 |
| 68 | Mme Monique BARBUT | 2025-11-13 | `b9c1be04-63ac-4f31-a7c2-4f9edcfc52b3` | Life insurance | BARBUT MONIQUE | €459 082 | `459082` | 1 |
| 69 | M. Edouard GEFFRAY | 2025-12-08 | `1155d9b2-782c-4670-aed4-d0aff6f6aeef` | Real estate | Maison individuelle | €450 000 | `450000` | 0 |
| 70 | M. Jean-Noel Barrot | 2026-02-25 | `c0ed614c-26a5-4531-ad13-f826e37cba6c` | Bank accounts | Compte courant | €429 347 | `429347` | 7 |
| 71 | Mme Anne Le Hénanff | 2025-11-16 | `69f2d720-c3de-4a9e-9cae-970b0bceee66` | Real estate | Maison individuelle | €420 000 | `420000` | 0 |
| 72 | Mme Naima Moutchou | 2026-03-05 | `5784dc94-12d6-4aa5-a44e-12dd229c18ae` | Foreign assets | Créance à l'égard de la société [Données non publiées] pour acquérir une maison | €410 000 | `410000` | 0 |
| 73 | Mme Naima Moutchou | 2025-11-24 | `d042bdf0-9e69-4520-b67e-5f1ebae99ab2` | Foreign assets | Créance à l'égard de la société [Données non publiées] pour acquérir une maison | €410 000 | `410000` | 0 |
| 74 | M. Nicolas Forissier | 2025-11-16 | `1ef45579-254a-48ad-a43b-f16677371fc5` | Real estate | Maison individuelle | €400 000 | `400000` | 0 |
| 75 | M. Nicolas Forissier | 2026-02-27 | `32bdb365-b2a2-48ce-b18b-e7fb202cb4c4` | Real estate | Maison individuelle | €400 000 | `400000` | 0 |
| 76 | Mme Charlotte LECOCQ | 2026-03-03 | `3ae51772-5b1b-4d15-afe8-4f018589442e` | Real estate | Appartement | €400 000 | `400000` | 0 |
| 77 | Mme Françoise Gatel | 2025-11-21 | `47ead3d6-257b-4dff-a359-7cf480189c35` | Real estate | Maison individuelle | €400 000 | `400000` | 1 |
| 78 | Mme Françoise Gatel | 2026-02-13 | `54b3975d-2daa-4587-82fb-0814860d6f01` | Real estate | Maison individuelle | €400 000 | `400000` | 1 |
| 79 | M. Jean-Noel Barrot | 2025-12-05 | `302d9e1f-7835-4269-b775-261e0a04fc8a` | Real estate | Appartement | €368 021 | `368021` | 2 |
| 80 | M. Jean-Noel Barrot | 2026-02-25 | `c0ed614c-26a5-4531-ad13-f826e37cba6c` | Real estate | Appartement | €368 021 | `368021` | 2 |
| 81 | M. Gérard TERRIEN | 2025-12-20 | `0f874fb8-0e5a-4f5a-bdc9-870ab282f0c6` | Real estate | Appartement | €357 500 | `357500` | 0 |
| 82 | M. Gérard TERRIEN | 2024-01-12 | `bc435e56-4dcc-4d94-a319-d412b607aeb2` | Real estate | Appartement | €357 500 | `357500` | 0 |
| 83 | M. Gérard TERRIEN | 2022-01-21 | `d00d89a4-a201-455f-9993-d0f40a052c37` | Real estate | Appartement | €357 500 | `357500` | 0 |
| 84 | M. LAURENT NUNEZ | 2026-02-09 | `323781a6-bd3b-4134-bf7e-30a963bfa27b` | Real estate | Appartement | €354 000 | `354000` | 2 |
| 85 | M. LAURENT NUNEZ | 2025-11-23 | `e4e3a7c0-bed2-4549-81f5-35eaa9ce17e9` | Real estate | Appartement | €354 000 | `354000` | 2 |
| 86 | M. Laurent PANIFOUS | 2025-11-07 | `07ba839d-dfed-4db1-9f46-72f129fe42ec` | Real estate | Maison individuelle | €350 000 | `350000` | 1 |
| 87 | Mme Amélie de Montchalin | 2026-03-14 | `3261cb23-f5cd-4d7f-9622-732629e474b2` | Real estate | Maison individuelle | €350 000 | `350000` | 1 |
| 88 | M. Jean-Noel Barrot | 2025-12-05 | `302d9e1f-7835-4269-b775-261e0a04fc8a` | Real estate | Garage | €349 667 | `349667` | 7 |
| 89 | M. Jean-Noel Barrot | 2026-02-25 | `c0ed614c-26a5-4531-ad13-f826e37cba6c` | Real estate | Garage | €349 667 | `349667` | 7 |
| 90 | Mme Catherine Brouard-Gallet | 2024-05-20 | `324849c0-3a42-4a8f-b470-c27f5fe33cfa` | Life insurance | Catherine Gallet | €348 111 | `348111` | 0 |
| 91 | Mme Catherine Brouard-Gallet | 2024-06-14 | `4d231832-72b6-460a-8485-c073ba7bf767` | Life insurance | Catherine Gallet | €348 111 | `348111` | 0 |
| 92 | M. Sébastien Martin | 2025-10-19 | `91ad3e7d-9aa9-43f3-83d0-de69725c053f` | Real estate | Appartement | €340 000 | `340000` | 0 |
| 93 | M. Rémi Bouchez | 2025-03-11 | `31e7cefd-5945-415f-a881-6244f95ff7b9` | Life insurance | Rémi Bouchez | €328 511 | `328511` | 0 |
| 94 | Mme Stephanie Rist | 2026-02-21 | `d87a341b-68e4-4fcd-9b2e-0adb201efdf8` | Life insurance | — | €326 050 | `326050` | 0 |
| 95 | M. Jean Maïa | 2026-04-09 | `50d46461-b2a5-4668-a3ba-75a13f29c0c3` | Life insurance | Maïa Jean | €320 123 | `320123` | 1 |
| 96 | M. Jean Maïa | 2026-04-09 | `50d46461-b2a5-4668-a3ba-75a13f29c0c3` | Life insurance | Maïa Jean | €315 190 | `315190` | 2 |
| 97 | M. Jean-Noel Barrot | 2025-12-05 | `302d9e1f-7835-4269-b775-261e0a04fc8a` | Other assets | Caisse des Règlements Pécuniaires des Avocats [Données non publiées] | €313 573 | `313573` | 2 |
| 98 | M. Jean-Noel Barrot | 2026-02-25 | `c0ed614c-26a5-4531-ad13-f826e37cba6c` | Other assets | Caisse des Règlements Pécuniaires des Avocats [Données non publiées] | €313 573 | `313573` | 2 |
| 99 | Mme Monique BARBUT | 2026-03-22 | `0e8fdc5f-1425-4a4f-9243-8ed3e1f3fb0b` | Life insurance | BARBUT MONIQUE | €306 815 | `306815` | 0 |
| 100 | Mme Monique BARBUT | 2025-11-13 | `b9c1be04-63ac-4f31-a7c2-4f9edcfc52b3` | Life insurance | BARBUT MONIQUE | €306 815 | `306815` | 0 |
| 101 | Mme Catherine Chabaud | 2026-02-24 | `b28ed874-b615-41e0-85a0-e968dd6f452b` | Life insurance | Chabaud Catherine | €305 408 | `305408` | 1 |
| 102 | Mme Catherine Chabaud | 2025-11-08 | `f1b39514-b457-4a13-be34-49e87d297d20` | Life insurance | Chabaud Catherine | €305 408 | `305408` | 1 |
| 103 | M. Jean-Noel Barrot | 2025-12-05 | `302d9e1f-7835-4269-b775-261e0a04fc8a` | Other assets | Quote-part estimative du capital figurant sur les contrats d'assurance-vie [Données non publiées] | €300 000 | `300000` | 6 |
| 104 | Mme Naima Moutchou | 2026-03-05 | `5784dc94-12d6-4aa5-a44e-12dd229c18ae` | Real estate | Maison individuelle | €300 000 | `300000` | 1 |
| 105 | Mme Naima Moutchou | 2025-11-24 | `d042bdf0-9e69-4520-b67e-5f1ebae99ab2` | Real estate | Maison individuelle | €300 000 | `300000` | 1 |
| 106 | M. VINCENT JEANBRUN | 2025-10-22 | `b016ad28-4c76-4fbb-9cd4-c78a5268763b` | Real estate | Maison individuelle | €294 000 | `294000` | 0 |
| 107 | Mme Camille Galliard-Minier | 2026-04-09 | `adca1851-ccc6-4068-a652-b1e879b543f4` | Real estate | Maison individuelle | €292 500 | `292500` | 0 |
| 108 | M. PHILIPPE TABAROT | 2025-12-03 | `2fd25bf5-de0b-473e-8613-0f0f4adb5027` | Real estate | Maison individuelle | €270 660 | `270660` | 0 |
| 109 | Mme MARINA FERRARI | 2025-11-30 | `e0b95884-0d64-4b4a-b280-f1b6f34a38eb` | Real estate | Appartement | €270 000 | `270000` | 0 |
| 110 | M. Jean-Noel Barrot | 2025-12-05 | `302d9e1f-7835-4269-b775-261e0a04fc8a` | Real estate | Appartement | €269 167 | `269167` | 8 |
| 111 | Mme Naima Moutchou | 2026-03-05 | `5784dc94-12d6-4aa5-a44e-12dd229c18ae` | Real estate | Appartement | €260 000 | `260000` | 0 |
| 112 | Mme Naima Moutchou | 2025-11-24 | `d042bdf0-9e69-4520-b67e-5f1ebae99ab2` | Real estate | Appartement | €260 000 | `260000` | 0 |
| 113 | M. Nicolas Forissier | 2025-11-16 | `1ef45579-254a-48ad-a43b-f16677371fc5` | SCI / property company | — | €256 747 | `256747` | 0 |
| 114 | Mme Annie GENEVARD | 2025-11-07 | `697577ec-9c79-44f3-be24-137c680316ff` | Life insurance | Annie GENEVARD | €253 183 | `253183` | 1 |
| 115 | Mme Annie GENEVARD | 2025-11-07 | `697577ec-9c79-44f3-be24-137c680316ff` | Real estate | maison individuelle | €240 000 | `240000` | 0 |
| 116 | Mme Rachida Dati | 2026-04-22 | `6dcd326d-e076-4d7a-a428-15075a15dddd` | Real estate | Appartement | €238 650 | `238650` | 0 |
| 117 | M. Nicolas Forissier | 2025-11-16 | `1ef45579-254a-48ad-a43b-f16677371fc5` | Other assets | SCI [Données non publiées] | €234 817 | `234817` | 0 |
| 118 | M. Nicolas Forissier | 2026-02-27 | `32bdb365-b2a2-48ce-b18b-e7fb202cb4c4` | Other assets | SCI [Données non publiées] | €234 817 | `234817` | 0 |
| 119 | Mme Catherine Pégard | 2026-07-03 | `30a4d227-58b7-4272-bb02-7b184261a28f` | Listed securities | BNP Paribas | €230 580 | `230580` | 0 |
| 120 | Mme Catherine Pégard | 2026-02-12 | `bcc2575f-b226-44ae-865f-964fd60f129e` | Listed securities | BNP Paribas | €230 580 | `230580` | 0 |
| 121 | Mme Aurore Bergé | 2025-12-04 | `52ff5cc4-e4ad-41be-9368-fa09f9885101` | Bank accounts | Compte d'épargne | €230 010 | `230010` | 5 |
| 122 | M. Jean Maïa | 2026-04-09 | `50d46461-b2a5-4668-a3ba-75a13f29c0c3` | Real estate | Maison individuelle | €230 000 | `230000` | 0 |
| 123 | Mme catherine vautrin | 2025-11-02 | `443aca59-8b1d-4cd0-a38e-ddaac448d82a` | SCI / property company | — | €227 055 | `227055` | 0 |
| 124 | M. Gérald Darmanin | 2025-12-05 | `d4449adc-cdf1-4752-8981-ab9925f6a7f2` | Real estate | Appartement | €225 000 | `225000` | 0 |
| 125 | Mme Aurore Bergé | 2026-05-13 | `ec589d51-7664-4638-bef7-809b1e318273` | Bank accounts | Compte d'épargne | €224 459 | `224459` | 5 |
| 126 | Mme Maud BREGEON | 2026-07-27 | `f2b84cea-cbba-4e05-a6a6-cb656fb4a80e` | Real estate | Maison individuelle | €220 000 | `220000` | 0 |
| 127 | Mme Maud BREGEON | 2026-04-30 | `f9e780b3-8763-442c-ba34-50e31f6206e7` | Real estate | Maison individuelle | €220 000 | `220000` | 0 |
| 128 | M. Rémi Bouchez | 2024-09-07 | `4cbb3f5d-bed9-4870-b22b-4f3f76450a03` | Life insurance | Rémi Bouchez | €218 935 | `218935` | 0 |
| 129 | M. Rémi Bouchez | 2024-01-23 | `6e136e04-b5b7-4087-93c2-ae8dba947e9f` | Life insurance | Rémi Bouchez | €218 935 | `218935` | 0 |
| 130 | M. Rémi Bouchez | 2024-02-28 | `8947c42d-6ed0-4c5c-b2d0-6d34399230ca` | Life insurance | Rémi Bouchez | €218 935 | `218935` | 0 |
| 131 | M. Laurent PANIFOUS | 2025-11-07 | `07ba839d-dfed-4db1-9f46-72f129fe42ec` | Life insurance | PANIFOUS LAURENT | €218 615 | `218615` | 0 |
| 132 | M. Gérard TERRIEN | 2022-01-21 | `d00d89a4-a201-455f-9993-d0f40a052c37` | Life insurance | Gérard Terrien | €210 748 | `210748` | 1 |
| 133 | M. MICHEL FOURNIER | 2025-11-17 | `acb6b55c-bacb-40f5-8cd0-1cdfe7699a17` | Other assets | SCI [Données non publiées] | €207 381 | `207381` | 0 |
| 134 | M. MICHEL FOURNIER | 2026-03-20 | `f7127e0a-c19a-4081-968f-bfa5e6a832dc` | Other assets | SCI [Données non publiées] | €207 381 | `207381` | 0 |
| 135 | Mme Sabrina ROUBACHE | 2026-05-10 | `56492a1d-8aab-4423-9593-11be3baeb4ef` | Life insurance | Sabrina Agresti Roubache | €200 702 | `200702` | 0 |
| 136 | Mme Sabrina ROUBACHE | 2026-03-24 | `a3f9180d-82df-470e-a281-d6fe8543dd15` | Life insurance | Sabrina Agresti Roubache | €200 702 | `200702` | 0 |
| 137 | M. LAURENT NUNEZ | 2026-02-09 | `323781a6-bd3b-4134-bf7e-30a963bfa27b` | Real estate | Appartement | €200 000 | `200000` | 1 |
| 138 | M. LAURENT NUNEZ | 2025-11-23 | `e4e3a7c0-bed2-4549-81f5-35eaa9ce17e9` | Real estate | Appartement | €200 000 | `200000` | 1 |
| 139 | M. MICHEL FOURNIER | 2025-11-17 | `acb6b55c-bacb-40f5-8cd0-1cdfe7699a17` | Real estate | Maison individuelle | €200 000 | `200000` | 0 |
| 140 | M. MICHEL FOURNIER | 2026-03-20 | `f7127e0a-c19a-4081-968f-bfa5e6a832dc` | Real estate | Maison individuelle | €200 000 | `200000` | 0 |
| 141 | M. Patrick Wyon | 2026-02-13 | `792d05d3-70c2-444e-98e4-9b37ff6a75dc` | Real estate | Appartement | €200 000 | `200000` | 0 |
| 142 | Mme Annie GENEVARD | 2025-11-07 | `697577ec-9c79-44f3-be24-137c680316ff` | Real estate | maison secondaire chalet | €200 000 | `200000` | 1 |
| 143 | M. Gérard TERRIEN | 2022-01-21 | `d00d89a4-a201-455f-9993-d0f40a052c37` | Bank accounts | COMPTE SUR LIVRET BFM | €192 252 | `192252` | 3 |

## Method and limitations

- The outlier detector uses the median and median absolute deviation (MAD) over numeric `assets.normalized_value` rows. The robust scale is `1.4826 × MAD`; rows with an absolute robust z-score above 10 are flagged and retained.
- The detector was run on the full asset table for snapshot `2026-08-17`, which contains 1,376 rows, including 1,156 rows with numeric normalized values.
- The report does not infer whether a value is correct, illicit, duplicated across declarations, a partial ownership value, or a source parsing issue. Each flag requires source review.
- Declarant names are joined by `declaration_uuid`; repeated names are not treated as unique identities. The report preserves the declaration UUID for disambiguation.
- “Publication date” here means the normalized declaration deposit date from the source XML (`date_depot`), not an independently verified public-web publication timestamp.

## Recommended fact-check sequence

1. Start with the highest-value rows and the grouped declarations above.
2. Use the declarant name, normalized publication date, and declaration UUID to locate the corresponding HATVP source declaration or PDF.
3. Compare the displayed asset value with the source field and inspect ownership share, valuation date, asset type, and whether the same asset appears in related declarations.
4. Record confirmed source issues as pipeline fixtures or normalization fixes; retain plausible high values as review flags.

## Source artifacts

- Assets: `gs://yahatvp-pipeline-eu-data/hatvp/silver/assets/snapshot_date=2026-08-17/data.parquet`
- People: `gs://yahatvp-pipeline-eu-data/hatvp/silver/people/snapshot_date=2026-08-17/data.parquet`
- Declarations: `gs://yahatvp-pipeline-eu-data/hatvp/silver/declarations/snapshot_date=2026-08-17/data.parquet`
- Quality anomalies: `gs://yahatvp-pipeline-eu-data/hatvp/quarantine/snapshot_date=2026-08-17/anomalies.parquet`
- Pipeline quality report: `gs://yahatvp-pipeline-eu-data/hatvp/quality/snapshot_date=2026-08-17/report.json`
