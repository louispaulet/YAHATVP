import { describe, expect, it, vi } from "vitest";
import { handleRequest } from "./index";
import type { AgeAnalysisResponse, DashboardGenderResponse, DashboardHealthResponse, DashboardHighlightsResponse, DashboardOverviewResponse, SimpleAnalysisResponse, WorkerEnv } from "./types";

const env: WorkerEnv = {
  BRIDGE_URL: "https://bridge.example.test",
  BRIDGE_TOKEN: "fixture-token",
  FRONTEND_ORIGIN: "https://louispaulet.github.io,http://localhost:5173",
};

const overview: DashboardOverviewResponse = {
  snapshotDate: "2026-08-18",
  generatedAt: "2026-08-18T08:00:00Z",
  tables: { declarations: 2, people: 2, incomes: 3, assets: 4 },
};

const health: DashboardHealthResponse = {
  snapshotDate: "2026-08-18",
  generatedAt: "2026-08-18T08:00:00Z",
  nextIngestionAt: "2026-08-24T05:00:00Z",
  sources: [{ sourceId: "hatvp_website", declarations: 2, rawDeclarations: 3 }],
  layers: [{ layer: "gold", rows: 2, reviewRows: 1 }],
  quality: { errors: 0, warnings: 1, flaggedRecords: 1, regression: false },
  anomalies: [{ status: "active", rows: 1 }],
  anomalyCategories: [{ category: "COMP_YOY_CHANGE", rows: 1 }],
};

const gender: DashboardGenderResponse = {
  snapshotDate: "2026-08-18",
  generatedAt: "2026-08-18T08:00:00Z",
  gender: [{ label: "male", rows: 1 }, { label: "female", rows: 1 }],
  unknownRows: 0,
  positions: [{ label: "Maire", male: 1, female: 1, unknown: 0 }],
};

const highlights: DashboardHighlightsResponse = {
  snapshotDate: "2026-08-18",
  generatedAt: "2026-08-18T08:00:00Z",
  incomeChanges: [{ declarationUuid: "income-1", firstName: "Alice", lastName: "DUPONT",
    mandate: "Mayor", fromYear: 2023, toYear: 2024, fromAmount: 50_000,
    toAmount: 120_000, absoluteChange: 70_000, ratio: 2.4, reviewRequired: true }],
  unusualAssets: [],
  amendedRecords: [],
};

const search = {
  snapshotDate: "2026-08-18",
  generatedAt: "2026-08-18T08:00:00Z",
  resultCount: 0,
  results: [],
};

const declaration = {
  snapshotDate: "2026-08-18",
  generatedAt: "2026-08-18T08:00:00Z",
  declaration: { declarationUuid: "fixture-uuid-1" },
  rawXml: "<declaration><uuid>fixture-uuid-1</uuid></declaration>",
};

const simpleAnalysis: SimpleAnalysisResponse = {
  snapshotDate: "2026-08-18",
  generatedAt: "2026-08-18T08:00:00Z",
  referenceDate: "2026-08-18",
  youngest: [],
  oldest: [],
  ageBins: [],
};

const ageAnalysis: AgeAnalysisResponse = {
  snapshotDate: "2026-08-18",
  generatedAt: "2026-08-18T08:00:00Z",
  person: {
    personKey: "fixture",
    primaryUuid: "fixture-uuid-1",
    firstName: "Alice",
    lastName: "DUPONT",
    dateOfBirth: "1980-03-02",
    ageYears: 46,
    qualityStatus: "valid",
    declarationCount: 1,
  },
  matches: [],
  declarationContext: {
    interestCount: 1,
    assetCount: 0,
    latestInterest: null,
    latestAssets: null,
    history: [],
  },
  incomeByYear: [],
  assetInventory: [],
};

function request(path: string, init?: RequestInit): Request {
  return new Request(`https://api.example.test${path}`, init);
}

