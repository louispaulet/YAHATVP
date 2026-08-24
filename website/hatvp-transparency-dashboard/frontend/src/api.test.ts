import { beforeEach, describe, expect, it, vi } from "vitest";
import { fetchAgeAnalysis, fetchAssets, fetchGender, fetchHealth, fetchHighlights, fetchIncome, fetchOverview, fetchSimpleAnalysis } from "./api";

describe("dashboard API client", () => {
  beforeEach(() => vi.restoreAllMocks());

  it("loads the overview slice", async () => {
    const response = {
      snapshotDate: "2026-08-18",
      generatedAt: "2026-08-18T08:00:00Z",
      tables: { declarations: 1, people: 1, incomes: 2, assets: 3 },
    };
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response(JSON.stringify(response), { status: 200 })));
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchOverview()).resolves.toEqual(response);
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8787/api/dashboard/overview?schema=4", expect.any(Object));
  });

  it("loads breakdown slices independently", async () => {
    const response = { snapshotDate: "2026-08-18", generatedAt: "now", items: [] };
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response(JSON.stringify(response), { status: 200 })));
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchIncome()).resolves.toEqual(response);
    await expect(fetchAssets()).resolves.toEqual(response);
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(fetchMock.mock.calls.map(([url]) => url)).toEqual([
      "http://localhost:8787/api/dashboard/income?schema=4",
      "http://localhost:8787/api/dashboard/assets?schema=4",
    ]);
  });

  it("loads the pipeline health slice", async () => {
    const response = {
      snapshotDate: "2026-08-18", generatedAt: "now", nextIngestionAt: "2026-08-24T05:00:00Z",
      sources: [{ sourceId: "hatvp_website", declarations: 1, rawDeclarations: 2 }],
      layers: [{ layer: "gold", rows: 1, reviewRows: 0 }],
      quality: { errors: 0, warnings: 1, flaggedRecords: 1, regression: false },
      anomalies: [{ status: "active", rows: 1 }],
      anomalyCategories: [{ category: "COMP_YOY_CHANGE", rows: 1 }],
    };
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(response), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchHealth()).resolves.toEqual(response);
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8787/api/dashboard/health?schema=4", expect.any(Object));
  });

  it("loads the gender slice", async () => {
    const response = { snapshotDate: "2026-08-18", generatedAt: "now", gender: [], unknownRows: 0, positions: [] };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(response), { status: 200 })));

    await expect(fetchGender()).resolves.toEqual(response);
  });

  it("loads the source-linked highlights slice", async () => {
    const response = { snapshotDate: "2026-08-18", generatedAt: "now",
      incomeChanges: [], unusualAssets: [], amendedRecords: [] };
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(response), { status: 200 }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchHighlights()).resolves.toEqual(response);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8787/api/dashboard/highlights?schema=4",
      expect.any(Object),
    );
  });

  it("loads both analysis slices with the expected query", async () => {
    const simple = { snapshotDate: "2026-08-18", generatedAt: "now", referenceDate: "2026-08-18", youngest: [], oldest: [], ageBins: [], ageBinsIncludingZero: [], zeroSalaryBins: [] };
    const age = { snapshotDate: "2026-08-18", generatedAt: "now", person: {}, matches: [], declarationContext: { interestCount: 0, assetCount: 0, history: [] }, incomeByYear: [], assetInventory: [] };
    const fetchMock = vi.fn().mockImplementation((url: string) => Promise.resolve(new Response(JSON.stringify(url.includes("simple-analysis") ? simple : age), { status: 200 })));
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchSimpleAnalysis()).resolves.toEqual(simple);
    await expect(fetchAgeAnalysis("Sébastien Lecornu")).resolves.toEqual(age);
    expect(fetchMock.mock.calls.map(([url]) => url)).toEqual([
      "http://localhost:8787/api/dashboard/simple-analysis?schema=4",
      "http://localhost:8787/api/dashboard/age-analysis?q=S%C3%A9bastien%20Lecornu&schema=4",
    ]);
  });

  it("rejects failed or malformed responses", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("nope", { status: 503 })));
    await expect(fetchOverview()).rejects.toThrow("Dashboard data could not be loaded");

    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({}), { status: 200 })));
    await expect(fetchOverview()).rejects.toThrow("unexpected shape");
  });
});
