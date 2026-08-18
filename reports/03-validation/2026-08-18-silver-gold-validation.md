# Silver and Gold validation — 2026-08-18

## Scope

This validation covers the explicit Bronze → Silver → Gold local pipeline, the
deterministic anomaly registry, and the dashboard bridge's Gold read contract.
The live run used the current HATVP CSV and XML sources with
`--local-output /tmp/yahatvp-e2e.8S1D3J --force`; no cloud credentials or live
BigQuery writes were required.

## Live forced run

The run completed with `SUCCESS_WITH_WARNINGS`, exit code 0, and zero quality
errors. The exact downloaded source hashes were:

| Source | Bytes | SHA-256 |
| --- | ---: | --- |
| `liste.csv` | 3,312,738 | `156463f08b88dd884dcbb0721d9295869c8df7595cf98696162030123938dd29` |
| `declarations.xml` | 88,825,812 | `865261857f88ec6c262558bc115b37b94f97ea3418b6829267aa6cbd1458fdaf` |

The snapshot contained 6,611 declarations and people, 74,791 income rows,
1,157 assets, and 5,818 quality-flagged records. The resulting local Parquet
counts were:

| Layer | Declarations | People | Incomes | Assets |
| --- | ---: | ---: | ---: | ---: |
| Bronze | 6,611 | 6,611 | 74,791 | 1,157 |
| Silver | 6,611 | 6,611 | 74,791 | 1,157 |
| Gold | 6,605 | 6,605 | 74,730 | 1,157 |

The registry contained 3,042 deterministic anomaly records. `state/latest.json`
was written only after all four layer families and the registry were present;
its stored source hashes match the table above.

## Replay and website checks

- A forced fixture replay writes raw, Bronze, Silver, Gold, and registry
  partitions and produces byte-identical Parquet/state fingerprints on retry.
- The unchanged live replay returned `NO_CHANGE` and left the derived snapshot
  and latest state untouched.
- Python unit suite: 140 tests pass, including the anomaly fixtures and module
  line-budget invariant.
- Bridge fixture suite: 31 tests pass; all current dashboard query paths point
  to Gold tables and keep historical anomalies outside current metrics.
- Frontend suite: 18 tests pass; TypeScript/Vite production build passes.
- Worker suite: 8 tests pass and TypeScript typecheck passes.

Historical Silver/registry backfill is implemented by reading every retained
Bronze partition through the artifact-store listing contract. It preserves
prior raw/source evidence and deduplicates only retry copies with the same
stable source occurrence key; repeated UUID occurrences remain separate.
