import type { DashboardBreakdownResponse, DashboardOverviewResponse } from "./types";

const DEFAULT_API_URL = "http://localhost:8787";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isMeta(value: unknown): value is Record<string, unknown> & { snapshotDate: string | null; generatedAt: string } {
  return (
    isRecord(value) &&
    typeof value.generatedAt === "string" &&
    (value.snapshotDate === null || typeof value.snapshotDate === "string")
  );
}

function isOverviewResponse(value: unknown): value is DashboardOverviewResponse {
  if (!isMeta(value)) return false;
  const tables = value.tables;
  return isRecord(tables) && ["declarations", "people", "incomes", "assets"].every(
    (name) => typeof tables[name] === "number",
  );
}

function isBreakdownResponse(value: unknown): value is DashboardBreakdownResponse {
  return isMeta(value) && Array.isArray(value.items);
}

async function fetchJson<T>(path: string, validate: (value: unknown) => value is T, signal?: AbortSignal): Promise<T> {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || DEFAULT_API_URL;
  const response = await fetch(`${baseUrl.replace(/\/$/, "")}${path}`, {
    headers: { Accept: "application/json" },
    signal,
  });
  if (!response.ok) throw new Error("Dashboard data could not be loaded.");
  const payload: unknown = await response.json();
  if (!validate(payload)) throw new Error("Dashboard data has an unexpected shape.");
  return payload;
}

export function fetchOverview(signal?: AbortSignal): Promise<DashboardOverviewResponse> {
  return fetchJson("/api/dashboard/overview", isOverviewResponse, signal);
}

export function fetchIncome(signal?: AbortSignal): Promise<DashboardBreakdownResponse> {
  return fetchJson("/api/dashboard/income", isBreakdownResponse, signal);
}

export function fetchAssets(signal?: AbortSignal): Promise<DashboardBreakdownResponse> {
  return fetchJson("/api/dashboard/assets", isBreakdownResponse, signal);
}

export function fetchDeclarations(signal?: AbortSignal): Promise<DashboardBreakdownResponse> {
  return fetchJson("/api/dashboard/declarations", isBreakdownResponse, signal);
}
