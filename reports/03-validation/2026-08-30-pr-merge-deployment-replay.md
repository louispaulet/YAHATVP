# 2026-08-30 PR merge, deployment, and forced replay

## Scope

`main` was fast-forwarded from `origin/main` before the merge train. Six open,
non-draft PRs were merged in order: #46, #47, #48, #49, #50, and #51. The
working tree was clean before and after the operation, and no frontend,
dashboard Worker, or bridge files were changed.

## Merge record

| PR | Merge commit | Modified elements | Conflict handling |
| --- | --- | --- | --- |
| #46 | `6692f2c` | `src/hatvp/layers/gold.py`; `tests/test_layers.py`; tracking docs | Clean merge; focused layer tests and Ruff passed. |
| #47 | `06a17d6` | `src/hatvp/pipeline/orchestrator.py`; `tests/test_pipeline_orchestrator.py`; tracking docs | `CHANGELOG.md` conflict resolved on the PR branch in `635e3f7`; full PR CI passed. |
| #48 | `cb6fcd3` | `src/hatvp/download/validation.py`; `tests/test_download.py`; tracking docs | `CHANGELOG.md` conflict resolved on the PR branch in `7af81c2`; full PR CI passed. |
| #49 | `be73600` | `src/hatvp/parser/declaration_support.py`; `tests/fixtures/whitespace_income.xml`; `tests/test_parser_structure.py`; tracking docs | Clean merge; focused parser tests and Ruff passed. |
| #50 | `113eb86` | `src/hatvp/layers/history.py`; `tests/test_layers_history.py`; tracking docs | `CHANGELOG.md` and `TODO.md` conflicts resolved on the PR branch in `4f5c6a2`; full PR CI passed. |
| #51 | `5352965` | `src/hatvp/layers/silver.py`; `src/hatvp/pipeline/flow.py`; `src/hatvp/pipeline/legacy.py`; `src/hatvp/pipeline/processing.py`; `tests/test_anomaly_regressions.py`; tracking docs | `CHANGELOG.md` conflict resolved on the PR branch in `fb9085d`; full PR CI passed. |

The combined merge range changed 18 tracked files: the eleven pipeline/parser/
download implementation files above, six regression/fixture files, and
`TODO.md`/`CHANGELOG.md`.

## Verification and deployment

- Local verification on `5352965`: Ruff check, Ruff format check, package build,
  and all 183 tests passed.
- Main workflow `33285643477` passed test, deployment-config, image build/push,
  and Cloud Run Job deployment for image
  `europe-west1-docker.pkg.dev/yahatvp-pipeline-eu/hatvp/hatvp:5352965`.
- Cloud Run Job `hatvp-ingestion` was verified with BigQuery enabled, the
  expected HATVP bucket/dataset, and the normal 1 CPU / 4 GiB / 30-minute
  scheduled profile after deployment. No frontend, Worker, or bridge redeploy
  was warranted because no files in those components changed.

## Forced production replay

The replay was warranted because the merged code changes source acceptance,
source-set short-circuiting, income normalization, DOB anomaly thresholds,
legacy-history materialization, and Gold eligibility. The first all-stage
`--force` execution, `hatvp-ingestion-grhrr`, reached the task but failed at the
4 GiB memory limit. The job was temporarily updated to 8 CPU / 32 GiB, and the
same all-stage `--force` replay was retried as `hatvp-ingestion-qhb9x`.

The retry completed successfully in 12m51.96s with `SUCCESS_WITH_WARNINGS`:

- BigQuery loading completed for all 13 Bronze, Silver, Gold, and anomaly
  registry tables.
- The quality report for snapshot `2026-08-30` records zero errors, zero
  catastrophic row-count reductions, 58,502 flagged records, 41,201 warnings,
  and `quality_regression: false`.
- `state/latest.json` advanced only after completion to snapshot `2026-08-30`
  with pipeline SHA/version `53529654c477df66dda4e4249dd349ce8c394450`.
- The temporary job profile was restored to 1 CPU / 4 GiB with the final image
  and environment unchanged.

Source hashes in the resulting state remain the exact-byte identifiers for the
official, GitHub/Wayback, and Hugging Face/Wayback sources; no source data was
silently corrected or deleted.
