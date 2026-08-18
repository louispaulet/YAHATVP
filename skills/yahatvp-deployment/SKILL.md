---
name: yahatvp-deployment
description: Deploy and release the YAHATVP ingestion pipeline and transparency dashboard from this repository, including Cloud Run, Cloudflare Worker, GitHub Pages, smoke tests, changelog evidence, and version tags.
metadata:
  short-description: Deploy and release YAHATVP safely
---

# YAHATVP deployment

Use this skill only when the user explicitly authorizes a deployment, release,
or production smoke test for this repository. The repository's `agents.md`,
`README.md`, `TODO.md`, and `CHANGELOG.md` remain authoritative; read them
before acting. Preserve unrelated working-tree changes.

## Preflight

1. Check `git status --short --branch` and inspect any local changes.
2. Pull the requested branch with `git pull --ff-only origin main` only when
   the working tree can safely accept it.
3. Run the dashboard checks before changing production state:

   ```bash
   make backend-test
   make frontend-test
   ```

   For a pipeline code change, also run `uv run pytest`, Ruff, `uv build`, and
   the narrowest relevant tests locally. The GitHub Actions workflow is the
   final pipeline test and deployment gate.
4. Confirm the intended project and sessions without printing secrets:

   ```bash
   gcloud config get-value project
   gcloud auth list --filter=status:ACTIVE
   (cd website/hatvp-transparency-dashboard/backend/worker && npx wrangler whoami)
   ```

   Use ADC, Workload Identity Federation, and the existing Wrangler login.
   Never create or request a long-lived service-account JSON key.

## Dashboard deployment

The dashboard backend is the Cloud Run bridge followed by the Cloudflare
Worker. The frontend is the Vite build published to GitHub Pages.

1. Deploy the bridge and Worker:

   ```bash
   make backend-deploy
   ```

   This target grants or reuses the read-only bridge service account, deploys
   `hatvp-dashboard-api`, resolves its URL, and deploys
   `hatvp-transparency-api`. Record the Cloud Run revision and Worker version
   printed by the commands.
2. Publish the frontend using the Worker URL printed by Wrangler:

   ```bash
   make frontend-deploy \
     VITE_API_BASE_URL="https://hatvp-transparency-api.louispaulet13.workers.dev"
   ```

   Do not rotate `BRIDGE_TOKEN` as part of an ordinary deployment. Use
   `make backend-secrets` only when the user explicitly requests secret
   rotation and provides a token through the environment.

## Ingestion and Gold data

The `main` push workflow builds and deploys the ingestion image to the
`hatvp-ingestion` Cloud Run Job. It must keep the production job at 4 GiB;
the Silver/Gold build can exceed the former 2 GiB limit. Wait for the workflow
test and deploy jobs to succeed before executing the job.

After analytical-layer code or a fresh production image is deployed, run one
forced replay when Gold data must be materialized:

```bash
gcloud run jobs execute hatvp-ingestion \
  --project=yahatvp-pipeline-eu \
  --region=europe-west1 \
  --args=--force \
  --wait
```

Never overlap forced replays or start one while another execution is still
running. The loader uses shared `_hatvp_staging_*` BigQuery table names, so
overlapping executions can delete each other's staging tables and fail. If an
execution is stuck or failed, inspect it before retrying:

```bash
gcloud run jobs executions list \
  --job=hatvp-ingestion --project=yahatvp-pipeline-eu \
  --region=europe-west1 --limit=5
```

Require a successful execution status (`SUCCESS` or
`SUCCESS_WITH_WARNINGS`) and confirm the logs include `bigquery_load_complete`
for Bronze, Silver, Gold, and `anomaly_registry` before calling the release
ready.

## Smoke test

Check the deployed Worker and custom domain. The health route is `/healthz`,
not `/health`:

```bash
WORKER_URL="https://hatvp-transparency-api.louispaulet13.workers.dev"
FRONTEND_URL="https://yahatvp.thefrenchartist.dev"

for route in \
  healthz \
  api/dashboard/overview \
  api/dashboard/income \
  api/dashboard/assets \
  api/dashboard/declarations \
  'api/dashboard/search?q=Dupont'; do
  curl --fail --silent --show-error \
    "$WORKER_URL/$route" >/dev/null
done
curl --fail --silent --show-error "$FRONTEND_URL/" >/dev/null
```

The slice responses should contain the same latest `snapshotDate`. If a
dashboard slice returns 502, inspect Gold-table existence and the Cloud Run
bridge logs; do not tag the release while public routes are failing.

## Changelog, commit, and tag

After deployment and smoke testing, append a dated `CHANGELOG.md` entry with
the deployed Cloud Run revision, Worker version, frontend URL, CI workflow run,
forced execution name/status, and meaningful layer counts or HTTP evidence.

Then follow the repository's required change workflow:

```bash
git diff --check
git add <intentional-files>
git commit -m "<focused message>"
git push origin main
git tag -a vX.Y -m "YAHATVP vX.Y"
git push origin vX.Y
```

Tag only the verified commit after `main` is pushed and the deployment
workflow is green. Do not force-push, rewrite history, or create a release tag
when CI, the forced replay, or any smoke-test route is failing. Report the
exact external blocker instead.
