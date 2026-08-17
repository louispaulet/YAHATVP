import type { DashboardResponse } from "./types";

const DEFAULT_API_URL = "http://localhost:8787";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isDashboardResponse(value: unknown): value is DashboardResponse {
  if (!isRecord(value) || typeof value.generatedAt !== "string") return false;
  if (!(value.snapshotDate === null || typeof value.snapshotDate === "string")) return false;
  const tables = value.tables;
  if (!isRecord(tables)) return false;
  return ["declarations", "people", "incomes", "assets"].every(
    (name) => typeof tables[name] === "number",
  );
}

export async function fetchDashboard(signal?: AbortSignal): Promise<DashboardResponse> {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || DEFAULT_API_URL;
  const response = await fetch(`${baseUrl.replace(/\/$/, "")}/api/dashboard`, {
    headers: { Accept: "application/json" },
    signal,
  });
  if (!response.ok) throw new Error("Dashboard data could not be loaded.");
  const payload: unknown = await response.json();
  if (!isDashboardResponse(payload)) throw new Error("Dashboard data has an unexpected shape.");
  return payload;
}
