import { lazy, Suspense } from "react";
import type { Language } from "../config/i18n";
import { useI18n } from "../context/I18nContext";
import type { ResourceState } from "../hooks/useResource";
import type { DashboardBreakdownResponse, DashboardGenderResponse } from "../types";
import { ChartSkeleton, SliceError } from "./Feedback";
import { Panel } from "./Panel";

const IncomeAssetsChart = lazy(() => import("./charts/IncomeAssetsChart"));
const AssetChart = lazy(() => import("./charts/AssetChart"));
const GenderRatioChart = lazy(() => import("./charts/GenderRatioChart"));
const GenderPositionChart = lazy(() => import("./charts/GenderPositionChart"));

interface DashboardChartsProps {
  income: ResourceState<DashboardBreakdownResponse>;
  assets: ResourceState<DashboardBreakdownResponse>;
  gender: ResourceState<DashboardGenderResponse>;
  language: Language;
}

export function DashboardCharts({ income, assets, gender, language }: DashboardChartsProps) {
  const { locale } = useI18n();
  return (
    <>
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
      <section className="mt-8 grid gap-6 lg:grid-cols-2">
        <Panel title={locale.panels.genderRatio.title} eyebrow={locale.panels.genderRatio.eyebrow}>
        {gender.loading && <ChartSkeleton />}
        {gender.error && <SliceError onRetry={gender.reload} />}
        {gender.data && <Suspense fallback={<ChartSkeleton />}><GenderRatioChart items={gender.data.gender} unknownRows={gender.data.unknownRows} emptyLabel={locale.panels.genderRatio.empty} language={language} chartLabel={locale.accessibility.genderRatioChart} legendLabel={locale.accessibility.genderRatioLegend} maleLabel={locale.panels.genderRatio.male} femaleLabel={locale.panels.genderRatio.female} unknownNote={locale.panels.genderRatio.unknownNote} /></Suspense>}
        </Panel>
        <Panel title={locale.panels.genderPositions.title} eyebrow={locale.panels.genderPositions.eyebrow}>
        {gender.loading && <ChartSkeleton />}
        {gender.error && <SliceError onRetry={gender.reload} />}
        {gender.data && <Suspense fallback={<ChartSkeleton />}><GenderPositionChart positions={gender.data.positions} emptyLabel={locale.panels.genderPositions.empty} language={language} chartLabel={locale.accessibility.genderPositionsChart} maleLabel={locale.panels.genderPositions.male} femaleLabel={locale.panels.genderPositions.female} /></Suspense>}
        </Panel>
      </section>
    </>
  );
}
