# Quality triage — HATVP snapshot 2026-08-16

> Auditable review register for every flagged anomaly in the first production snapshot.

## Outcome

The immutable snapshot contains **5,763 flagged records**, with **0 unresolved records** after source-linked review. The register reconciles to the quality report: **passed**.

No raw, silver, quarantine, quality, or state artifact was modified. Statistical flags remain retained; this report records review dispositions rather than correcting source data.

## Evidence

| Item | Value |
| --- | --- |
| Snapshot date | `2026-08-16` |
| Raw XML SHA-256 | `865261857f88ec6c262558bc115b37b94f97ea3418b6829267aa6cbd1458fdaf` |
| Pipeline Git SHA | `f21853de13c236400d3fc9f9b8da34ce16ad7bb2` |
| Quality report | `gs://yahatvp-pipeline-eu-data/hatvp/quality/snapshot_date=2026-08-16/report.json` |
| Quarantine register | `gs://yahatvp-pipeline-eu-data/hatvp/quarantine/snapshot_date=2026-08-16/anomalies.parquet` |
| Raw XML | `gs://yahatvp-pipeline-eu-data/hatvp/raw/snapshot_date=2026-08-16/declarations.xml` |
| Quality report SHA-256 | `ea8a3608ef2acee18327d00f00bc49a2732b6726688fa23d0eed7241e4a6a62b` |
| Quarantine SHA-256 | `8d8fd8a586fd05ed7511ae15094274b3d7ec48fa873b245f1f11e95640b58135` |

## Reconciliation

The source quality report records `5,763` flagged records, zero errors, and `3,510` warnings. The warning count is a separate metric from the anomaly-row count.

| Original quality reason | Rows | Disposition |
| --- | ---: | --- |
| duplicate declaration_uuid: 23a569db-f01d-406b-9d49-d77062d16c0b | 2 | `duplicate_source_identifier`: 2 |
| duplicate declaration_uuid: 3cc80dd4-5497-4119-ae82-bf748f3cf34e | 2 | `duplicate_source_identifier`: 2 |
| duplicate declaration_uuid: 64076b58-0b72-43ed-9d06-3421ed2ad7cf | 2 | `duplicate_source_identifier`: 2 |
| duplicate declaration_uuid: 918bed9f-21cc-46fd-a13a-0f3e07b4b9ce | 2 | `duplicate_source_identifier`: 2 |
| duplicate declaration_uuid: 9ccaaa4b-93bd-4ac3-b99c-e8e5835be9f3 | 2 | `duplicate_source_identifier`: 2 |
| duplicate declaration_uuid: fe395431-4550-4b8d-9251-50bd4cfd5eb0 | 2 | `duplicate_source_identifier`: 2 |
| negative asset value | 9 | `source_valid_flag`: 9 |
| repeated name; retained because names are not stable identity keys | 5,599 | `expected_identity_collision`: 5,599 |
| robust statistical asset outlier; retained for review | 143 | `source_consistent_outlier`: 143 |

| Review disposition | Rows |
| --- | ---: |
| `duplicate_source_identifier` | 12 |
| `expected_identity_collision` | 5,599 |
| `source_consistent_outlier` | 143 |
| `source_valid_flag` | 9 |

## Findings

- **Repeated names:** 5,599 rows across 2,247 normalized name groups. Each matched a source-linked person record and is retained as an expected identity collision; no people were deduplicated.
- **Duplicate declaration UUIDs:** 12 rows across 6 source UUID groups. Each group requires source-quality follow-up.
- **Negative assets:** 9 rows. The reviewed values are bank-account entries and remain flagged as source-valid overdraft-style values.
- **Statistical asset outliers:** 143 rows. Each matched the raw XML and persisted normalized row; values remain descriptive outlier flags for monitoring.

## Duplicate declaration UUID groups

