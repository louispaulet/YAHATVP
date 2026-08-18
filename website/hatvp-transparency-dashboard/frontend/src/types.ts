export interface DashboardTableCounts {
  declarations: number;
  people: number;
  incomes: number;
  assets: number;
}

export interface BreakdownItem {
  label: string;
  rows: number;
  totalValue?: number;
}

export interface DashboardOverviewResponse {
  snapshotDate: string | null;
  generatedAt: string;
  tables: DashboardTableCounts;
}

export interface DashboardBreakdownResponse {
  snapshotDate: string | null;
  generatedAt: string;
  items: BreakdownItem[];
  totalValue?: number;
  yearCount?: number;
}

export interface DeclarationSearchResult {
  declarationUuid: string | null;
  civilite: string | null;
  firstName: string | null;
  lastName: string | null;
  declarationType: string | null;
  mandate: string | null;
  mandateType: string | null;
  mandateCategory: string | null;
  organ: string | null;
  organDeclaration: string | null;
  dateDeposited: string | null;
  isAmended: string | null;
}

export interface DashboardSearchResponse {
  snapshotDate: string | null;
  generatedAt: string;
  results: DeclarationSearchResult[];
  resultCount: number;
}

export interface DashboardDeclarationResponse {
  snapshotDate: string | null;
  generatedAt: string;
  declaration: DeclarationSearchResult;
  rawXml: string;
}
