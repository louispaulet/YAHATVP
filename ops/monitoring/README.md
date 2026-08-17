# HATVP monitoring and retention runbook

This runbook configures the operational safeguards for the production HATVP
pipeline. It is intentionally `gcloud`-based and uses explicit project and
resource variables so a local default project cannot receive the changes.

The production resources are:

```bash
export PROJECT_ID="yahatvp-pipeline-eu"
export REGION="europe-west1"
export JOB_NAME="hatvp-ingestion"
: "${NOTIFICATION_EMAIL:?Set NOTIFICATION_EMAIL to the verified operator address}"
```

Do not commit credentials, access tokens, notification-channel IDs, or local
configuration files. Use ADC for local Google Cloud access.

## 1. Verify retention and audit-log routing

The accepted baseline is 400 days and locked for the system `_Required` audit
bucket, and 30 days for the system `_Default` application bucket. These are
read-only checks; do not change either bucket as part of this runbook.

```bash
gcloud logging buckets describe _Required \
  --project="$PROJECT_ID" \
  --location=global \
  --format='yaml(name,retentionDays,locked,description)'

gcloud logging buckets describe _Default \
  --project="$PROJECT_ID" \
  --location=global \
  --format='yaml(name,retentionDays,locked,description)'

gcloud logging sinks list \
  --project="$PROJECT_ID" \
  --format='table(name,destination,filter)'

gcloud projects get-iam-policy "$PROJECT_ID" \
  --format='yaml(auditConfigs)'
```

Acceptance requires:

- `_Required` reports `retentionDays: 400`, `locked: true`, and the required
  Admin Activity/System Event audit-log routing.
- `_Default` reports `retentionDays: 30` and stores application logs.
- No retention mutation is needed unless the accepted baseline changes.

## 2. Create or reuse the email notification channel

Notification channels are managed by the Cloud Monitoring beta command group.
Install that optional command group locally if it is not already available:

```bash
gcloud components install beta
```

List existing email channels first. Reuse the channel with the exact target
address when present:

```bash
gcloud beta monitoring channels list \
  --project="$PROJECT_ID" \
  --filter="type=email AND labels.email_address=$NOTIFICATION_EMAIL" \
  --format='table(name,displayName,type,enabled,labels.email_address)'
```

If no matching channel exists, create one:

```bash
gcloud beta monitoring channels create \
  --project="$PROJECT_ID" \
  --display-name="HATVP operational alerts" \
  --description="Email notifications for HATVP Cloud Run and quality alerts" \
  --type=email \
  --channel-labels="email_address=$NOTIFICATION_EMAIL"
```

Set the channel resource name for the policy commands:

```bash
export CHANNEL_NAME="$(gcloud beta monitoring channels list \
  --project="$PROJECT_ID" \
  --filter="type=email AND labels.email_address=$NOTIFICATION_EMAIL" \
  --format='value(name)' | head -n 1)"

test -n "$CHANNEL_NAME"
echo "$CHANNEL_NAME"
```

Confirm the test notification in the Cloud Monitoring Alerting page and verify
receipt at `NOTIFICATION_EMAIL` before considering the channel validated.

## 3. Create or update the alert policies

The manifests are kept in `ops/monitoring/policies/`. The helper below makes
policy application idempotent by updating a policy with the same display name
instead of creating a duplicate.

```bash
apply_policy() {
  local policy_file="$1"
  local display_name
  local policy_name

  display_name="$(python -c 'import json, sys; print(json.load(open(sys.argv[1]))["displayName"])' "$policy_file")"
  policy_name="$(gcloud monitoring policies list \
    --project="$PROJECT_ID" \
    --filter="displayName=\"$display_name\"" \
    --format='value(name)' | head -n 1)"

  if [ -n "$policy_name" ]; then
    gcloud monitoring policies update "$policy_name" \
      --project="$PROJECT_ID" \
      --policy-from-file="$policy_file" \
      --set-notification-channels="$CHANNEL_NAME"
  else
    gcloud monitoring policies create \
      --project="$PROJECT_ID" \
      --policy-from-file="$policy_file" \
      --notification-channels="$CHANNEL_NAME"
  fi
}

apply_policy ops/monitoring/policies/failed-execution.json
apply_policy ops/monitoring/policies/warning-streak.json
apply_policy ops/monitoring/policies/flagged-record-regression.json
```

The failed-execution policy uses the Cloud Run metric
`run.googleapis.com/job/completed_execution_count` with
`metric.labels.result="failed"`. The two quality policies match the structured
`quality_warning_streak` and `quality_regression` events emitted by the
pipeline.

Verify the policies and their notification channel:

```bash
gcloud monitoring policies list \
  --project="$PROJECT_ID" \
  --filter='userLabels.service=hatvp' \
  --format='table(name,displayName,enabled)'

FAILED_POLICY_NAME="$(gcloud monitoring policies list \
  --project="$PROJECT_ID" \
  --filter='displayName="HATVP ingestion failed execution"' \
  --format='value(name)' | head -n 1)"
gcloud monitoring policies describe "$FAILED_POLICY_NAME" \
  --format='yaml(displayName,enabled,conditions,notificationChannels)'
```

Repeat `describe` for the two quality policy display names and confirm each
policy has the expected filter and the email channel resource name.

## 4. Verify pipeline telemetry

After the merged image is deployed, inspect structured events directly:

```bash
gcloud logging read \
  'resource.type="cloud_run_job" AND resource.labels.job_name="hatvp-ingestion" AND (jsonPayload.event="quality_warning_streak" OR jsonPayload.event="quality_regression")' \
  --project="$PROJECT_ID" \
  --limit=20 \
  --format=json
```

The first successful warning-bearing snapshot has `warning_streak=1`. A second
consecutive warning-bearing snapshot emits `quality_warning_streak` and can
open the repeated-warning incident. `quality_regression` is emitted only when
flagged records increase by more than 10% from the prior successful report.
First snapshots, failed prior reports, and `NO_CHANGE` runs do not emit either
quality alert event.

Inspect the Cloud Run metric and job configuration when validating the failed
execution policy:

```bash
gcloud run jobs describe "$JOB_NAME" \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --format='yaml(metadata.name,spec.template.spec.template.spec.containers)'

gcloud run jobs executions list \
  --project="$PROJECT_ID" \
  --job="$JOB_NAME" \
  --region="$REGION" \
  --limit=10 \
  --format='table(name,createTime,completionTime,conditions[0].state)'
```

## Rollback

Disable an alert without changing the pipeline or retention settings:

```bash
gcloud monitoring policies update POLICY_NAME \
  --project="$PROJECT_ID" \
  --no-enabled
```

Delete a notification channel only after removing it from every policy. Never
delete or shorten the immutable raw archive, and never change the accepted log
retention baseline as part of alert rollback.
