SHELL := /bin/sh

DASHBOARD_DIR := website/hatvp-transparency-dashboard
BACKEND_DIR := $(DASHBOARD_DIR)/backend
WORKER_DIR := $(BACKEND_DIR)/worker
BRIDGE_DIR := $(BACKEND_DIR)/bigquery-bridge
FRONTEND_DIR := $(DASHBOARD_DIR)/frontend

GCP_PROJECT_ID ?= yahatvp-pipeline-eu
GCP_REGION ?= europe-west1
BQ_DATASET ?= hatvp
BRIDGE_SERVICE ?= hatvp-dashboard-api
BRIDGE_SECRET_NAME ?= hatvp-dashboard-bridge-token
READER_SERVICE_ACCOUNT ?= hatvp-dashboard-reader
FRONTEND_ORIGIN ?= https://yahatvp.thefrenchartist.dev

.PHONY: dashboard-install backend-test backend-dev backend-secrets bridge-deploy backend-deploy frontend-test frontend-dev frontend-deploy

dashboard-install:
	npm --prefix $(WORKER_DIR) install
	npm --prefix $(FRONTEND_DIR) install

backend-test:
	npm --prefix $(WORKER_DIR) run test
	npm --prefix $(WORKER_DIR) run typecheck
	uv run pytest $(BRIDGE_DIR)/test_*.py

backend-dev:
	cd $(WORKER_DIR) && npm run dev

backend-secrets:
	@test -n "$$BRIDGE_TOKEN" || (echo "Set BRIDGE_TOKEN before rotating dashboard secrets." >&2; exit 1)
	@if ! gcloud secrets describe "$(BRIDGE_SECRET_NAME)" --project="$(GCP_PROJECT_ID)" >/dev/null 2>&1; then \
		gcloud secrets create "$(BRIDGE_SECRET_NAME)" --project="$(GCP_PROJECT_ID)" --replication-policy=automatic; \
	fi
	printf '%s' "$$BRIDGE_TOKEN" | gcloud secrets versions add "$(BRIDGE_SECRET_NAME)" --project="$(GCP_PROJECT_ID)" --data-file=-
	cd $(WORKER_DIR) && printf '%s' "$$BRIDGE_TOKEN" | npx wrangler secret put BRIDGE_TOKEN

bridge-deploy:
	@if ! gcloud iam service-accounts describe "$(READER_SERVICE_ACCOUNT)@$(GCP_PROJECT_ID).iam.gserviceaccount.com" --project="$(GCP_PROJECT_ID)" >/dev/null 2>&1; then \
		gcloud iam service-accounts create "$(READER_SERVICE_ACCOUNT)" --project="$(GCP_PROJECT_ID)" --display-name="HATVP dashboard BigQuery reader"; \
	fi
	gcloud projects add-iam-policy-binding "$(GCP_PROJECT_ID)" --member="serviceAccount:$(READER_SERVICE_ACCOUNT)@$(GCP_PROJECT_ID).iam.gserviceaccount.com" --role="roles/bigquery.jobUser" --quiet >/dev/null
	bq --project_id="$(GCP_PROJECT_ID)" --location="$(GCP_REGION)" query --use_legacy_sql=false --quiet "GRANT \`roles/bigquery.dataViewer\` ON SCHEMA \`$(GCP_PROJECT_ID).$(BQ_DATASET)\` TO \"serviceAccount:$(READER_SERVICE_ACCOUNT)@$(GCP_PROJECT_ID).iam.gserviceaccount.com\""
	gcloud secrets add-iam-policy-binding "$(BRIDGE_SECRET_NAME)" --project="$(GCP_PROJECT_ID)" --member="serviceAccount:$(READER_SERVICE_ACCOUNT)@$(GCP_PROJECT_ID).iam.gserviceaccount.com" --role="roles/secretmanager.secretAccessor" --quiet >/dev/null
	gcloud run deploy "$(BRIDGE_SERVICE)" --source="$(BRIDGE_DIR)" --project="$(GCP_PROJECT_ID)" --region="$(GCP_REGION)" --service-account="$(READER_SERVICE_ACCOUNT)@$(GCP_PROJECT_ID).iam.gserviceaccount.com" --allow-unauthenticated --memory=512Mi --set-env-vars="BQ_PROJECT_ID=$(GCP_PROJECT_ID),BQ_DATASET=$(BQ_DATASET),BQ_LOCATION=$(GCP_REGION)" --set-secrets="BRIDGE_TOKEN=$(BRIDGE_SECRET_NAME):latest"

backend-deploy: bridge-deploy
	@BRIDGE_URL="$$(gcloud run services describe "$(BRIDGE_SERVICE)" --project="$(GCP_PROJECT_ID)" --region="$(GCP_REGION)" --format='value(status.url)')"; \
		test -n "$$BRIDGE_URL" || (echo "Could not resolve the deployed bridge URL." >&2; exit 1); \
		cd $(WORKER_DIR) && npx wrangler deploy --var "BRIDGE_URL:$$BRIDGE_URL" --var "FRONTEND_ORIGIN:$(FRONTEND_ORIGIN)"

frontend-test:
	env -u VITE_API_BASE_URL npm --prefix $(FRONTEND_DIR) run test
	npm --prefix $(FRONTEND_DIR) run build

frontend-dev:
	npm --prefix $(FRONTEND_DIR) run dev

frontend-deploy:
	@test -n "$(VITE_API_BASE_URL)" || (echo "Set VITE_API_BASE_URL to the deployed Worker URL before publishing." >&2; exit 1)
	env -u VITE_API_BASE_URL npm --prefix $(FRONTEND_DIR) run test
	VITE_API_BASE_URL="$(VITE_API_BASE_URL)" npm --prefix $(FRONTEND_DIR) run build
	VITE_API_BASE_URL="$(VITE_API_BASE_URL)" npm --prefix $(FRONTEND_DIR) run deploy