describe("dashboard Worker", () => {
  it("returns a health response", async () => {
    const response = await handleRequest(request("/healthz"), env);
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({ ok: true });
  });

  it("handles CORS preflight for an allowed origin", async () => {
    const response = await handleRequest(
      request("/api/dashboard/income", {
        method: "OPTIONS",
        headers: { Origin: "http://localhost:5173" },
      }),
      env,
    );
    expect(response.status).toBe(204);
    expect(response.headers.get("Access-Control-Allow-Origin")).toBe("http://localhost:5173");
  });

  it("forwards the bridge token and validates the overview slice", async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(JSON.stringify(overview), { status: 200 }),
    );
    const response = await handleRequest(
      request("/api/dashboard/overview", { headers: { Origin: "https://louispaulet.github.io" } }),
      env,
      fetcher,
    );
    expect(response.status).toBe(200);
    expect(response.headers.get("Cache-Control")).toContain("max-age=300");
    expect(await response.json()).toEqual(overview);
    expect(fetcher).toHaveBeenCalledWith(
      "https://bridge.example.test/v1/dashboard/overview",
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: "Bearer fixture-token" }),
      }),
    );
  });

  it("forwards and validates the pipeline health slice", async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(JSON.stringify(health), { status: 200 }),
    );
    const response = await handleRequest(request("/api/dashboard/health"), env, fetcher);
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual(health);
    expect(fetcher).toHaveBeenCalledWith(
      "https://bridge.example.test/v1/dashboard/health",
      expect.anything(),
    );
  });

  it("maps bridge failures to a safe 502 response", async () => {
    const response = await handleRequest(
      request("/api/dashboard/assets"),
      env,
      vi.fn<typeof fetch>().mockResolvedValue(new Response("failure", { status: 500 })),
    );
    expect(response.status).toBe(502);
    expect(await response.json()).toEqual({
      error: { code: "UPSTREAM_ERROR", message: "Dashboard data is unavailable" },
    });
  });

  it("forwards and validates the gender slice", async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(JSON.stringify(gender), { status: 200 }),
    );
    const response = await handleRequest(request("/api/dashboard/gender"), env, fetcher);
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual(gender);
    expect(fetcher).toHaveBeenCalledWith(
      "https://bridge.example.test/v1/dashboard/gender",
      expect.anything(),
    );
  });

  it("forwards and validates source-linked highlights", async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(JSON.stringify(highlights), { status: 200 }),
    );
    const response = await handleRequest(request("/api/dashboard/highlights"), env, fetcher);
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual(highlights);
    expect(fetcher).toHaveBeenCalledWith(
      "https://bridge.example.test/v1/dashboard/highlights",
      expect.anything(),
    );
  });

  it("rejects unsupported methods and routes", async () => {
    expect((await handleRequest(request("/api/dashboard/assets", { method: "POST" }), env)).status).toBe(405);
    expect((await handleRequest(request("/unknown"), env)).status).toBe(404);
  });

  it("proxies every independent dashboard slice", async () => {
    const fetcher = vi.fn<typeof fetch>().mockImplementation(() =>
      Promise.resolve(new Response(JSON.stringify({ snapshotDate: null, generatedAt: "now", items: [] }), { status: 200 })),
    );
    for (const path of ["income", "assets", "declarations"]) {
      const response = await handleRequest(request(`/api/dashboard/${path}`), env, fetcher);
      expect(response.status).toBe(200);
    }
    expect(fetcher).toHaveBeenCalledTimes(3);
  });

  it("forwards a declaration search query", async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(JSON.stringify(search), { status: 200 }),
    );
    const response = await handleRequest(request("/api/dashboard/search?q=Dupont"), env, fetcher);
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual(search);
    expect(fetcher).toHaveBeenCalledWith(
      "https://bridge.example.test/v1/dashboard/search?q=Dupont",
      expect.anything(),
    );
  });

  it("proxies a declaration detail route to the bridge", async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(JSON.stringify(declaration), { status: 200 }),
    );
    const response = await handleRequest(
      request("/api/dashboard/declarations/fixture-uuid-1"),
      env,
      fetcher,
    );
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual(declaration);
    expect(fetcher).toHaveBeenCalledWith(
      "https://bridge.example.test/v1/dashboard/declarations/fixture-uuid-1",
      expect.anything(),
    );
  });

  it("proxies both analytical routes and forwards the declarant query", async () => {
    const fetcher = vi.fn<typeof fetch>().mockImplementation((url) => {
      const target = typeof url === "string" ? url : url instanceof URL ? url.toString() : url.url;
      const payload = target.includes("age-analysis") ? ageAnalysis : simpleAnalysis;
      return Promise.resolve(new Response(JSON.stringify(payload), { status: 200 }));
    });
    expect((await handleRequest(request("/api/dashboard/simple-analysis"), env, fetcher)).status).toBe(200);
    expect((await handleRequest(request("/api/dashboard/age-analysis?q=Lecornu"), env, fetcher)).status).toBe(200);
    expect(fetcher).toHaveBeenLastCalledWith(
      "https://bridge.example.test/v1/dashboard/age-analysis?q=Lecornu",
      expect.anything(),
    );
  });

  it("rejects the obsolete occupation and repeated-asset age payload", async () => {
    const legacy = { ...ageAnalysis, declarationContext: undefined, assetInventory: undefined,
      occupationsByYear: [], assetTimeline: [] };
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(JSON.stringify(legacy), { status: 200 }),
    );
    const response = await handleRequest(
      request("/api/dashboard/age-analysis?q=Lecornu"), env, fetcher,
    );
    expect(response.status).toBe(502);
  });
});
