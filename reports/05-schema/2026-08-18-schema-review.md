# HATVP source schema and raw-archive review — 2026-08-18

> Review completed before any normalization change. The current source schema
> remains compatible with the configured parser boundary; no normalization code
> was changed.

## Schema disposition

The review used the latest archived production snapshot and the current public
CSV header:

- XML: `gs://yahatvp-pipeline-eu-data/hatvp/raw/snapshot_date=2026-08-18/declarations.xml`
- CSV: `gs://yahatvp-pipeline-eu-data/hatvp/raw/snapshot_date=2026-08-18/liste.csv`
- XML source URL: `https://www.hatvp.fr/livraison/merge/declarations.xml`
- CSV source URL: `https://www.hatvp.fr/livraison/opendata/liste.csv`
- Pipeline schema configuration: `src/hatvp/pipeline.yml`

The XML inventory contains 6,611 declarations with root `declarations` and
direct top-level child `declaration`. This matches the configured
`xml_root=declarations` and the allowed top-level children
`[declaration, declarations]`.

The current CSV header has 16 semicolon-delimited columns:

```text
civilite;prenom;nom;classement;type_mandat;qualite;type_document;departement;
date_publication;date_depot;nom_fichier;url_dossier;open_data;
statut_publication;id_origine;url_photo
```

Both configured identity columns, `id_origine` and `url_dossier`, remain
present. The current public CSV header matches the archived production CSV
header exactly.

The latest XML contains every currently modeled section: income, elected
mandates, liabilities, activities, participations, and all configured asset
DTOs. It also contains four observed but intentionally unmodeled declaration
children: `attachedFiles`, `evenementMajeurDto`, `observationInteretDto`, and
`observationPatrimoineDto`. They are documented here rather than silently
invented into normalized tables. Any future decision to model one of them must
start with a source fixture and focused tests.

## Fixture guardrail

The new `tests/fixtures/schema_review.xml` fixture contains the four observed
unmodeled sections and verifies that the parser preserves the declaration and
person rows without inventing normalized rows for unsupported sections.

The existing `tests/fixtures/quality_triage.xml` fixture already covers the
observed duplicate UUID and trailing-whitespace edge case, with assertions in
`tests/test_quality_triage.py` for distinct canonical XML hashes and identical
semantic hashes. No normalization fix was needed during this review.

## Historical raw snapshot immutability

The production bucket reports `versioning_enabled: true`,
`uniform_bucket_level_access: true`, and `public_access_prevention: enforced`.
The raw storage adapter uses `if_generation_match=0` for immutable writes and
only accepts a retry when the existing bytes match exactly.

The three historical snapshots each have one visible object generation for
both raw files. Their byte-level storage checksums are identical across dates:

| Snapshot | XML generation | CSV generation | XML size | CSV size | XML MD5 | CSV MD5 |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `2026-08-16` | `1786913756346402` | `1786913755619158` | 88,825,812 | 3,312,738 | `xH4xtWu67pHeawiM96OuVw==` | `LuuNqLWvujnAczGF3I+1dA==` |
| `2026-08-17` | `1786918419370483` | `1786918418645726` | 88,825,812 | 3,312,738 | `xH4xtWu67pHeawiM96OuVw==` | `LuuNqLWvujnAczGF3I+1dA==` |
| `2026-08-18` | `1787006049828486` | `1787006049021953` | 88,825,812 | 3,312,738 | `xH4xtWu67pHeawiM96OuVw==` | `LuuNqLWvujnAczGF3I+1dA==` |

No historical raw object was overwritten, deleted, or rewritten as part of
this review.

## Verification

- `src/hatvp/pipeline.yml` was compared with the current CSV header and latest
  XML root, top-level structure, and section inventory.
- The live CSV endpoint returned the same 16-column semicolon-delimited header;
  the latest archived XML snapshot supplied the full streaming inventory.
- `gcloud storage buckets describe` confirmed bucket versioning and access
  protections.
- `gcloud storage objects describe` and `gcloud storage ls -a` confirmed raw
  object generations, sizes, and checksums for all three snapshots.
- The fixture-backed parser and triage tests cover the observed edge cases
  before any future normalization change.
