import { fetchAssets, fetchDeclarations, fetchGender, fetchIncome, fetchOverview } from "../api";
import { DashboardCharts } from "../components/DashboardCharts";
import { DashboardHero } from "../components/DashboardHero";
import { DashboardMetrics } from "../components/DashboardMetrics";
import { useI18n } from "../context/I18nContext";
import { useDeferredLoad } from "../hooks/useDeferredLoad";
import { useResource } from "../hooks/useResource";
import type { DashboardBreakdownResponse, DashboardGenderResponse, DashboardOverviewResponse } from "../types";

export function DashboardPage() {
  const { language } = useI18n();
  const { ready: deferred, sentinelRef } = useDeferredLoad();
  const overview = useResource<DashboardOverviewResponse>(fetchOverview);
  const income = useResource<DashboardBreakdownResponse>(fetchIncome, { enabled: deferred });
  const assets = useResource<DashboardBreakdownResponse>(fetchAssets, { enabled: deferred });
  const declarations = useResource<DashboardBreakdownResponse>(fetchDeclarations, { enabled: deferred });
  const gender = useResource<DashboardGenderResponse>(fetchGender, { enabled: deferred });

  return (
    <div className="mx-auto max-w-7xl px-5 py-8 lg:px-8 lg:py-12">
      <DashboardHero overview={overview.data} loading={overview.loading} error={overview.error} onRetry={overview.reload} />
      <DashboardMetrics resource={overview} language={language} />
      <div ref={sentinelRef} data-testid="homepage-deferred-sentinel" className="h-px" aria-hidden="true" />
      <DashboardCharts income={income} assets={assets} declarations={declarations} gender={gender} overview={overview.data} language={language} deferred={deferred} />
    </div>
  );
}
