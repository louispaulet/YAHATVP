import { describe, expect, it, vi } from "vitest";
import { handleRequest } from "./index";
import type { DashboardOverviewResponse, WorkerEnv } from "./types";

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
});
