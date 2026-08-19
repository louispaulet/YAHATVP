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

export interface GenderPosition {
  label: string;
  male: number;
  female: number;
  unknown: number;
}

export interface DashboardGenderResponse {
  snapshotDate: string | null;
  generatedAt: string;
  gender: BreakdownItem[];
  unknownRows: number;
  positions: GenderPosition[];
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

export interface SimpleAnalysisLeader {
  declarationUuid: string | null;
  firstName: string | null;
  lastName: string | null;
  dateOfBirth: string | null;
  ageYears: number;
  qualityStatus: string | null;
  mandate: string | null;
  organ: string | null;
}

export interface SimpleAnalysisResponse {
  snapshotDate: string | null;
  generatedAt: string;
  referenceDate: string | null;
  youngest: SimpleAnalysisLeader[];
  oldest: SimpleAnalysisLeader[];
  ageBins: Array<{ label: string; ageBinStart: number; rows: number; averageSalary: number; medianSalary: number }>;
}

export type { AgeAnalysisDeclaration, AgeAnalysisPerson, AgeAnalysisResponse } from "./age-analysis-types";

export interface WorkerEnv {
  BRIDGE_URL: string;
  BRIDGE_TOKEN: string;
  FRONTEND_ORIGIN: string;
}
