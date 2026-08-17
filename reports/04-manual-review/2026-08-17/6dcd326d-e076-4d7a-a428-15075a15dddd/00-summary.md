# Manual declaration review fixture

This folder contains one declaration from the 2026-08-17 HATVP XML snapshot
for manual parser review.

- `01-declaration.xml` is the selected declaration serialized under a
  `<declarations>` wrapper for easy XML inspection.
- `02-parsed.json` contains the declaration summary and every normalized row whose
  `declaration_uuid` matches the source UUID, grouped by table.
- `02-parsed.json` also contains `source_income.category_slots` with all nine raw
  income categories, including empty slots, plus `source_income.totals` and a
  category-to-total reconciliation.

Selected declaration:

- UUID: `6dcd326d-e076-4d7a-a428-15075a15dddd`
- Declarant: Rachida Dati
- Type: `DSPFM` — declaration of patrimonial situation at end of mandate
- Deposit date: `2026-04-22`
- Parsed rows: 1 declaration, 1 person, 1 mandate, 6 incomes, 19 assets, and
  0 liabilities

The six populated category values sum to the source `totalElu` value of
`73005`. The total is kept in the source-income view but is not emitted as a
seventh normalized income row because it is an aggregate of the categories.

`02-parsed.json` records the full source XML SHA-256, source URL, GCS raw
snapshot path, snapshot date, and parser commit. `raw_record_json` fields
retain the source-level values used for normalization.
