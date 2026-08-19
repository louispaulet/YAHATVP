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

export const gender = {
  snapshotDate: "2026-08-18", generatedAt: "2026-08-18T08:00:00Z", unknownRows: 0,
  gender: [{ label: "male", rows: 1 }, { label: "female", rows: 1 }],
  positions: [{ label: "Élu local", male: 1, female: 1, unknown: 0 }],
};

export const declarations = {
  snapshotDate: "2026-08-18", generatedAt: "2026-08-18T08:00:00Z",
  items: [{ label: "Déclaration d'intérêts", rows: 2 }],
};

export const highlights = {
  snapshotDate: "2026-08-18", generatedAt: "2026-08-18T08:00:00Z",
  incomeChanges: [{ declarationUuid: "fixture-uuid-1", firstName: "Alice", lastName: "DUPONT",
    mandate: "Élu local", fromYear: 2023, toYear: 2024, fromAmount: 50_000,
    toAmount: 120_000, absoluteChange: 70_000, ratio: 2.4, reviewRequired: true }],
  unusualAssets: [{ declarationUuid: "fixture-uuid-1", firstName: "Alice", lastName: "DUPONT",
    mandate: "Élu local", section: "immeubleDto", assetName: "Maison individuelle",
    rawValue: "2 400 000", amount: 2_400_000, anomalyStatus: "active", reviewRequired: true }],
  amendedRecords: [{ declarationUuid: "fixture-uuid-1", firstName: "Alice", lastName: "DUPONT",
    mandate: "Élu local", filingCount: 5, amendedCount: 3,
    firstFiled: "2022-01-01", latestFiled: "2026-01-01" }],
};

export const simpleAnalysis = {
  snapshotDate: "2026-08-18", generatedAt: "2026-08-18T08:00:00Z", referenceDate: "2026-08-18",
  youngest: [{ declarationUuid: "young", firstName: "Young", lastName: "Person", dateOfBirth: "2010-01-01", ageYears: 16, qualityStatus: "implausible", mandate: "Example", organ: "Example" }],
  oldest: [{ declarationUuid: "old", firstName: "Old", lastName: "Person", dateOfBirth: "1905-01-01", ageYears: 121, qualityStatus: "implausible", mandate: "Example", organ: "Example" }],
  ageBins: [{ label: "40–44", ageBinStart: 40, rows: 2, averageSalary: 20000, medianSalary: 15000 }],
  ageBinsIncludingZero: [{ label: "40–44", ageBinStart: 40, rows: 3, averageSalary: 13333, medianSalary: 15000 }],
  zeroSalaryBins: [{ label: "40–44", ageBinStart: 40, rows: 1 }],
};

const declaration = (declarationUuid: string, family: string, filedAt: string, isSelected: boolean, incomeRows = 0, assetRows = 0) => ({
  declarationUuid, filedAt, family, isSelected, incomeRows, assetRows,
  typeId: family === "interest" ? "DI" : "DSP",
  typeLabel: family === "interest" ? "Déclaration d'intérêts modificative" : "Déclaration de situation patrimoniale modificative",
  isAmended: isSelected, mandate: "Membre du Gouvernement", organ: "Premier ministre",
});

const incomeSource = (sourceId: string, label: string, amount: number, kind = "activity", employer = "Gouvernement") => ({
  sourceId, label, amount, kind, employer, metricEligible: false, reviewStatus: "active",
  sourceSection: kind === "mandate" ? "mandatElectifDto" : "activProfCinqDerniereDto",
  startDate: null, endDate: null, basis: "Net",
});

const asset = (sourceId: string, kind: string, name: string, value: number, eventYear: number | null = null) => ({
  sourceId, kind, name, value, eventYear, eventDateRaw: eventYear ? String(eventYear) : null,
  eventDate: null, eventPrecision: eventYear ? "year" : null,
  eventSourceField: eventYear ? "dateAcquisition" : null,
  eventKind: eventYear ? "acquisition" : null, ageYears: null,
  ageRangeMin: eventYear ? eventYear - 1987 : null, ageRangeMax: eventYear ? eventYear - 1986 : null,
  declaredAt: "2026-06-04", metricEligible: false, reviewStatus: "active",
});

const latestInterest = declaration("f0f1acca-0721-494c-af26-84fc59abc0e3", "interest", "2026-06-04", true, 26);
const latestAssets = declaration("d832921b-f94c-4e3e-8a4a-34418517b4ac", "assets", "2026-06-04", true, 0, 9);

