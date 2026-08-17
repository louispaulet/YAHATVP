import { beforeEach, describe, expect, it, vi } from "vitest";
import { fetchDashboard } from "./api";

describe("dashboard API client", () => {
  beforeEach(() => vi.restoreAllMocks());

  it("loads a valid aggregate response", async () => {
    const response = {
      snapshotDate: "2026-08-18",
      generatedAt: "2026-08-18T08:00:00Z",
      tables: { declarations: 1, people: 1, incomes: 2, assets: 3 },
      incomeByStream: [],
      assetsBySection: [],
      declarationsByType: [],
    };
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(response), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchDashboard()).resolves.toEqual(response);
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8787/api/dashboard", expect.any(Object));
  });

  it("rejects failed or malformed responses", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("nope", { status: 503 })));
    await expect(fetchDashboard()).rejects.toThrow("Dashboard data could not be loaded");

    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({}), { status: 200 })));
    await expect(fetchDashboard()).rejects.toThrow("unexpected shape");
  });
});
