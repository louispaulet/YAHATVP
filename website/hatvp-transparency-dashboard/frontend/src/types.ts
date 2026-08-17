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

export interface DashboardResponse {
  snapshotDate: string | null;
  generatedAt: string;
  tables: DashboardTableCounts;
  incomeByStream: BreakdownItem[];
  assetsBySection: BreakdownItem[];
  declarationsByType: BreakdownItem[];
}
