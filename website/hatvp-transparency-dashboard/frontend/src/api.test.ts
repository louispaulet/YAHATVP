import { beforeEach, describe, expect, it, vi } from "vitest";
import { fetchAssets, fetchIncome, fetchOverview } from "./api";

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
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8787/api/dashboard/overview", expect.any(Object));
  });

  it("loads breakdown slices independently", async () => {
    const response = { snapshotDate: "2026-08-18", generatedAt: "now", items: [] };
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response(JSON.stringify(response), { status: 200 })));
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchIncome()).resolves.toEqual(response);
    await expect(fetchAssets()).resolves.toEqual(response);
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(fetchMock.mock.calls.map(([url]) => url)).toEqual([
      "http://localhost:8787/api/dashboard/income",
      "http://localhost:8787/api/dashboard/assets",
    ]);
  });

  it("rejects failed or malformed responses", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("nope", { status: 503 })));
    await expect(fetchOverview()).rejects.toThrow("Dashboard data could not be loaded");

    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({}), { status: 200 })));
    await expect(fetchOverview()).rejects.toThrow("unexpected shape");
  });
});
