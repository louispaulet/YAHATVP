export interface HighlightIdentity {
  declarationUuid: string | null;
  firstName: string | null;
  lastName: string | null;
  mandate: string | null;
}

export interface IncomeChangeHighlight extends HighlightIdentity {
  fromYear: number;
  toYear: number;
  fromAmount: number;
  toAmount: number;
  absoluteChange: number;
  ratio: number | null;
  reviewRequired: boolean;
}

export interface AssetHighlight extends HighlightIdentity {
  section: string | null;
  assetName: string | null;
  rawValue: string | null;
  amount: number;
  anomalyStatus: string | null;
  reviewRequired: boolean;
}

export interface AmendedRecordHighlight extends HighlightIdentity {
  filingCount: number;
  amendedCount: number;
  firstFiled: string | null;
  latestFiled: string | null;
}

export interface DashboardHighlightsResponse {
  snapshotDate: string | null;
  generatedAt: string;
  incomeChanges: IncomeChangeHighlight[];
  unusualAssets: AssetHighlight[];
  amendedRecords: AmendedRecordHighlight[];
}
