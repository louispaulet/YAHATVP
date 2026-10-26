# 2026-10-27 HATVP refresh and publication-search validation

## Conclusion

The weekly runs on October 12, 19, and 26 completed, but each reported
`NO_CHANGE`: the official HATVP CSV and XML hashes had not changed. That alone
does not explain the historical sample counts. Silver's distinct declaration
count fell from 17,898 on August 23 to 17,812 on October 6, contrary to the
intended cumulative-retention behavior. The October 27 replay now has 17,900
distinct declarations in Silver, including versions absent from the latest
official export. The older BigQuery partitions remain historical evidence and
were not rewritten.

Search and declaration detail now use Silver so preserved public records remain
findable. Current dashboard statistics use Gold, whose latest partition
represents the current analytical selection. The example below was present in
the August 30 official snapshot and absent from the October 5 official XML; its
exact removal date is not known.

## Scheduled refreshes and source bytes

| Scheduled date | Cloud Run execution | Start–finish (UTC) | Result |
| --- | --- | --- | --- |
| 2026-10-12 | `hatvp-ingestion-m4vfp` | 05:01:08–05:01:50 | `NO_CHANGE` |
| 2026-10-19 | `hatvp-ingestion-92nwm` | 05:00:29–05:01:17 | `NO_CHANGE` |
| 2026-10-26 | `hatvp-ingestion-wpvpm` | 06:00:52–06:02:07 | `NO_CHANGE` |

All three scheduled executions observed the same official source hashes:

- XML: `a042d437b9b05f0af0aa93e7e95f18b038fb21c0eb8a3b69f499dc1e66bcd9cb`
- CSV: `781fc5e54b20bda1be5b095dcd76bbfee674cee342ec36e694099f6781704597`

The XML currently captured from HATVP matches the source snapshot dated October
5. These scheduled executions did not create newer source snapshots.

## Declaration sample counts by BigQuery snapshot

“Samples” below means `COUNT(DISTINCT declaration_uuid)`, not Silver row count.
Silver row counts include multiple declaration versions and source records.
Gold rows are current analytical records; they are not a cumulative archive.
Older partitions predate publication-status fields, so their online/unpublished
row counts are unavailable rather than zero.

| Snapshot date | Silver rows | Silver distinct declarations | Silver online rows | Silver unpublished rows | Gold rows | Gold distinct declarations | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2026-08-19 | 6,611 | 6,605 | — | — | 6,615 | 6,605 | Legacy partition |
| 2026-08-23 | 31,578 | 17,898 | — | — | 17,899 | 17,898 | Legacy partition |
| 2026-08-24 | 31,578 | 17,898 | — | — | 17,950 | 17,898 | Legacy partition |
| 2026-08-28 | 31,497 | 17,884 | — | — | 17,885 | 17,884 | Legacy partition |
| 2026-08-30 | 31,497 | 17,884 | — | — | 17,957 | 17,884 | Legacy partition |
| 2026-10-06 | 30,946 | 17,812 | — | — | 17,813 | 17,812 | Legacy partition |
| 2026-10-26 | 38,133 | 17,900 | 20,670 | 17,463 | 17,985 | 17,900 | Interim partition with incorrect lifecycle assignment; superseded |
| **2026-10-27** | **38,133** | **17,900** | **18,446** | **19,687** | **18,005** | **17,900** | **Current, corrected partition** |

The October 26 interim partition came from the first replay after the lifecycle
change. Its publication-status arguments were reversed. The call was corrected;
two corrected-image attempts then hit the memory limit while serializing Silver
and did not advance pipeline state or load BigQuery. A follow-up change reduced
peak serialization memory. Execution `hatvp-ingestion-fzrln` then completed
successfully, wrote all 13 BigQuery tables, and advanced `state/latest.json` to
October 27. The current search API selects the maximum Silver snapshot date,
therefore it reads the corrected October 27 partition.

## Unpublished declaration verified in production

- **Declaration UUID:** `1b384fad-9ae2-4cea-a5b3-812244f0628d`
- **Declarant:** Françoise DUMONT
- **Type:** amended declaration of interests and activities
- **Deposited:** June 29, 2026
- **Mandate / organisation:** senator / Var (83)
- **Preserved source snapshot:** August 30, 2026
- **Current publication status:** unpublished; absent from the October 5 HATVP
  XML extract
- **Search test:** [open this declaration search](https://yahatvp.thefrenchartist.dev/#/search?q=1b384fad-9ae2-4cea-a5b3-812244f0628d)

Chrome loaded the deployed frontend from the ordinary public URL in a clean
browser context. The result showed “Not in latest HATVP extract”; opening it
showed the preserved-publication context and source XML. The API search returned
HTTP 200 with `publicationStatus: "unpublished"` and
`sourceSnapshotDate: "2026-08-30"`. No console errors were observed. An older
already-open Chrome context had cached the September frontend asset; a fresh
context loaded the current hashed asset and showed the updated badge and copy.

The public API's latest overview returned snapshot `2026-10-27` and Gold-backed
counts of 18,005 declaration rows, 7,318 people, 242,399 eligible income rows,
and 4,854 eligible asset rows. These are current analytical counts, not the
cumulative declaration sample series above.

## Code, deployment, and verification

- Search and detail queries select Silver; the Gold query table mapping remains
  the source for dashboard aggregates. The declaration response includes
  publication status and source snapshot, and detail serves the preserved raw
  XML object.
- Commits `0a1a592` (Silver-backed search/detail), `359c773` (publication
  lifecycle argument correction), and `9c1dce0` (lower-memory layer writes) are
  on `main`.
- Forced replay `hatvp-ingestion-fzrln` completed in about 14 minutes with
  `SUCCESS_WITH_WARNINGS`, zero quality errors, 40,156 warnings, 57,370
  flagged records, and warning streak 23.
- GitHub Actions run `40416843578` passed. Local verification passed 185 Python
  tests, 13 Worker tests, 48 bridge tests, 47 frontend tests, Worker typecheck,
  Ruff, package build, and frontend build.
- Cloud Run bridge revision `hatvp-dashboard-api-00037-xrv` serves 100% of
  traffic. Worker version `e976a62c-b3cc-4ea9-a17e-bc3cabff1ea5` is deployed.
  The frontend was published to the public GitHub Pages domain.

The 23-run warning streak remains a human-review follow-up. The reported
warnings and flagged records are source-quality signals; this report does not
assert that their underlying declarations are incorrect.