| Declaration UUID | Occurrences | Content | Canonical XML SHA-256 |
| --- | ---: | --- | --- |
| `23a569db-f01d-406b-9d49-d77062d16c0b` | 2 | identical | `3b7664f4e5a29144a0a8f23d3090865a8fde66dd7a30b8133fffc5001318d6f8`<br>`3b7664f4e5a29144a0a8f23d3090865a8fde66dd7a30b8133fffc5001318d6f8` |
| `3cc80dd4-5497-4119-ae82-bf748f3cf34e` | 2 | identical | `b062cbf26974654277e04561e1a36137740c5fb9449dd6228627fc4e7375db22`<br>`b062cbf26974654277e04561e1a36137740c5fb9449dd6228627fc4e7375db22` |
| `64076b58-0b72-43ed-9d06-3421ed2ad7cf` | 2 | identical | `a1c9c7057da83df1fcb003be11b4e2d3d2ccd5e132500df31cb525e5a76ba1d3`<br>`a1c9c7057da83df1fcb003be11b4e2d3d2ccd5e132500df31cb525e5a76ba1d3` |
| `918bed9f-21cc-46fd-a13a-0f3e07b4b9ce` | 2 | identical | `3ae0cc7395914374805d4f83bd2c68c279d1a342337ef449ffeec7fbf11639b9`<br>`3ae0cc7395914374805d4f83bd2c68c279d1a342337ef449ffeec7fbf11639b9` |
| `9ccaaa4b-93bd-4ac3-b99c-e8e5835be9f3` | 2 | conflicting | `3d461dee73181875849b81f7f10547641fb2bfc97da40ed79a987609896c3ed2`<br>`0f958233efe72196454e8d7744829e46a4a318acb4e19be4dd8e29e401068b14` |
| `fe395431-4550-4b8d-9251-50bd4cfd5eb0` | 2 | identical | `28dbe67e5f85da63db41e0657dc75e7e7c4008be2c469c41a01f7fa6d12626b6`<br>`28dbe67e5f85da63db41e0657dc75e7e7c4008be2c469c41a01f7fa6d12626b6` |

## Negative asset values

| Declaration UUID | Section | Item | Raw value | Normalized value | Disposition |
| --- | --- | ---: | ---: | ---: | --- |
| `2fd25bf5-de0b-473e-8613-0f0f4adb5027` | `comptesBancaireDto` | 0 | `-141` | -141 | `source_valid_flag` |
| `2fd25bf5-de0b-473e-8613-0f0f4adb5027` | `comptesBancaireDto` | 3 | `-3421` | -3 421 | `source_valid_flag` |
| `5784dc94-12d6-4aa5-a44e-12dd229c18ae` | `comptesBancaireDto` | 3 | `-620` | -620 | `source_valid_flag` |
| `c9a75061-21bc-44ee-8589-e07899a1e4d8` | `comptesBancaireDto` | 2 | `-559` | -559 | `source_valid_flag` |
| `d042bdf0-9e69-4520-b67e-5f1ebae99ab2` | `comptesBancaireDto` | 3 | `-620` | -620 | `source_valid_flag` |
| `d832921b-f94c-4e3e-8a4a-34418517b4ac` | `comptesBancaireDto` | 2 | `-559` | -559 | `source_valid_flag` |
| `e0b95884-0d64-4b4a-b280-f1b6f34a38eb` | `comptesBancaireDto` | 4 | `-663` | -663 | `source_valid_flag` |
| `f2b84cea-cbba-4e05-a6a6-cb656fb4a80e` | `comptesBancaireDto` | 2 | `-260` | -260 | `source_valid_flag` |
| `f9e780b3-8763-442c-ba34-50e31f6206e7` | `comptesBancaireDto` | 2 | `-260` | -260 | `source_valid_flag` |

## Highest-value asset outliers

The complete row-level register is in the JSON artifact. The table below provides the highest-value source-linked candidates for manual fact checking.

