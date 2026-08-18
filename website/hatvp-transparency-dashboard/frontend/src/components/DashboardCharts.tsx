import { lazy, Suspense } from "react";
import type { Language } from "../config/i18n";
import { useI18n } from "../context/I18nContext";
import type { ResourceState } from "../hooks/useResource";
import type { DashboardBreakdownResponse } from "../types";
import { ChartSkeleton, SliceError } from "./Feedback";
import { Panel } from "./Panel";

const IncomeAssetsChart = lazy(() => import("./charts/IncomeAssetsChart"));
const AssetChart = lazy(() => import("./charts/AssetChart"));

interface DashboardChartsProps {
  income: ResourceState<DashboardBreakdownResponse>;
  assets: ResourceState<DashboardBreakdownResponse>;
  language: Language;
}

export function DashboardCharts({ income, assets, language }: DashboardChartsProps) {
  const { locale } = useI18n();
  return (
    <section className="mt-8 grid gap-6 lg:grid-cols-2">
      <Panel title={locale.panels.comparison.title} eyebrow={locale.panels.comparison.eyebrow}>
        {(income.loading || assets.loading) && <ChartSkeleton />}
        {(income.error || assets.error) && <SliceError onRetry={() => { if (income.error) income.reload(); if (assets.error) assets.reload(); }} />}
        {income.data && assets.data && <Suspense fallback={<ChartSkeleton />}><IncomeAssetsChart incomeItems={income.data.items} assetItems={assets.data.items} incomeTotal={income.data.totalValue ?? 0} assetTotal={assets.data.totalValue ?? 0} incomeYearCount={income.data.yearCount ?? 0} emptyLabel={locale.panels.comparison.empty} language={language} chartLabel={locale.accessibility.comparisonChart} legendLabel={locale.accessibility.comparisonLegend} rowsLabel={locale.accessibility.rows} incomeLabel={locale.panels.comparison.income} assetsLabel={locale.panels.comparison.assets} incomeExplanation={locale.panels.comparison.incomeExplanation} assetsExplanation={locale.panels.comparison.assetsExplanation} comparisonNote={locale.panels.comparison.note} /></Suspense>}
      </Panel>
      <Panel title={locale.panels.assets.title} eyebrow={locale.panels.assets.eyebrow}>
        {assets.loading && <ChartSkeleton />}
        {assets.error && <SliceError onRetry={assets.reload} />}
        {assets.data && <Suspense fallback={<ChartSkeleton />}><AssetChart items={assets.data.items} emptyLabel={locale.panels.assets.empty} language={language} /></Suspense>}
      </Panel>
    </section>
  );
}
