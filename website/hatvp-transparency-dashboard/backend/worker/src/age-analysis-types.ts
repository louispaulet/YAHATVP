export interface AgeAnalysisPerson {
  personKey: string | null;
  primaryUuid: string | null;
  firstName: string | null;
  lastName: string | null;
  dateOfBirth: string | null;
  ageYears: number | null;
  qualityStatus: string | null;
  declarationCount: number;
}

export interface AgeAnalysisDeclaration {
  declarationUuid: string | null;
  filedAt: string | null;
  typeId: string | null;
  typeLabel: string | null;
  isAmended: boolean;
  mandate: string | null;
  organ: string | null;
  family: string | null;
  isSelected: boolean;
  incomeRows: number;
  assetRows: number;
}

export interface AgeAnalysisResponse {
  snapshotDate: string | null;
  generatedAt: string;
  person: AgeAnalysisPerson;
  matches: AgeAnalysisPerson[];
  declarationContext: {
    interestCount: number;
    assetCount: number;
    latestInterest: AgeAnalysisDeclaration | null;
    latestAssets: AgeAnalysisDeclaration | null;
    history: AgeAnalysisDeclaration[];
  };
  incomeByYear: Array<{
    year: number; combinedAmount: number;
    sources: Array<{
      sourceId: string; kind: string | null; sourceSection: string | null;
      label: string | null; employer: string | null; startDate: string | null;
      endDate: string | null; basis: string | null; amount: number;
      metricEligible: boolean; reviewStatus: string | null;
    }>;
  }>;
  assetInventory: Array<{
    sourceId: string; kind: string; name: string | null; value: number | null;
    eventYear: number | null; eventDateRaw: string | null; eventDate: string | null;
    eventPrecision: string | null; eventSourceField: string | null;
    eventKind: string | null; ageYears: number | null; ageRangeMin: number | null;
    ageRangeMax: number | null; declaredAt: string | null;
    metricEligible: boolean; reviewStatus: string | null;
  }>;
}
