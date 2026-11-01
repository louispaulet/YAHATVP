# Artifact Registry cleanup record

**Date:** 2026-11-01  
**Project:** `yahatvp-pipeline-eu`  
**Region:** `europe-west1`  
**Outcome:** Old image versions were deleted and retention policies are active. Physical layer reclamation has not yet been confirmed.

## Before and after

Repository sizes are as reported by `gcloud artifacts repositories describe`.
The shared `cloud-run-source-deploy` size includes both the dashboard API and
Nitter packages. The latest snapshot includes the documentation-only build and
the one-time build triggered by changing the workflow filter.

| Scope | Before purge | Immediately after version purge | After docs build (`95f951a`) | After filter deployment (`97fe99f`) |
| --- | ---: | ---: | ---: | ---: |
| `hatvp` repository size | 37,137.229 MB | 37,136.854 MB | 37,327.190 MB | 37,517.529 MB |
| `hatvp/hatvp` versions | 205 | 10 | 13 | 16 |
| `cloud-run-source-deploy` repository size | 1,261.772 MB | 1,261.704 MB | 1,261.704 MB | 1,261.704 MB |
| `hatvp-dashboard-api` versions | 37 | 3 | 3 | 3 |
| `my-nitter_nitter` versions | 4 | 4 | 4 | 4 |

The manual purge removed **195 pipeline versions** and **34 dashboard API
versions**. The immediate repository-size change was only 0.375 MB for `hatvp`
and 0.068 MB for `cloud-run-source-deploy`; those figures do not represent the
expected final storage savings because Artifact Registry removes unreferenced
container layers during daily garbage collection. See Google's [image deletion
documentation](https://docs.cloud.google.com/artifact-registry/docs/docker/manage-images).

## What was retained

At the time of the purge, `hatvp/hatvp` retained the three newest `main` builds
(`27530ef`, `1cb94d4`, and `ee5c54f`), represented by nine registry records
(index, runnable manifest, and attestation per build), plus `baa27d8`, which is
still referenced by `hatvp-scheduler-smoke`. The dashboard API retained its
three newest versions, including the digest used by the live service. All four
`my-nitter_nitter` versions and the running Nitter image were left untouched.

After the purge, commit `95f951a` added only project documentation, but the
`Test and deploy` workflow ran anyway. GitHub Actions run
[41331036755](https://github.com/louispaulet/YAHATVP/actions/runs/41331036755)
built and deployed `hatvp:95f951a`; this added three pipeline registry records
and the latest measured `hatvp` size rose by 190.336 MB from the immediate
post-purge reading. The ingestion job now references that image. There was no
pipeline execution as part of this deploy.

To prevent repeats, the deployment workflow now ignores pushes limited to the
listed tracking documents, reports, and Markdown paths outside the image build
inputs. The workflow change itself triggered one expected final build and
deployment: run
[41336949571](https://github.com/louispaulet/YAHATVP/actions/runs/41336949571)
passed tests, deployment configuration, and deployment, producing
`hatvp:97fe99f`. This added another three registry records and 190.339 MB to the
reported `hatvp` size. The ingestion job now references that image; no pipeline
execution was started by the deployment.

At the latest check, 16 pipeline versions represent five recent build groups
plus the smoke image. The two oldest recent groups are under one day old, so the
active cleanup policy's one-day deletion threshold has not made them eligible.
After they age out, the policy should retain the nine records for the three
newest builds (`97fe99f`, `95f951a`, and `27530ef`) plus the smoke tag.

## Cause and prevention

Older pipeline and dashboard API images had accumulated because no effective
retention policy was cleaning them up. Each pipeline build produces several
registry version records, and stored image layers dominate repository size.
Deleting manifests and tags does not immediately reclaim unreferenced layer
storage.

The following controls are now in place:

1. The `hatvp` repository deletes versions older than one day, keeps the nine
   most recent records for `hatvp` (three builds at the current output shape),
   and separately keeps the `baa27d8` smoke-job image.
2. The shared repository deletes old `hatvp-dashboard-api` versions after one
   day and keeps its three most recent versions. No Nitter package is targeted.
3. The deployment workflow skips pushes that change only tracking documents,
   reports, and the listed Markdown paths outside the image build inputs.
   Pull-request checks remain enabled, and `README.md` remains a push trigger
   because the Dockerfile copies it into the image. The workflow-filter change
   itself is expected to run once because it changes a non-ignored workflow
   file; future commits limited to the ignored docs will not build an image.
   Docs-only commit `acc9f96` created no Actions run, confirming the filter.
4. After the one-day retention window and daily layer collection, compare the
   repository sizes and retained tags again. The remaining check is tracked in
   [`TODO.md`](../../TODO.md).

Artifact Registry's [cleanup policy guide](https://docs.cloud.google.com/artifact-registry/docs/repositories/cleanup-policy-overview)
explains how keep and delete rules are combined.

## Verification commands

```sh
gcloud artifacts repositories describe hatvp --location=europe-west1
gcloud artifacts versions list --location=europe-west1 --repository=hatvp --package=hatvp
gcloud artifacts repositories describe cloud-run-source-deploy --location=europe-west1
gcloud artifacts versions list --location=europe-west1 --repository=cloud-run-source-deploy --package=hatvp-dashboard-api
gcloud artifacts versions list --location=europe-west1 --repository=cloud-run-source-deploy --package=my-nitter_nitter
```

The active image references were checked after the purge: the ingestion job,
smoke job, dashboard API service, and Nitter service all pointed to retained
versions. See the live follow-up in `TODO.md` for the post-GC size check.