| Declaration UUID | Section | Item | Asset | Raw value | Normalized value |
| --- | --- | ---: | --- | ---: | ---: |
| `307a6524-c8a6-4e5c-92b0-731029d15b19` | `valeursNonEnBourseDto` | 0 | FINAPA | `6719662` | 6 719 662 |
| `bd19a0d5-eb22-4649-bb6b-e8d77ff89118` | `valeursNonEnBourseDto` | 0 | FINAPA | `6719662` | 6 719 662 |
| `6dcd326d-e076-4d7a-a428-15075a15dddd` | `valeursEnBourseDto` | 2 | CIC Market Solution | `3133135` | 3 133 135 |
| `6dcd326d-e076-4d7a-a428-15075a15dddd` | `assuranceVieDto` | 0 | Dati Rachida | `2413888` | 2 413 888 |
| `0e8fdc5f-1425-4a4f-9243-8ed3e1f3fb0b` | `immeubleDto` | 0 | Appartement | `2250000` | 2 250 000 |
| `b9c1be04-63ac-4f31-a7c2-4f9edcfc52b3` | `immeubleDto` | 0 | Appartement | `2250000` | 2 250 000 |
| `2bd08f0f-8aba-4e87-b2f4-d564a963a79a` | `immeubleDto` | 1 | Appartement | `2225000` | 2 225 000 |
| `6e136e04-b5b7-4087-93c2-ae8dba947e9f` | `immeubleDto` | 0 | Appartement | `1764000` | 1 764 000 |
| `8947c42d-6ed0-4c5c-b2d0-6d34399230ca` | `immeubleDto` | 0 | Appartement | `1764000` | 1 764 000 |
| `6ca782ee-be24-42c2-976c-57d78c8988cc` | `immeubleDto` | 1 | Maison individuelle | `1700000` | 1 700 000 |
| `302d9e1f-7835-4269-b775-261e0a04fc8a` | `assuranceVieDto` | 1 | Jean-Noël Barrot | `1634267` | 1 634 267 |
| `c0ed614c-26a5-4531-ad13-f826e37cba6c` | `assuranceVieDto` | 1 | Jean-Noël Barrot | `1623013` | 1 623 013 |
| `00ccc47c-9a67-4b79-a0ed-d3d2cc584d2b` | `immeubleDto` | 0 | Appartement | `1600000` | 1 600 000 |
| `9a3fd717-92d6-4dcb-8bcc-877aaa95dec3` | `immeubleDto` | 2 | Appartement | `1400000` | 1 400 000 |
| `bd19a0d5-eb22-4649-bb6b-e8d77ff89118` | `immeubleDto` | 0 | Appartement | `1250000` | 1 250 000 |
| `06572e52-2668-484b-8b44-c3ab52ccc447` | `immeubleDto` | 0 | Appartement | `1210000` | 1 210 000 |
| `6c96dc98-91e8-4a0a-98c2-1a9111932600` | `immeubleDto` | 0 | Appartement | `1180000` | 1 180 000 |
| `3261cb23-f5cd-4d7f-9622-732629e474b2` | `immeubleDto` | 0 | Maison individuelle | `1160000` | 1 160 000 |
| `30a4d227-58b7-4272-bb02-7b184261a28f` | `assuranceVieDto` | 0 | PEGARD Catherine | `1086077` | 1 086 077 |
| `bcc2575f-b226-44ae-865f-964fd60f129e` | `assuranceVieDto` | 0 | PEGARD Catherine | `1086077` | 1 086 077 |

## Review method and follow-up

- The raw XML is authoritative for source verification; normalized Parquet is used to confirm the persisted row and provenance key.
- Repeated names are not identity proof. Stable declaration UUIDs remain the identity boundary.
- Duplicate UUID groups are retained and require monitoring or source correction; no duplicate declaration was deleted.
- Any source/parser mismatch is an actionable follow-up requiring a fixture before changing normalization logic.
- The machine-readable register contains one entry per flagged row, including source evidence, disposition, review status, notes, and follow-up status.

## Artifacts

- Machine-readable register: `reports/quality-triage-2026-08-16.json`
- Immutable source evidence: the GCS objects listed above
