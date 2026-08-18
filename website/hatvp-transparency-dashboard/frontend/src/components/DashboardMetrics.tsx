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
    <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {resource.loading && [0, 1, 2, 3].map((key) => <MetricSkeleton key={key} />)}
      {resource.error && <div className="sm:col-span-2 lg:col-span-4"><SliceError onRetry={resource.reload} /></div>}
      {resource.data && metrics.map(([metric, value, accent]) => <MetricCard key={metric.label} language={language} label={metric.label} value={value!} detail={metric.detail} accent={accent} />)}
    </section>
  );
}
