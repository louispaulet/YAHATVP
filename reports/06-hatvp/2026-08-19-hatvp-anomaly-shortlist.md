# HATVP anomaly review and current declaration shortlist — 2026-08-19

This report records a BigQuery-backed review of the 2026-08-19 HATVP
snapshot and a small, source-linked shortlist for human follow-up with HATVP.
The flags are review signals, not confirmed source errors. No source or
normalized value was changed.

## Decision summary

- The snapshot contains 5,026 anomaly-registry rows. 5,024 are linked to
  current Gold rows, 1,832 have registry status `active`, and 3,194 are
  internally marked `previously_reported`.
- Candidate declarations were restricted to `status = 'active'`,
  `active_in_gold`, and `NOT previously_reported`. The shortlist uses only
  `COMP_YOY_CHANGE`, `COMP_DIGIT_EDIT`, `COMP_FACTOR_ERROR`, and
  `COMP_IMPLAUSIBLE_AMOUNT`.
- The name+surname latest-version rule was applied to all Gold declarations
  before anomalies were joined. The result is 701 deduplicated eligible
  anomaly IDs across 637 latest normalized name+surname pairs after the
  exclusions below.
- Ten declarations are selected for HATVP review. All ten are rank 1 under
  the name+surname version ordering, including the number of versions found
  for that normalized pair.
- The hash-routed public issue register at
  `https://yahatvp.thefrenchartist.dev/#/quality-issues` was inspected directly:
  it shows 10 open issues and 0 solved issues. The non-hash URL is not the
  dashboard route and can return a GitHub Pages 404.

The query used for the analysis and the exact audited shortlist is in
[`2026-08-19-hatvp-anomaly-shortlist.sql`](2026-08-19-hatvp-anomaly-shortlist.sql).

## Dataset, grain, and provenance

The analysis used project `yahatvp-pipeline-eu`, dataset `hatvp`, location
`europe-west1`, and partition `snapshot_date = DATE '2026-08-19'`.

| Layer | declarations | people | incomes | assets |
| --- | ---: | ---: | ---: | ---: |
| Bronze | 6,611 | 6,611 | 106,351 | 1,157 |
| Silver | 6,611 | 6,611 | 106,351 | 1,157 |
| Gold | 6,605 | 6,605 | 106,271 | 1,157 |

Gold is the latest-applicable declaration layer. For this request, an
additional deterministic name-based ordering was applied across all Gold
declarations joined to Gold people:

1. `date_depot` descending;
2. `date_derniere_declaration_raw` descending;
3. modificative declarations before non-modificative declarations;
4. `declaration_version` descending;
5. `declaration_uuid` descending as a deterministic tie-breaker.

The name key is `LOWER(TRIM(prenom))` plus `LOWER(TRIM(nom))`. This is a
pragmatic request-specific deduplication key, not a claim of stable person
identity. The raw HATVP snapshot remains available at
`gs://yahatvp-pipeline-eu-data/hatvp/raw/snapshot_date=2026-08-19/liste.csv`.
Each selected declaration is linked below to its public HATVP dossier; the
anomaly evidence retains its BigQuery registry ID and XML source location.

## Quality findings

All registry rows in this snapshot have severity `review`; the rules are
intentionally conservative signals for source inspection.

| Rule | Total | Active | Internally previously reported | Disposition |
| --- | ---: | ---: | ---: | --- |
| `COMP_YOY_CHANGE` | 2,507 | 948 | 1,559 | Eligible for a small current-review sample |
| `COMP_DIGIT_EDIT` | 1,578 | 358 | 1,220 | Eligible for a small current-review sample |
| `COMP_FACTOR_ERROR` | 237 | 91 | 146 | Eligible for a small current-review sample |
| `COMP_IMPLAUSIBLE_AMOUNT` | 64 | 18 | 46 | Eligible for a small current-review sample |
| `COMP_CONFLICT_SAME_PERIOD` | 301 | 190 | 111 | Excluded: generic amount-inconsistency issue already listed locally |
| `COMP_SUPERSEDED_DECLARATION` | 333 | 227 | 106 | Excluded: historical/supersession path, not a current handoff |
| `PERSON_DOB_IMPLAUSIBLE` | 6 | 0 | 6 | Excluded: DOB issue family already listed locally |
| **Total** | **5,026** | **1,832** | **3,194** | |

