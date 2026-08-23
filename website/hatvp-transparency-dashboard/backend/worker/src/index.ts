import type {
  DashboardBreakdownResponse,
  DashboardDeclarationResponse,
  AgeAnalysisResponse,
  SimpleAnalysisResponse,
  DashboardOverviewResponse,
  DashboardSearchResponse,
  DashboardGenderResponse,
  DashboardHealthResponse,
  DashboardHighlightsResponse,
  WorkerEnv,
} from "./types";

const HEALTH_PATH = "/healthz";
const CACHE_CONTROL = "public, max-age=300, s-maxage=600";
const DASHBOARD_SLICE_ROUTES = {
  "/api/dashboard/overview": "/v1/dashboard/overview",
  "/api/dashboard/income": "/v1/dashboard/income",
  "/api/dashboard/assets": "/v1/dashboard/assets",
  "/api/dashboard/declarations": "/v1/dashboard/declarations",
  "/api/dashboard/gender": "/v1/dashboard/gender",
  "/api/dashboard/highlights": "/v1/dashboard/highlights",
  "/api/dashboard/health": "/v1/dashboard/health",
  "/api/dashboard/search": "/v1/dashboard/search",
  "/api/dashboard/simple-analysis": "/v1/dashboard/simple-analysis",
  "/api/dashboard/age-analysis": "/v1/dashboard/age-analysis",
} as const;
const DASHBOARD_DECLARATION_PREFIX = "/api/dashboard/declarations/";

type Fetcher = typeof fetch;

function allowedOrigins(configured: string): Set<string> {
  return new Set(configured.split(",").map((origin) => origin.trim()).filter(Boolean));
}

function corsHeaders(request: Request, env: WorkerEnv): Headers {
  const headers = new Headers();
  const origin = request.headers.get("Origin");
  if (origin && allowedOrigins(env.FRONTEND_ORIGIN).has(origin)) {
    headers.set("Access-Control-Allow-Origin", origin);
    headers.set("Vary", "Origin");
  }
  headers.set("Access-Control-Allow-Methods", "GET, OPTIONS");
  headers.set("Access-Control-Allow-Headers", "Content-Type");
  return headers;
}

function jsonResponse(
  request: Request,
  env: WorkerEnv,
  payload: unknown,
  status = 200,
  extraHeaders: HeadersInit = {},
): Response {
  const headers = corsHeaders(request, env);
  headers.set("Content-Type", "application/json; charset=utf-8");
  for (const [key, value] of Object.entries(extraHeaders)) headers.set(key, value);
  return new Response(JSON.stringify(payload), { status, headers });
}

