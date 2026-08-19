import { fetchAssets, fetchDeclarations, fetchGender, fetchIncome, fetchOverview } from "../api";
import { DashboardCharts } from "../components/DashboardCharts";
import { DashboardHero } from "../components/DashboardHero";
import { DashboardMetrics } from "../components/DashboardMetrics";
import { ChartSkeleton, SliceError } from "../components/Feedback";
import { DeclarationTable } from "../components/DeclarationTable";
import { Panel } from "../components/Panel";
import { SnapshotMeaning } from "../components/SnapshotMeaning";
import { useI18n } from "../context/I18nContext";
import { useResource } from "../hooks/useResource";
import type { DashboardBreakdownResponse, DashboardGenderResponse, DashboardOverviewResponse } from "../types";

export function DashboardPage() {
  const { language, locale } = useI18n();
  const overview = useResource<DashboardOverviewResponse>(fetchOverview);
  const income = useResource<DashboardBreakdownResponse>(fetchIncome);
  const assets = useResource<DashboardBreakdownResponse>(fetchAssets);
  const declarations = useResource<DashboardBreakdownResponse>(fetchDeclarations);
  const gender = useResource<DashboardGenderResponse>(fetchGender);

  return (
    <div className="mx-auto max-w-7xl px-5 py-8 lg:px-8 lg:py-12">
      <DashboardHero overview={overview.data} loading={overview.loading} />
      <DashboardMetrics resource={overview} language={language} />
      <DashboardCharts income={income} assets={assets} gender={gender} language={language} />
      <section className="mt-6 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <Panel title={locale.panels.declarationTypes.title} eyebrow={locale.panels.declarationTypes.eyebrow}>
          {declarations.loading && <ChartSkeleton table />}
          {declarations.error && <SliceError onRetry={declarations.reload} />}
          {declarations.data && <DeclarationTable data={declarations.data} language={language} />}
        </Panel>
        <Panel title={locale.panels.snapshotMeaning.title} eyebrow={locale.panels.snapshotMeaning.eyebrow}>
          <SnapshotMeaning overview={overview.data} loading={overview.loading} language={language} />
        </Panel>
      </section>
    </div>
  );
}
