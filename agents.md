# Agent instructions

Read this file before making changes in this repository.

## Website design system

Before changing anything under `website/hatvp-transparency-dashboard/frontend`,
read the repository-level [design_style.md](design_style.md). It is the
canonical visual and interaction guide for the dashboard: follow its tokens,
typography, responsive rules, reusable component patterns, data-visualization
conventions, loading behavior, accessibility requirements, and bilingual
content rules. Update `design_style.md` when a website change introduces a
new shared visual pattern or token.

## Required workflow

After every change, always:

1. inspect the diff and run the relevant tests/checks;
2. stage the intentional files;
3. create a focused commit;
4. push the commit to the current remote branch.

This rule applies even when the current branch is `main`. Do not leave completed
changes uncommitted or unpushed. Never force-push or rewrite history unless the
user explicitly asks for it. If authentication, branch protection, or a remote
failure prevents the push, report the exact blocker instead of pretending the
change is complete.

## Project direction

- Follow `README.md` as the architecture and operational contract.
- Keep the pipeline small and HATVP-specific; do not introduce an orchestrator.
- Inspect the current HATVP CSV/XML schema before inventing normalized fields.
- Preserve immutable raw bytes, source identifiers, and provenance.
- Update `state/latest.json` only after every required processing stage succeeds.
- Flag suspicious records for review; do not silently delete or “correct” them.
- Use fixtures for normal tests. Tests must not require live HATVP, GCS, or
  BigQuery access.
- Use Application Default Credentials locally, the Cloud Run runtime service
  account in production, and GitHub Workload Identity Federation in CI/CD.
- Never create, commit, or request long-lived service-account JSON keys.

## Before editing

- Check `git status --short --branch` and preserve unrelated user changes.
- Read `agents.md`, `TODO.md`, and `CHANGELOG.md` before starting work. If
  `CHANGELOG.md` is missing, create it as part of the repository documentation
  update.
- Read the relevant source, tests, and documentation before modifying them.
- Prefer `rg` for repository searches.
- Avoid destructive commands and broad rewrites.

## Project tracking

- Treat `TODO.md` as the current execution plan. Reconcile its checkboxes and
  remaining work with the actual result of every repository, infrastructure,
  CI/CD, or operational change.
- Append a dated entry to `CHANGELOG.md` for completed user-visible,
  infrastructure, CI/CD, and operational changes. Include the important
  verification evidence and leave unresolved follow-up work in `TODO.md`.
- Do not mark work complete based only on configuration; record a successful
  test, deployment, or smoke-test result when one is required.

## Before committing

- Review `git diff` and confirm no secrets or generated data are included.
- Run the narrowest relevant tests first, then the full project checks when the
  implementation supports them.
- Use a concise commit message describing the change.
- Push to the current branch, including `main`, as required above.

## Google Cloud access

No GCloud login is needed for documentation changes, fixture-only tests, or
local-output mode. ADC login is needed for local GCS/BigQuery integration, and
Google Cloud permissions are needed for deployment. Ask the user for access or
configuration details only when an operation genuinely requires them; never ask
for service-account JSON credentials.
