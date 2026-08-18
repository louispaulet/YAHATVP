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

export interface WorkerEnv {
  BRIDGE_URL: string;
  BRIDGE_TOKEN: string;
  FRONTEND_ORIGIN: string;
}
