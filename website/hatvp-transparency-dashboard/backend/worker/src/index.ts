import type { DashboardResponse, WorkerEnv } from "./types";

const DASHBOARD_PATH = "/api/dashboard";
const HEALTH_PATH = "/healthz";
const CACHE_CONTROL = "public, max-age=300, s-maxage=600";

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

function isDashboardResponse(value: unknown): value is DashboardResponse {
  if (!isRecord(value) || typeof value.generatedAt !== "string") return false;
  if (!(value.snapshotDate === null || typeof value.snapshotDate === "string")) return false;
  const tables = value.tables;
  if (!isRecord(tables)) return false;
  const tableNames = ["declarations", "people", "incomes", "assets"];
  if (!tableNames.every((name) => typeof tables[name] === "number")) return false;
  return ["incomeByStream", "assetsBySection", "declarationsByType"].every(
    (key) => Array.isArray(value[key]),
  );
}

async function proxyDashboard(
  request: Request,
  env: WorkerEnv,
  fetcher: Fetcher,
): Promise<Response> {
  if (!env.BRIDGE_URL || !env.BRIDGE_TOKEN) {
    return jsonResponse(request, env, errorPayload("CONFIGURATION_ERROR", "API is not configured"), 500);
  }

  let upstream: Response;
  try {
    const target = new URL("/v1/dashboard", env.BRIDGE_URL).toString();
    upstream = await fetcher(target, {
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
  if (!isDashboardResponse(payload)) {
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
  if (url.pathname === DASHBOARD_PATH && request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders(request, env) });
  }
  if (url.pathname === DASHBOARD_PATH && request.method === "GET") {
    return proxyDashboard(request, env, fetcher);
  }
  if (url.pathname === DASHBOARD_PATH) {
    return jsonResponse(request, env, errorPayload("METHOD_NOT_ALLOWED", "Use GET for dashboard data"), 405);
  }
  return jsonResponse(request, env, errorPayload("NOT_FOUND", "Route not found"), 404);
}

export default {
  fetch(request: Request, env: WorkerEnv): Promise<Response> {
    return handleRequest(request, env);
  },
};
