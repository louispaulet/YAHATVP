import type {
  AgeAnalysisResponse,
  DashboardBreakdownResponse,
  DashboardDeclarationResponse,
  DashboardOverviewResponse,
  DashboardSearchResponse,
  SimpleAnalysisResponse,
} from "./types";

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
  if (!isMeta(value) || !Array.isArray(value.items)) return false;
  return (value.totalValue === undefined || typeof value.totalValue === "number") &&
    (value.yearCount === undefined || typeof value.yearCount === "number");
}

function isSearchResponse(value: unknown): value is DashboardSearchResponse {
  return isMeta(value) && Array.isArray(value.results) && typeof value.resultCount === "number";
}

function isDeclarationResponse(value: unknown): value is DashboardDeclarationResponse {
  return isMeta(value) && typeof value.rawXml === "string" && typeof value.declaration === "object" && value.declaration !== null;
}

function isSimpleAnalysisResponse(value: unknown): value is SimpleAnalysisResponse {
  return isMeta(value) && Array.isArray(value.youngest) && Array.isArray(value.oldest)
    && Array.isArray(value.ageBins) && Array.isArray(value.ageBinsIncludingZero)
    && Array.isArray(value.zeroSalaryBins);
}

function isAgeAnalysisResponse(value: unknown): value is AgeAnalysisResponse {
  return isMeta(value) && isRecord(value.person) && Array.isArray(value.matches)
    && Array.isArray(value.incomeByYear) && Array.isArray(value.occupationsByYear)
    && Array.isArray(value.assetTimeline);
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

export function fetchSearch(query: string, signal?: AbortSignal): Promise<DashboardSearchResponse> {
  return fetchJson(`/api/dashboard/search?q=${encodeURIComponent(query)}`, isSearchResponse, signal);
}

export function fetchDeclaration(uuid: string, signal?: AbortSignal): Promise<DashboardDeclarationResponse> {
  return fetchJson(`/api/dashboard/declarations/${encodeURIComponent(uuid)}`, isDeclarationResponse, signal);
}

export function fetchSimpleAnalysis(signal?: AbortSignal): Promise<SimpleAnalysisResponse> {
  return fetchJson("/api/dashboard/simple-analysis", isSimpleAnalysisResponse, signal);
}

export function fetchAgeAnalysis(query: string, signal?: AbortSignal): Promise<AgeAnalysisResponse> {
  return fetchJson(`/api/dashboard/age-analysis?q=${encodeURIComponent(query)}`, isAgeAnalysisResponse, signal);
}
