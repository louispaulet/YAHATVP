# BigQuery Bronze contract — 2026-08-18

## Boundary and physical names

The existing `hatvp` BigQuery dataset remains the Bronze boundary. Its four
physical tables keep their deployed names: `declarations`, `people`, `incomes`,
and `assets`. They are not latest-declarant tables and are not renamed while
future Silver and Gold readers are still being designed. The normalized GCS
artifacts continue to use their existing `silver/<table>/snapshot_date=...`
paths; that storage path is historical naming, not a claim that the BigQuery
tables already implement the future Silver anomaly layer.

All four BigQuery tables are partitioned by the `DATE` field `snapshot_date`.
The loader deletes and replaces only the requested partition, then inserts by
explicit column name. Earlier successful snapshot partitions remain available.
There is no uniqueness constraint on `declaration_uuid` and no deduplication
step.

## Observed HATVP grain and version fields

| Bronze table | Grain | Identity and version evidence |
| --- | --- | --- |
| `declarations` | One row per direct XML `<declaration>` occurrence in one source snapshot. | `declaration_uuid` is the stable source UUID when present; `bronze_record_key` distinguishes repeated occurrences. `date_depot`, `declaration_modificative`, `date_derniere_declaration_raw`, `declaration_version`, mandate dates, role, and organ fields remain attached to the row. |
| `people` | One declarant record belonging to one declaration occurrence. | Join to the parent with `bronze_record_key`; `declaration_uuid` is retained but is not assumed unique. Name and date fields are source observations, not an identity replacement. |
| `incomes` | One populated declared-income category or one annual `mandatElectifDto` remuneration value. | Join to the parent with `bronze_record_key`; `source_section`, `source_item_index`, `income_category_index`, `remuneration_index`, and `income_year` identify the observed child value. |
| `assets` | One observed asset DTO item. | Join to the parent with `bronze_record_key`; `source_section` and `source_item_index` identify the source item, while `raw_value` and `normalized_value` remain side by side. |

The source field `declarationVersion` is retained verbatim as
`declaration_version`. In the observed files it behaves as a source/schema
version marker and is not used alone as chronological amendment ordering. The
source `declarationModificative` flag is retained as
`declaration_modificative`; `date_depot` and the source declaration dates are
the available temporal evidence. Latest-version selection is deliberately not
performed in Bronze.

The CSV listing remains a source-shaped GCS table with one row per CSV record.
Its configured stable source identifiers (`id_origine` and `url_dossier`) are
preserved, and `source_record_id` uses the first populated configured identity.

## Required provenance carried into Bronze

Every normalized row now carries the following fields where the source
format allows them:

```text
bronze_record_key, source_record_id, source_format, source_file,
source_url, source_object, source_sha256, source_snapshot_date,
source_location, pipeline_version, parser_version, raw_record_json
```

`bronze_record_key` is a deterministic hash of source format, file, snapshot,
stable source identifier, and source occurrence index. It is a parent key for
XML child rows, so two declarations with the same UUID are still separate
records. The declaration and person rows retain JSON representations of their
source XML nodes; child rows retain their existing item-level JSON evidence;
CSV rows retain the unnormalized source row JSON. Numeric and date fields keep
their existing raw/normalized pairs.

`source_object` points to the immutable raw archive object for pipeline runs,
for example `gs://<bucket>/hatvp/raw/snapshot_date=YYYY-MM-DD/declarations.xml`.
Direct parser calls use the local source path as a fallback. `source_sha256`
matches the exact downloaded bytes recorded in `raw/.../metadata.json`, and
`source_snapshot_date` is a typed `DATE` copy of the partition provenance.

## Historical retention and raw immutability

A later source snapshot or amended declaration never removes an earlier Bronze
row. A repeated UUID in the same snapshot is retained as another row with its
own occurrence key, and a row in a later partition remains queryable beside
the earlier partition. Anomaly processing has no write path to the raw archive.

Raw XML, CSV, and metadata objects continue to be written with immutable
generation preconditions. A retry with identical hashes may reuse the existing
metadata; different bytes for an existing snapshot remain a hard failure. The
raw object, exact hashes, source URLs, and row-level source locations provide
the evidence boundary for future Silver comparisons.

## Future-layer mapping

Silver can copy each Bronze row at the same `bronze_record_key` and add
`anomaly_status`, `rule_ids`, `anomaly_registry_id`, and `metric_eligible`
without changing the observed value. Raw and normalized values, source
locations, and evidence JSON remain available in the Silver row.

Future Gold grain is one latest applicable declaration per stable declarant,
role/mandate, and relevant period. Identity resolution uses source identifiers
first and leaves unresolved matches for review. The documented ordering is
`date_depot`, then the amendment/date evidence (`declaration_modificative` and
`date_derniere_declaration_raw`), with `snapshot_date` and `bronze_record_key`
as deterministic tie-breakers. `declaration_version` is not a standalone
latest-order field. Child rows join to the selected `bronze_record_key`.

The planned registry key is
`declarant_key|field|period|observed_value`, supplemented by declaration and
rule identifiers when the source lacks a reliable declarant key. Historical
registry occurrences remain retained; a future Silver/Gold implementation may
change notification status to `superseded/resolved` without deleting the
underlying Bronze or anomaly evidence. The raw archive and historical
BigQuery partitions are retained under the existing operational policy; no
Bronze change introduces deletion or correction behavior.

No Silver anomaly detection or Gold latest-row selection is enabled by this
Bronze change.

Example version-preserving query:

```sql
SELECT declaration_uuid, bronze_record_key, snapshot_date,
       date_depot, declaration_modificative, declaration_version
FROM `PROJECT.hatvp.declarations`
WHERE snapshot_date BETWEEN DATE '2026-08-16' AND DATE '2026-08-18'
ORDER BY declaration_uuid, date_depot, bronze_record_key;
```