The largest current rule family is year-over-year compensation change. It is
useful for review triage but does not establish that a declaration is wrong:
legitimate changes in remuneration, mandate, or activity can produce the same
signal. Factor and digit-edit candidates likewise remain hypotheses until the
source document is checked.

## Existing issue exclusions

The public hash-routed issue register contains 10 open entries. The explicitly
linked declarants were excluded from the shortlist: Jean-François Vigier, Alain
Kelyor, Isabelle Kaloi-Bearune, Robert Cavanna, Jean-Louis Rio, Claude Cannet,
Christelle Michel Deleage, Daniel Rouge, Georges Botella, Allen Salmon,
Chantal Juglard, and Fabienne Keller.

The generic “Amount inconsistency across declarations” entry has no declarant
link, so the whole `COMP_CONFLICT_SAME_PERIOD` family was excluded. The linked
birth-date issue entries led to excluding `PERSON_DOB_IMPLAUSIBLE`. This is a
conservative interpretation of the public register: it avoids reselecting an
issue family when a name cannot be mapped reliably.

## Ten declarations selected for HATVP review

The sample covers implausible amounts, factor-of-ten candidates, digit-edit
candidates, and year-over-year changes. Observed values are shown exactly as
the anomaly evidence reports them; bracketed candidate values are hypotheses
from the rule and must never be treated as replacements.

