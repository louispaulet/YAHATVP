import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { declarationXmlFixtures } from "./declaration-fixtures";
import { ageAnalysis, assets, dashboard, declarations, income, simpleAnalysis } from "./test-fixtures";

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
  rawXml: declarationXmlFixtures[0],
};

describe("dashboard application", () => {
  afterEach(() => vi.useRealTimers());

  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn().mockImplementation((url: string) => {
      const path = new URL(url).pathname;
      const payload = path.endsWith("/overview") ? dashboard : path.endsWith("/income") ? income : path.endsWith("/assets") ? assets : path.endsWith("/search") ? search : path.endsWith("/simple-analysis") ? simpleAnalysis : path.endsWith("/age-analysis") ? ageAnalysis : path.includes("/declarations/") ? declaration : declarations;
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
      expect(badge).toHaveClass("shrink-0");
      expect(badge.parentElement).toHaveClass("source-link-header");
    });
    expect(screen.getAllByRole("link").filter((link) => link.classList.contains("source-link-card"))).toHaveLength(3);
    expect(screen.getByRole("link", { name: "View project on GitHub" })).toHaveAttribute("href", "https://github.com/louispaulet/YAHATVP/tree/main");
    expect(screen.getByRole("link", { name: /Explore YAHATVP on GitHub/ })).toHaveAttribute("href", "https://github.com/louispaulet/YAHATVP/tree/main");
  });

  it("renders the placeholder page in the expanded navigation", () => {
    render(<MemoryRouter initialEntries={["/explore"]}><App /></MemoryRouter>);
    expect(screen.getByRole("navigation", { name: "Primary navigation" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Search declarations" })).toHaveAttribute("href", "/search");
    expect(screen.getByRole("link", { name: "Data explorer" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByText("More ways to explore are on the way.")).toBeInTheDocument();
  });

  it("renders the simple DOB and salary analysis page", async () => {
    render(<MemoryRouter initialEntries={["/analysis"]}><App /></MemoryRouter>);
    expect(await screen.findByText("Age, pay, and the shape of the dataset.")).toBeInTheDocument();
    expect(screen.getByText("Youngest declarants")).toBeInTheDocument();
    expect(screen.getByText("Young Person")).toBeInTheDocument();
    expect(screen.getByText("Salary distribution by age")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "Average and median salary by five-year age bin" })).toBeInTheDocument();
  });

  it("renders the Lecornu age and year analysis page", async () => {
    render(<MemoryRouter initialEntries={["/age-analysis"]}><App /></MemoryRouter>);
    expect(await screen.findByText("Sébastien LECORNU")).toBeInTheDocument();
    expect(screen.getByText("Income by year")).toBeInTheDocument();
    expect(screen.getByText("Occupations by year")).toBeInTheDocument();
    expect(screen.getByText("Asset acquisitions over time")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Sébastien Lecornu")).toBeInTheDocument();
  });

  it("renders the redacted HATVP quality issue register", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-08-19T12:00:00Z"));
    render(<MemoryRouter initialEntries={["/quality-issues"]}><App /></MemoryRouter>);
    expect(screen.getByText("Issues reported to HATVP.")).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Issue type" })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Open for" })).toBeInTheDocument();
    expect(screen.getAllByText("Not solved")).toHaveLength(10);
    expect(screen.getByText("3 years, 1 month, 29 days")).toBeInTheDocument();
    expect(screen.getAllByText("2 years, 1 month, 22 days")).toHaveLength(4);
    expect(screen.getAllByText("0 days")).toHaveLength(2);
    expect(screen.getAllByRole("link", { name: "Open link ↗" })[0]).toHaveAttribute("href", "https://www.hatvp.fr/fiche-nominative/?declarant=vigier-jean-francois-17617");
    expect(screen.getByRole("link", { name: "Reported issues" })).toHaveAttribute("aria-current", "page");
  });

  it("searches declarations and opens the source XML detail page", async () => {
    render(<MemoryRouter initialEntries={["/search?q=Alice"]}><App /></MemoryRouter>);
    expect(await screen.findByText("M. Alice DUPONT")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Alice")).toBeInTheDocument();
    const detailLink = screen.getByRole("link", { name: "Open declaration and source XML" });
    expect(detailLink).toHaveAttribute("href", "/declarations/fixture-uuid-1");
    fireEvent.click(detailLink);
    expect(await screen.findByText("The declaration as published")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "What this declaration contains" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Elected mandates" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Bank accounts" })).toBeInTheDocument();
    expect(screen.getByText("50 000,00")).toBeInTheDocument();
    expect(screen.getByText("published fields rendered")).toBeInTheDocument();
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
    expect(screen.getByText("Sources officielles")).toBeInTheDocument();
    const frenchDownloadBadges = screen.getAllByText("Téléchargement direct");
    expect(frenchDownloadBadges).toHaveLength(2);
    frenchDownloadBadges.forEach((badge) => expect(badge.parentElement).toHaveClass("source-link-header"));
    expect(screen.getByRole("link", { name: /Découvrez YAHATVP sur GitHub/ })).toHaveAttribute("href", "https://github.com/louispaulet/YAHATVP/tree/main");
  });
});
