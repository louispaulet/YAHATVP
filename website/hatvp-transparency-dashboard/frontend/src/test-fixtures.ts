export const dashboard = {
  snapshotDate: "2026-08-18", generatedAt: "2026-08-18T08:00:00Z",
  tables: { declarations: 2, people: 2, incomes: 3, assets: 4 },
};

export const income = {
  snapshotDate: "2026-08-18", generatedAt: "2026-08-18T08:00:00Z", totalValue: 150000, yearCount: 2,
  items: [{ label: "mandate_remuneration", rows: 2, totalValue: 120000 }, { label: "revenu_mandat", rows: 1, totalValue: 30000 }],
};

export const assets = {
  snapshotDate: "2026-08-18", generatedAt: "2026-08-18T08:00:00Z", totalValue: 80000,
  items: [{ label: "immeubleDto", rows: 4, totalValue: 80000 }],
};

export const declarations = {
  snapshotDate: "2026-08-18", generatedAt: "2026-08-18T08:00:00Z",
  items: [{ label: "Déclaration d'intérêts", rows: 2 }],
};

export const simpleAnalysis = {
  snapshotDate: "2026-08-18", generatedAt: "2026-08-18T08:00:00Z", referenceDate: "2026-08-18",
  youngest: [{ declarationUuid: "young", firstName: "Young", lastName: "Person", dateOfBirth: "2010-01-01", ageYears: 16, qualityStatus: "implausible", mandate: "Example", organ: "Example" }],
  oldest: [{ declarationUuid: "old", firstName: "Old", lastName: "Person", dateOfBirth: "1905-01-01", ageYears: 121, qualityStatus: "implausible", mandate: "Example", organ: "Example" }],
  ageBins: [{ label: "40–44", ageBinStart: 40, rows: 2, averageSalary: 20000, medianSalary: 15000 }],
};

export const ageAnalysis = {
  snapshotDate: "2026-08-18", generatedAt: "2026-08-18T08:00:00Z",
  person: { personKey: "sebastien|lecornu|1976-06-11", primaryUuid: "lecornu-1", firstName: "Sébastien", lastName: "LECORNU", dateOfBirth: "1976-06-11", ageYears: 50, qualityStatus: "valid", declarationCount: 4 },
  matches: [],
  incomeByYear: [{ year: 2025, combinedAmount: 120000, sources: [{ source: "mandatElectifDto", label: "Minister", amount: 120000 }] }],
  occupationsByYear: [{ year: 2025, count: 1, occupations: [{ label: "Minister", source: "Government", rows: 1 }] }],
  assetTimeline: [{ year: 2007, relativeAge: 30, assets: [{ source: "immeubleDto", name: "House", value: 770000 }] }],
};