| # | Declarant | Deposit date | Gold declaration UUID | Latest-name rank | Review flags and observed evidence | HATVP dossier |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | Rachida Dati | 2026-06-10 | `4fe560c3-59e0-42b5-bda6-094139aeef1e` | 1 of 3 | `COMP_IMPLAUSIBLE_AMOUNT`, 2022: `2078847.0`; `declarations.xml#/declaration[1807]/activProfCinqDerniereDto[item=1]` | [Dossier](https://www.hatvp.fr/pages_nominatives/dati-rachida) |
| 2 | Cédric Nouvelot | 2021-11-28 | `2bb7d5df-98f5-4e42-ad28-0cbf2445c9e8` | 1 of 1 | `COMP_IMPLAUSIBLE_AMOUNT`, 2020: `1047971.0`; `COMP_YOY_CHANGE`, 2021: `55332.0`; `declarations.xml#/declaration[4810]/activProfCinqDerniereDto[item=0]` | [Dossier](https://www.hatvp.fr/pages_nominatives/nouvelot-cedric-21704) |
| 3 | Valérie Alain | 2022-02-02 | `4794faad-da62-40f8-a76d-8e05539adeb8` | 1 of 2 | `COMP_IMPLAUSIBLE_AMOUNT`, 2020: `935458.0`; `declarations.xml#/declaration[36]/activProfCinqDerniereDto[item=0]` | [Dossier](https://www.hatvp.fr/pages_nominatives/alain-valerie-22889) |
| 4 | Francis Szpiner | 2024-03-04 | `46e63284-3037-44f9-bdb3-50d709a9e119` | 1 of 2 | `COMP_IMPLAUSIBLE_AMOUNT`, 2022: `733712.0`; `declarations.xml#/declaration[6057]/activProfCinqDerniereDto[item=0]` | [Dossier](https://www.hatvp.fr/pages_nominatives/szpiner-francis-26156) |
| 5 | Fabrice Geoffroy | 2026-03-16 | `89adb603-8266-4f95-b278-657cd2e72de0` | 1 of 2 | `COMP_IMPLAUSIBLE_AMOUNT`, 2022: `697734.0`; `declarations.xml#/declaration[2765]/activProfCinqDerniereDto[item=0]` | [Dossier](https://www.hatvp.fr/pages_nominatives/geoffroy-fabrice-30133) |
| 6 | Agnès Pannier-Runacher | 2026-03-17 | `39684a69-d8f3-4616-b51e-a554727f628e` | 1 of 2 | `COMP_FACTOR_ERROR`, 2024: `11024.0` (candidate `[110240.0]`); `COMP_YOY_CHANGE`, 2025: `70531.0`; `declarations.xml#/declaration[4904]/activProfCinqDerniereDto[item=1]` and `[item=4]` | [Dossier](https://www.hatvp.fr/pages_nominatives/pannier-runacher-agnes) |
| 7 | Pascal Coste | 2026-03-13 | `b7fee2e7-052b-49f8-9b4b-95ee89a81696` | 1 of 3 | `COMP_FACTOR_ERROR`, 2021: `87632.0` (candidate `[8763.2]`); `COMP_YOY_CHANGE`, 2025: `60494.0`; `declarations.xml#/declaration[1636]/activProfCinqDerniereDto[item=0]` | [Dossier](https://www.hatvp.fr/pages_nominatives/coste-pascal-2585) |
| 8 | Valérie Létard | 2026-02-23 | `549ef34f-1669-4c3f-895f-70a9a4279537` | 1 of 2 | `COMP_FACTOR_ERROR`, 2025: `91137.0` (candidate `[9113.7]`); `declarations.xml#/declaration[3962]/activProfCinqDerniereDto[item=1]` | [Dossier](https://www.hatvp.fr/pages_nominatives/letard-valerie) |
| 9 | François Hollande | 2025-01-22 | `bdff151a-af40-4ea0-98b7-cca32021f1aa` | 1 of 2 | `COMP_DIGIT_EDIT`, 2023: `21.0` (candidate `["24"]`); `COMP_FACTOR_ERROR`, 2021: `1693.0` (candidate `[169300.0]`); `declarations.xml#/declaration[3205]/activProfCinqDerniereDto[item=1]` | [Dossier](https://www.hatvp.fr/pages_nominatives/hollande-francois-27434) |
| 10 | Katja Krüger | 2022-02-15 | `6e9e510a-f18f-4c76-b68e-6e58e02a7825` | 1 of 1 | `COMP_DIGIT_EDIT`, 2021: `1400.0` (candidate `["1800"]`); `COMP_FACTOR_ERROR`, 2020: `450.0` (candidate `[4500.0]`); `declarations.xml#/declaration[3500]/activProfCinqDerniereDto[item=16]` and `[item=4]` | [Dossier](https://www.hatvp.fr/pages_nominatives/kruger-katja) |

## Recommended human follow-up

1. Open the dossier and inspect the linked XML/PDF section, including the
   surrounding activity, employer, period, and remuneration-basis fields.
2. Compare the displayed amount with the source document and with the
   declarant's immediately preceding declaration when the flag is temporal.
3. Treat factor and digit-edit candidates as possible parsing or entry-pattern
   explanations, not corrections. Treat implausible amounts as requests for
   source confirmation, not proof of an error.
4. Contact or report to HATVP only after a human confirms that the source
   evidence supports escalation. Preserve the original value and anomaly
   provenance in every case.

## Assumptions and limitations

- “Last version” is implemented by the name-based ordering documented above.
  Homonyms, spelling variants, accents, and missing names can make this a
  weaker identity key than a source person identifier.
- `previously_reported` is an internal registry lifecycle field. It is used as
  a conservative exclusion and is not evidence that HATVP has accepted or
  resolved an issue.
- The public dashboard uses hash routing; the working issue-register URL is
  `/#/quality-issues`. It showed 10 open issues and 0 solved issues at review
  time. The report explicitly documents the names and rule families excluded
  from it.
- The analysis is snapshot-specific. A later ingestion can change the latest
  declaration, anomaly lifecycle, or public issue register; rerun the SQL
  before sending a final external handoff.

## Verification evidence

- BigQuery profile: 5,026 registry rows, 5,024 linked to Gold, 1,832 active,
  and 3,194 internally previously reported.
- Exclusion-aware candidate query: 701 distinct anomaly IDs across 637 latest
  normalized name+surname pairs.
- Latest-version verification: all ten selected UUIDs returned
  `name_version_rank = 1`; their version counts are recorded in the table.
- Source-link verification: all ten have a current HATVP dossier path from the
  2026-08-19 raw CSV and a registry XML source location.
- Reported-issue verification: the live hash-routed page showed 10 open and 0
  solved issues; the linked names and generic issue families were excluded.
- Repository checks run for this documentation-only change are recorded in the
  PR and commit history.