export const ageAnalysis = {
  snapshotDate: "2026-08-19", generatedAt: "2026-08-19T08:00:00Z",
  person: { personKey: "sebastien|lecornu|1986-06-11", primaryUuid: latestInterest.declarationUuid, firstName: "Sébastien", lastName: "LECORNU", dateOfBirth: "1986-06-11", ageYears: 40, qualityStatus: "valid", declarationCount: 6 },
  matches: [],
  declarationContext: {
    interestCount: 3, assetCount: 3, latestInterest, latestAssets,
    history: [
      latestInterest, latestAssets,
      declaration("9d86eed3-1694-4954-85f1-709f50680473", "interest", "2026-02-27", false, 23),
      declaration("c9a75061-21bc-44ee-8589-e07899a1e4d8", "assets", "2026-02-27", false, 0, 8),
      declaration("74353f7c-8c2c-4b87-8863-ea5fde31f22e", "interest", "2025-11-13", false, 20),
      declaration("b6ff5941-142a-4075-9c06-482c2eaccbfb", "assets", "2025-11-13", false, 0, 7),
    ],
  },
  incomeByYear: [
    { year: 2020, combinedAmount: 120794, sources: [incomeSource("i-2020-1", "Ministre des Outre-mer", 50886), incomeSource("i-2020-2", "Conseiller départemental de l'Eure", 19022, "mandate")] },
    { year: 2021, combinedAmount: 119977, sources: [incomeSource("i-2021-1", "Ministre des Outre-mer", 101772), incomeSource("i-2021-2", "Conseiller départemental de l'Eure", 18205, "mandate")] },
    { year: 2022, combinedAmount: 127455, sources: [incomeSource("i-2022-1", "Ministre des armées", 66744), incomeSource("i-2022-2", "Conseiller départemental de l'Eure", 19967, "mandate")] },
    { year: 2023, combinedAmount: 132524, sources: [incomeSource("i-2023-1", "Ministre des armées", 110161), incomeSource("i-2023-2", "5ème vice-président du conseil départemental de l'Eure", 22363, "mandate")] },
    { year: 2024, combinedAmount: 146250, sources: [incomeSource("i-2024-1", "Ministre des armées", 111393), incomeSource("i-2024-2", "Droits d'adaptation audiovisuelle", 10000, "activity", "Éditions Plon"), incomeSource("i-2024-3", "5ème vice-président du conseil départemental de l'Eure", 24857, "mandate")] },
    { year: 2025, combinedAmount: 192449, sources: [incomeSource("i-2025-1", "Ministre des armées", 83502), incomeSource("i-2025-2", "Premier ministre", 49950), incomeSource("i-2025-3", "Droits d'adaptation audiovisuelle", 34138, "activity", "Éditions Plon"), incomeSource("i-2025-4", "5ème vice-président du conseil départemental de l'Eure", 24859, "mandate")] },
    { year: 2026, combinedAmount: 89653, sources: [incomeSource("i-2026-1", "Premier ministre", 67500), incomeSource("i-2026-2", "Droits d'adaptation audiovisuelle", 11796, "activity", "Éditions Plon"), incomeSource("i-2026-3", "5ème vice-président du conseil départemental de l'Eure", 10357, "mandate")] },
  ],
  assetInventory: [
    { ...asset("a-life-1", "assuranceVieDto", "BRED PEPARVIE", 274, 2002), eventDateRaw: "21/01/2002", eventDate: "2002-01-21", eventPrecision: "day", eventSourceField: "dateSouscription", eventKind: "subscription", ageYears: 15, ageRangeMin: null, ageRangeMax: null },
    { ...asset("a-life-2", "assuranceVieDto", "FONPEL", 7049, 2023), eventDateRaw: "01/09/2023", eventDate: "2023-09-01", eventPrecision: "day", eventSourceField: "dateSouscription", eventKind: "subscription", ageYears: 37, ageRangeMin: null, ageRangeMax: null },
    asset("a-bank-1", "comptesBancaireDto", "Compte courant · SG", 8378),
    asset("a-bank-2", "comptesBancaireDto", "Livret A · SG", 9000),
    asset("a-bank-3", "comptesBancaireDto", "Compte courant · BRED", -559),
    asset("a-bank-4", "comptesBancaireDto", "Compte courant · SG", 1129),
    asset("a-house-1", "immeubleDto", "Maison individuelle", 770000, 2018),
    asset("a-house-2", "immeubleDto", "Maison individuelle", 150475, 2023),
    asset("a-land", "immeubleDto", "Terrain", 100000, 2024),
  ],
};
