# Frontend bugfix deployment — 2026-09-14

## Changes and verification

- PR: https://github.com/louispaulet/YAHATVP/pull/52
- Fix commit: `38dbb3e19ec90e97c420394cdc95e5c8ccdb51c4`.
- Merged source: `08574884477c48872c1f96e3f77d5e8186f2ae10`.
- Repaired bare hash anchors that sent Explore and declaration readers to the
  not-found route; preserved query parameters and added section scroll/focus,
  including directly linked sections that load asynchronously.
- Prevented cancelled resource requests from publishing stale data or errors.
- Nine regression cases failed before the fix; the final suite has 45 passing
  frontend tests. TypeScript/Vite build passed with the existing size warning.
- Backend checks passed: 13 Worker tests, typecheck, and 48 bridge tests.
- PR workflow 34785202582 and merged-source workflow 34785229120 succeeded.
  The latter also deployed the ingestion image through the existing main workflow;
  no ingestion execution was requested for this frontend-only release.

## Publication

Ran the documented target after merge:

```sh
make frontend-deploy VITE_API_BASE_URL=https://hatvp-transparency-api.louispaulet13.workers.dev
```

- Pages commit: `d5c719a6c40af75d3eb8d3c69d356b7b91be5fb8`.
- Successful Pages run: https://github.com/louispaulet/YAHATVP/actions/runs/34880989968
- Site: https://yahatvp.thefrenchartist.dev/
- Main bundle: `assets/index-B7rT9R_h.js`.
- SHA-256: `b0e6ff861d978e3f63b33cb85c0f279cb4e9521ffaf7b218800c4d1e51031e2a`.
- The downloaded production bundle is byte-identical to the local built file.
- The custom CNAME is preserved. The bridge and Worker were not redeployed.

## Production smoke checks

The frontend and Worker `/healthz`, overview, income, assets, declarations, and
`search?q=Dupont` returned HTTP 200. All five data responses report the same
`2026-08-30` snapshot. The initial Python urllib probe received HTTP 403; the
standard curl checks and browser requests succeeded.

Live browser verification:

- Explore asset navigation retained `#/explore#asset-signals`, kept the Explore
  heading, focused `asset-signals`, and positioned it about 24px below the top.
- A source declaration opened successfully, and its miscellaneous-assets link
  retained the declaration UUID route and focused `declaration-section-bienDiverDto`.
- The skip link retained the declaration route and focused `main-content`.
- No browser console warnings or errors occurred.

Local responsive verification covered French Explore at 1440×1024, 1024×768,
390×844, and 320×844, with no page-level overflow. Declaration sections were
also inspected at tablet and mobile sizes. See frontend/design-qa.md for the
original reproduction and fixture coverage.
