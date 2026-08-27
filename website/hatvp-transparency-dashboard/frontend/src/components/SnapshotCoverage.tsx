import type { Language } from "../config/i18n";
import { useI18n } from "../context/I18nContext";
import { formatNumber } from "../formatters";
import type { DashboardOverviewResponse } from "../types";
import { LoadingShell } from "./Feedback";

interface SnapshotCoverageProps {
  overview: DashboardOverviewResponse | null;
  loading: boolean;
  language: Language;
}

export function SnapshotCoverage({ overview, loading, language }: SnapshotCoverageProps) {
  const { locale } = useI18n();
  const rows = [
    { label: locale.metrics.declarations.label, detail: locale.metrics.declarations.detail, value: overview?.tables.declarations, accent: "bg-emerald" },
    { label: locale.metrics.people.label, detail: locale.metrics.people.detail, value: overview?.tables.people, accent: "bg-lime" },
    { label: locale.metrics.incomes.label, detail: locale.metrics.incomes.detail, value: overview?.tables.incomes, accent: "bg-sky" },
    { label: locale.metrics.assets.label, detail: locale.metrics.assets.detail, value: overview?.tables.assets, accent: "bg-violet" },
  ];

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
      {rows.map((row) => (
        <div className="flex items-center justify-between gap-4 border-t border-slate-100 pt-3 first:border-t-0 first:pt-0" key={row.label}>
          <div className="flex min-w-0 items-start gap-3">
            <span className={`mt-1.5 size-2.5 shrink-0 rounded-full ${row.accent}`} aria-hidden="true" />
            <div className="min-w-0">
              <p className="text-sm font-semibold text-slate-700">{row.label}</p>
              <p className="mt-0.5 text-xs font-medium uppercase tracking-[0.12em] text-slate-400">{row.detail}</p>
            </div>
          </div>
          {loading || row.value === undefined ? <LoadingShell className="h-7 w-16 shrink-0 rounded-lg" /> : <p className="shrink-0 text-2xl font-black tracking-[-0.04em] text-ink">{formatNumber(row.value, language)}</p>}
        </div>
      ))}
    </div>
  );
}
