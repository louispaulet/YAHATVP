import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";

const dashboard = {
  snapshotDate: "2026-08-18",
  generatedAt: "2026-08-18T08:00:00Z",
  tables: { declarations: 2, people: 2, incomes: 3, assets: 4 },
  incomeByStream: [{ label: "mandate_remuneration", rows: 3, totalValue: 120000 }],
  assetsBySection: [{ label: "bank_accounts", rows: 4, totalValue: 80000 }],
  declarationsByType: [{ label: "mandat", rows: 2 }],
};

describe("dashboard application", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(dashboard), { status: 200 })));
  });

  it("renders aggregate metrics and breakdowns", async () => {
    render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);
    expect(await screen.findByText("Declarations")).toBeInTheDocument();
    expect(screen.getByText("Income, by stream")).toBeInTheDocument();
    expect(screen.getByText("Mandate Remuneration")).toBeInTheDocument();
    expect(screen.getByText("Declaration types")).toBeInTheDocument();
  });

  it("renders the about page through the router", () => {
    render(<MemoryRouter initialEntries={["/about"]}><App /></MemoryRouter>);
    expect(screen.getByText("A small window into a public dataset.")).toBeInTheDocument();
    expect(screen.getByText("HATVP open data")).toBeInTheDocument();
  });
});