function errorPayload(code: string, message: string): { error: { code: string; message: string } } {
  return { error: { code, message } };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isDashboardOverviewResponse(value: unknown): value is DashboardOverviewResponse {
  if (!isRecord(value) || typeof value.generatedAt !== "string") return false;
  if (!(value.snapshotDate === null || typeof value.snapshotDate === "string")) return false;
  const tables = value.tables;
  return isRecord(tables) && ["declarations", "people", "incomes", "assets"].every(
    (name) => typeof tables[name] === "number",
  );
}

function isDashboardHealthResponse(value: unknown): value is DashboardHealthResponse {
  if (!isRecord(value) || typeof value.generatedAt !== "string" || typeof value.nextIngestionAt !== "string") return false;
  const quality = value.quality;
  return (value.snapshotDate === null || typeof value.snapshotDate === "string")
    && Array.isArray(value.sources) && Array.isArray(value.layers) && Array.isArray(value.anomalies)
    && isRecord(quality) && typeof quality.errors === "number" && typeof quality.warnings === "number"
    && typeof quality.flaggedRecords === "number" && typeof quality.regression === "boolean"
    && value.sources.every((item) => isRecord(item) && typeof item.sourceId === "string" && typeof item.declarations === "number")
    && value.layers.every((item) => isRecord(item) && typeof item.layer === "string" && typeof item.rows === "number" && typeof item.reviewRows === "number")
    && value.anomalies.every((item) => isRecord(item) && typeof item.status === "string" && typeof item.rows === "number");
}

function isDashboardBreakdownResponse(value: unknown): value is DashboardBreakdownResponse {
  if (!isRecord(value) || typeof value.generatedAt !== "string") return false;
  if (!(value.snapshotDate === null || typeof value.snapshotDate === "string")) return false;
  return Array.isArray(value.items);
}

function isDashboardGenderResponse(value: unknown): value is DashboardGenderResponse {
  if (!isRecord(value) || typeof value.generatedAt !== "string") return false;
  if (!(value.snapshotDate === null || typeof value.snapshotDate === "string")) return false;
  return Array.isArray(value.gender) && typeof value.unknownRows === "number" && Array.isArray(value.positions);
}

function isDashboardSearchResponse(value: unknown): value is DashboardSearchResponse {
  if (!isRecord(value) || typeof value.generatedAt !== "string") return false;
  if (!(value.snapshotDate === null || typeof value.snapshotDate === "string")) return false;
  return Array.isArray(value.results) && typeof value.resultCount === "number";
}

function isDashboardHighlightsResponse(value: unknown): value is DashboardHighlightsResponse {
  if (!isRecord(value) || typeof value.generatedAt !== "string") return false;
  if (!(value.snapshotDate === null || typeof value.snapshotDate === "string")) return false;
  return Array.isArray(value.incomeChanges) && Array.isArray(value.unusualAssets)
    && Array.isArray(value.amendedRecords)
    && value.incomeChanges.every((item) => isRecord(item)
      && typeof item.absoluteChange === "number" && typeof item.reviewRequired === "boolean")
    && value.unusualAssets.every((item) => isRecord(item)
      && typeof item.amount === "number" && typeof item.reviewRequired === "boolean")
    && value.amendedRecords.every((item) => isRecord(item)
      && typeof item.filingCount === "number" && typeof item.amendedCount === "number");
}

function isDashboardDeclarationResponse(value: unknown): value is DashboardDeclarationResponse {
  if (!isRecord(value) || typeof value.generatedAt !== "string" || typeof value.rawXml !== "string") return false;
  if (!(value.snapshotDate === null || typeof value.snapshotDate === "string")) return false;
  return isRecord(value.declaration) && typeof value.declaration.declarationUuid === "string";
}

function isDashboardSimpleAnalysisResponse(value: unknown): value is SimpleAnalysisResponse {
  if (!isRecord(value) || typeof value.generatedAt !== "string") return false;
  return Array.isArray(value.youngest) && Array.isArray(value.oldest) && Array.isArray(value.ageBins);
}

function isDashboardAgeAnalysisResponse(value: unknown): value is AgeAnalysisResponse {
  if (!isRecord(value) || typeof value.generatedAt !== "string") return false;
  const context = value.declarationContext;
  return isRecord(value.person) && Array.isArray(value.matches)
    && isRecord(context) && typeof context.interestCount === "number"
    && typeof context.assetCount === "number" && Array.isArray(context.history)
    && Array.isArray(value.incomeByYear) && value.incomeByYear.every((year) =>
      isRecord(year) && typeof year.combinedAmount === "number" && Array.isArray(year.sources)
      && year.sources.every((source) => isRecord(source) && typeof source.sourceId === "string"
        && typeof source.amount === "number" && typeof source.metricEligible === "boolean"))
    && Array.isArray(value.assetInventory) && value.assetInventory.every((asset) =>
      isRecord(asset) && typeof asset.sourceId === "string" && typeof asset.kind === "string"
      && typeof asset.metricEligible === "boolean");
}

function declarationId(pathname: string): string | null {
  if (!pathname.startsWith(DASHBOARD_DECLARATION_PREFIX)) return null;
  const value = pathname.slice(DASHBOARD_DECLARATION_PREFIX.length);
  if (!value || value.includes("/")) return null;
  try {
    return decodeURIComponent(value);
  } catch {
    return null;
  }
}

async function proxySlice(
  request: Request,
  env: WorkerEnv,
  fetcher: Fetcher,
  upstreamPath: string,
  validate: (value: unknown) => boolean,
  upstreamSearch = "",
): Promise<Response> {
  if (!env.BRIDGE_URL || !env.BRIDGE_TOKEN) {
    return jsonResponse(request, env, errorPayload("CONFIGURATION_ERROR", "API is not configured"), 500);
  }

  let upstream: Response;
  try {
    const target = new URL(upstreamPath, env.BRIDGE_URL);
    target.search = upstreamSearch;
    upstream = await fetcher(target.toString(), {
      method: "GET",
      headers: { Authorization: `Bearer ${env.BRIDGE_TOKEN}`, Accept: "application/json" },
    });
  } catch {
    return jsonResponse(request, env, errorPayload("UPSTREAM_UNAVAILABLE", "Dashboard data is unavailable"), 502);
  }

  if (!upstream.ok) {
    return jsonResponse(request, env, errorPayload("UPSTREAM_ERROR", "Dashboard data is unavailable"), 502);
  }

  let payload: unknown;
  try {
    payload = await upstream.json();
  } catch {
    return jsonResponse(request, env, errorPayload("INVALID_UPSTREAM_RESPONSE", "Dashboard data is invalid"), 502);
  }
  if (!validate(payload)) {
    return jsonResponse(request, env, errorPayload("INVALID_UPSTREAM_RESPONSE", "Dashboard data is invalid"), 502);
  }
  return jsonResponse(request, env, payload, 200, { "Cache-Control": CACHE_CONTROL });
}

export async function handleRequest(
  request: Request,
  env: WorkerEnv,
  fetcher: Fetcher = fetch,
): Promise<Response> {
  const url = new URL(request.url);

  if (url.pathname === HEALTH_PATH && request.method === "GET") {
    return jsonResponse(request, env, { ok: true });
  }
  const slicePath = DASHBOARD_SLICE_ROUTES[url.pathname as keyof typeof DASHBOARD_SLICE_ROUTES];
  if (slicePath && request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders(request, env) });
  }
  if (slicePath && request.method === "GET") {
    const validate = slicePath.endsWith("/health")
      ? isDashboardHealthResponse
      : slicePath.endsWith("/overview")
      ? isDashboardOverviewResponse
      : slicePath.endsWith("/gender")
        ? isDashboardGenderResponse
      : slicePath.endsWith("/highlights")
        ? isDashboardHighlightsResponse
      : slicePath.endsWith("/search")
        ? isDashboardSearchResponse
        : slicePath.endsWith("/simple-analysis")
          ? isDashboardSimpleAnalysisResponse
          : slicePath.endsWith("/age-analysis")
            ? isDashboardAgeAnalysisResponse
        : isDashboardBreakdownResponse;
    const search = slicePath.endsWith("/search") || slicePath.endsWith("/age-analysis") ? new URL(request.url).search : "";
    return proxySlice(request, env, fetcher, slicePath, validate, search);
  }
  const id = declarationId(url.pathname);
  if (id && request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders(request, env) });
  }
  if (id && request.method === "GET") {
    return proxySlice(
      request,
      env,
      fetcher,
      `/v1/dashboard/declarations/${encodeURIComponent(id)}`,
      isDashboardDeclarationResponse,
    );
  }
  if (url.pathname.startsWith(DASHBOARD_DECLARATION_PREFIX)) {
    return jsonResponse(request, env, errorPayload("NOT_FOUND", "Route not found"), 404);
  }
  if (slicePath) {
    return jsonResponse(request, env, errorPayload("METHOD_NOT_ALLOWED", "Use GET for dashboard data"), 405);
  }
  return jsonResponse(request, env, errorPayload("NOT_FOUND", "Route not found"), 404);
}

export default {
  fetch(request: Request, env: WorkerEnv): Promise<Response> {
    return handleRequest(request, env);
  },
};
