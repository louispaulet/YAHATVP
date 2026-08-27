import type { Language } from "../config/i18n";
import { useI18n } from "../context/I18nContext";
import type { ResourceState } from "../hooks/useResource";
import type { DashboardOverviewResponse } from "../types";
import { MetricSkeleton, SliceError } from "./Feedback";
import { MetricCard } from "./MetricCard";

export function DashboardMetrics({ resource, language }: { resource: ResourceState<DashboardOverviewResponse>; language: Language }) {
  const { locale } = useI18n();
  const metrics = [
    [locale.metrics.declarations, resource.data?.tables.declarations, "bg-emerald"],
    [locale.metrics.people, resource.data?.tables.people, "bg-lime"],
    [locale.metrics.incomes, resource.data?.tables.incomes, "bg-sky"],
    [locale.metrics.assets, resource.data?.tables.assets, "bg-violet"],
  ] as const;

  return (
    <section className="mt-8 rounded-[1.75rem] bg-ink px-5 py-6 text-white shadow-soft sm:px-8 sm:py-7" aria-labelledby="at-a-glance-title">
      <div className="flex flex-col gap-2 border-b border-white/15 pb-5 sm:flex-row sm:items-end sm:justify-between sm:gap-6">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-lime">{locale.metrics.eyebrow}</p>
          <h2 id="at-a-glance-title" className="mt-2 text-2xl font-bold tracking-tight">{locale.metrics.title}</h2>
        </div>
        <p className="max-w-md text-sm leading-6 text-slate-400">{locale.metrics.description}</p>
      </div>
      {resource.loading && <div className="mt-6 grid gap-7 sm:grid-cols-2 lg:grid-cols-4">{[0, 1, 2, 3].map((key) => <MetricSkeleton key={key} compact />)}</div>}
      {resource.error && <div className="mt-6"><SliceError onRetry={resource.reload} /></div>}
      {resource.data && <div className="mt-6 grid gap-7 sm:grid-cols-2 lg:grid-cols-4">{metrics.map(([metric, value, accent]) => <MetricCard key={metric.label} language={language} label={metric.label} value={value!} detail={metric.detail} accent={accent} />)}</div>}
    </section>
  );
}
