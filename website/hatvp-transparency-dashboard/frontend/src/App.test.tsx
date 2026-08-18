import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";

const dashboard = {
  snapshotDate: "2026-08-18",
  generatedAt: "2026-08-18T08:00:00Z",
  tables: { declarations: 2, people: 2, incomes: 3, assets: 4 },
  incomeByStream: [
    { label: "mandate_remuneration", rows: 2, totalValue: 120000 },
    { label: "revenu_mandat", rows: 1, totalValue: 30000 },
  ],
  assetsBySection: [{ label: "immeubleDto", rows: 4, totalValue: 80000 }],
  declarationsByType: [{ label: "Déclaration d'intérêts", rows: 2 }],
};

describe("dashboard application", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(dashboard), { status: 200 })));
  });

  it("renders aggregate metrics and breakdowns", async () => {
    render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);
    expect(await screen.findByText("Declarations")).toBeInTheDocument();
    expect(screen.getByText("Income, by stream")).toBeInTheDocument();
    expect(screen.getByText("Mandate remuneration")).toBeInTheDocument();
    expect(screen.getByText("Mandate income")).toBeInTheDocument();
    expect(screen.getByText("Real estate")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: /Income totals by stream/i })).toBeInTheDocument();
    expect(screen.getByText("Declaration types")).toBeInTheDocument();
  });

  it("renders the about page through the router", () => {
    render(<MemoryRouter initialEntries={["/about"]}><App /></MemoryRouter>);
    expect(screen.getByText("A small window into a public dataset.")).toBeInTheDocument();
    expect(screen.getByText("HATVP open data")).toBeInTheDocument();
    expect(screen.getByText("Follow the data back to HATVP.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Declaration index \(CSV\)/ })).toHaveAttribute("href", "https://www.hatvp.fr/livraison/opendata/liste.csv");
    expect(screen.getByRole("link", { name: /Declarations feed \(XML\)/ })).toHaveAttribute("href", "https://www.hatvp.fr/livraison/merge/declarations.xml");
  });

  it("switches to French and translates configured data labels", async () => {
    render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);
    expect(await screen.findByText("Real estate")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "French" }));
    expect(screen.getByText("Vue d’ensemble")).toBeInTheDocument();
    expect(screen.getByText("Immobilier")).toBeInTheDocument();
    expect(screen.getByText("Revenus, par source")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: /Totaux des revenus par source/i })).toBeInTheDocument();
  });
});
