import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";

const dashboard = {
  snapshotDate: "2026-08-18",
  generatedAt: "2026-08-18T08:00:00Z",
  tables: { declarations: 2, people: 2, incomes: 3, assets: 4 },
};

const income = {
  snapshotDate: "2026-08-18",
  generatedAt: "2026-08-18T08:00:00Z",
  totalValue: 150000,
  yearCount: 2,
  items: [
    { label: "mandate_remuneration", rows: 2, totalValue: 120000 },
    { label: "revenu_mandat", rows: 1, totalValue: 30000 },
  ],
};

const assets = {
  snapshotDate: "2026-08-18",
  generatedAt: "2026-08-18T08:00:00Z",
  totalValue: 80000,
  items: [{ label: "immeubleDto", rows: 4, totalValue: 80000 }],
};

const declarations = {
  snapshotDate: "2026-08-18",
  generatedAt: "2026-08-18T08:00:00Z",
  items: [{ label: "Déclaration d'intérêts", rows: 2 }],
};

const search = {
  snapshotDate: "2026-08-18",
  generatedAt: "2026-08-18T08:00:00Z",
  resultCount: 1,
  results: [{
    declarationUuid: "fixture-uuid-1",
    civilite: "M.",
    firstName: "Alice",
    lastName: "DUPONT",
    declarationType: "Déclaration d'intérêts",
    mandate: "Élu local",
    mandateType: "Élu municipal",
    mandateCategory: "Local",
    organ: "Paris",
    organDeclaration: null,
    dateDeposited: "2026-01-01",
    isAmended: "false",
  }],
};

const declaration = {
  snapshotDate: "2026-08-18",
  generatedAt: "2026-08-18T08:00:00Z",
  declaration: search.results[0],
  rawXml: "<declaration>\n  <uuid>fixture-uuid-1</uuid>\n</declaration>",
};

describe("dashboard application", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn().mockImplementation((url: string) => {
      const path = new URL(url).pathname;
      const payload = path.endsWith("/overview") ? dashboard : path.endsWith("/income") ? income : path.endsWith("/assets") ? assets : path.endsWith("/search") ? search : path.includes("/declarations/") ? declaration : declarations;
      return Promise.resolve(new Response(JSON.stringify(payload), { status: 200 }));
    }));
  });

  it("renders aggregate metrics and breakdowns", async () => {
    render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);
    expect(await screen.findByText("Declarations")).toBeInTheDocument();
    expect(screen.getByText("unique declarants")).toBeInTheDocument();
    expect(screen.getByText("Average annual income vs assets")).toBeInTheDocument();
    expect(await screen.findByText("Average annual income")).toBeInTheDocument();
    expect(screen.getByText("Assets", { selector: "p" })).toBeInTheDocument();
    expect(screen.getByText("€75K")).toBeInTheDocument();
    expect(screen.getByText("Average annual income")).toHaveClass("break-words");
    expect(screen.getByText("Average annual income")).not.toHaveClass("truncate");
    expect(screen.getByText("€75K")).toHaveClass("whitespace-nowrap");
    expect(screen.getAllByText("€80K")).toHaveLength(2);
    expect(screen.getByText(/Average annual income: €75K/)).toBeInTheDocument();
    expect(screen.getByText("Real estate")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: /Average annual income and asset totals/i })).toBeInTheDocument();
    expect(screen.getByText("Declaration types")).toBeInTheDocument();
    expect(screen.getByText("⚖️", { selector: "header span" })).toHaveClass("size-10");
  });

  it("renders the about page through the router", () => {
    render(<MemoryRouter initialEntries={["/about"]}><App /></MemoryRouter>);
    expect(screen.getByText("A small window into a public dataset.")).toBeInTheDocument();
    expect(screen.getByText("HATVP open data")).toBeInTheDocument();
    expect(screen.getByText("Follow the data back to HATVP.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Declaration index \(CSV\)/ })).toHaveAttribute("href", "https://www.hatvp.fr/livraison/opendata/liste.csv");
    expect(screen.getByRole("link", { name: /Declarations feed \(XML\)/ })).toHaveAttribute("href", "https://www.hatvp.fr/livraison/merge/declarations.xml");
    expect(screen.getByRole("link", { name: /Open source page/ })).toHaveAttribute("target", "_blank");
    expect(screen.getByRole("link", { name: /Open source page/ })).not.toHaveAttribute("download");
    expect(screen.getByRole("link", { name: /Download CSV/ })).toHaveAttribute("download", "");
    expect(screen.getByRole("link", { name: /Download CSV/ })).not.toHaveAttribute("target");
    expect(screen.getByRole("link", { name: /Download XML/ })).toHaveAttribute("download", "");
    const downloadBadges = screen.getAllByText("Direct download");
    expect(downloadBadges).toHaveLength(2);
    downloadBadges.forEach((badge) => {
      expect(badge).toHaveClass("max-w-full");
      expect(badge.parentElement).toHaveClass("flex-wrap");
    });
    expect(screen.getByRole("link", { name: "View project on GitHub" })).toHaveAttribute("href", "https://github.com/louispaulet/YAHATVP/tree/main");
    expect(screen.getByRole("link", { name: /Explore YAHATVP on GitHub/ })).toHaveAttribute("href", "https://github.com/louispaulet/YAHATVP/tree/main");
  });

  it("renders the placeholder page in the expanded navigation", () => {
    render(<MemoryRouter initialEntries={["/explore"]}><App /></MemoryRouter>);
    expect(screen.getByRole("navigation", { name: "Primary navigation" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Data explorer" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByText("More ways to explore are on the way.")).toBeInTheDocument();
    expect(screen.getByText("Placeholder page")).toBeInTheDocument();
  });

  it("searches declarations and opens the source XML detail page", async () => {
    render(<MemoryRouter initialEntries={["/search?q=Alice"]}><App /></MemoryRouter>);
    expect(await screen.findByText("M. Alice DUPONT")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Alice")).toBeInTheDocument();
    const detailLink = screen.getByRole("link", { name: "Open declaration and source XML" });
    expect(detailLink).toHaveAttribute("href", "/declarations/fixture-uuid-1");
    fireEvent.click(detailLink);
    expect(await screen.findByText("The declaration as published")).toBeInTheDocument();
    expect(screen.getByLabelText("Raw declaration XML")).toHaveTextContent("fixture-uuid-1");
  });

  it("switches to French and translates configured data labels", async () => {
    render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);
    expect(await screen.findByText("Real estate")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "French" }));
    expect(screen.getByText("Vue d’ensemble")).toBeInTheDocument();
    expect(screen.getByText("déclarants uniques")).toBeInTheDocument();
    expect(screen.getByText("Immobilier")).toBeInTheDocument();
    expect(screen.getByText("Revenu annuel moyen vs patrimoine")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: /Revenu annuel moyen et patrimoine total/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Voir le projet sur GitHub" })).toHaveAttribute("href", "https://github.com/louispaulet/YAHATVP/tree/main");
    expect(screen.getByRole("link", { name: "Explorer les données" })).toHaveAttribute("href", "/explore");
    fireEvent.click(screen.getByRole("link", { name: "À propos des données" }));
    expect(screen.getByRole("link", { name: /Découvrez YAHATVP sur GitHub/ })).toHaveAttribute("href", "https://github.com/louispaulet/YAHATVP/tree/main");
  });
});
