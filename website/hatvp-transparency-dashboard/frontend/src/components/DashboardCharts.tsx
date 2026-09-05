import { lazy, Suspense, useEffect, useRef, useState } from "react";
import type { Language } from "../config/i18n";
import { useI18n } from "../context/I18nContext";
import type { ResourceState } from "../hooks/useResource";
import type { DashboardBreakdownResponse, DashboardGenderResponse, DashboardOverviewResponse } from "../types";
import { DeclarationTable } from "./DeclarationTable";
import { ChartSkeleton, SliceError } from "./Feedback";
import { DeclarationComposition } from "./DeclarationComposition";
import { HomepageInsightCard } from "./HomepageInsightCard";
import { HomepageRouteCard } from "./HomepageRouteCard";
import { Panel } from "./Panel";
import { SnapshotCoverage } from "./SnapshotCoverage";
import { SnapshotMeaning } from "./SnapshotMeaning";

const IncomeAssetsChart = lazy(() => import("./charts/IncomeAssetsChart"));
const AssetChart = lazy(() => import("./charts/AssetChart"));
const GenderRatioChart = lazy(() => import("./charts/GenderRatioChart"));
const GenderPositionChart = lazy(() => import("./charts/GenderPositionChart"));

interface DashboardChartsProps {
  income: ResourceState<DashboardBreakdownResponse>;
  assets: ResourceState<DashboardBreakdownResponse>;
  declarations: ResourceState<DashboardBreakdownResponse>;
  gender: ResourceState<DashboardGenderResponse>;
  overview: DashboardOverviewResponse | null;
  language: Language;
  deferred: boolean;
}

export function DashboardCharts({ income, assets, declarations, gender, overview, language, deferred }: DashboardChartsProps) {
  const { locale } = useI18n();
  const [genderPositionsVisible, setGenderPositionsVisible] = useState(false);
  const genderPositionsRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (genderPositionsVisible) return;

    const node = genderPositionsRef.current;
    if (!node) return;

    if (typeof IntersectionObserver === "undefined") {
      setGenderPositionsVisible(true);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (!entries.some((entry) => entry.isIntersecting)) return;
        setGenderPositionsVisible(true);
        observer.disconnect();
      },
      { rootMargin: "0px 0px 160px 0px", threshold: 0 },
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, [genderPositionsVisible]);

  const retryIncomeAssets = () => {
    if (income.error) income.reload();
    if (assets.error) assets.reload();
  };

  return (
    <>
      <section className="mt-16 scroll-mt-6" aria-labelledby="reading-snapshot-title">
        <div className="max-w-2xl">
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-emerald">{locale.homepage.reading.eyebrow}</p>
          <h2 id="reading-snapshot-title" className="mt-3 text-3xl font-black tracking-[-0.05em] text-ink sm:text-4xl">{locale.homepage.reading.title}</h2>
          <p className="mt-4 text-base leading-7 text-slate-600">{locale.homepage.reading.description}</p>
        </div>

        <div className="mt-8 grid items-stretch gap-5 lg:grid-cols-3">
          <HomepageInsightCard number="01" tone="emerald" eyebrow={locale.homepage.reading.incomeEyebrow} title={locale.panels.comparison.title} description={locale.homepage.reading.incomeDescription}>
            {(income.loading || assets.loading || !deferred) && <ChartSkeleton compact />}
            {(income.error || assets.error) && <SliceError onRetry={retryIncomeAssets} />}
            {income.data && assets.data && <Suspense fallback={<ChartSkeleton compact />}><IncomeAssetsChart incomeItems={income.data.items} assetItems={assets.data.items} incomeTotal={income.data.totalValue ?? 0} assetTotal={assets.data.totalValue ?? 0} incomeYearCount={income.data.yearCount ?? 0} emptyLabel={locale.panels.comparison.empty} language={language} chartLabel={locale.accessibility.comparisonChart} legendLabel={locale.accessibility.comparisonLegend} rowsLabel={locale.accessibility.rows} incomeLabel={locale.panels.comparison.income} assetsLabel={locale.panels.comparison.assets} incomeExplanation={locale.panels.comparison.incomeExplanation} assetsExplanation={locale.panels.comparison.assetsExplanation} comparisonNote={locale.panels.comparison.note} /></Suspense>}
          </HomepageInsightCard>

          <HomepageInsightCard number="02" tone="coral" eyebrow={locale.homepage.reading.representationEyebrow} title={locale.panels.genderRatio.title} description={locale.homepage.reading.representationDescription}>
            {(gender.loading || !deferred) && <ChartSkeleton compact />}
            {gender.error && <SliceError onRetry={gender.reload} />}
            {gender.data && <Suspense fallback={<ChartSkeleton compact />}><GenderRatioChart items={gender.data.gender} unknownRows={gender.data.unknownRows} emptyLabel={locale.panels.genderRatio.empty} language={language} chartLabel={locale.accessibility.genderRatioChart} legendLabel={locale.accessibility.genderRatioLegend} maleLabel={locale.panels.genderRatio.male} femaleLabel={locale.panels.genderRatio.female} unknownNote={locale.panels.genderRatio.unknownNote} compact /></Suspense>}
          </HomepageInsightCard>

          <HomepageInsightCard number="03" tone="sky" eyebrow={locale.homepage.reading.compositionEyebrow} title={locale.homepage.reading.compositionTitle} description={locale.homepage.reading.compositionDescription}>
            {(declarations.loading || !deferred) && <ChartSkeleton compact table />}
            {declarations.error && <SliceError onRetry={declarations.reload} />}
            {declarations.data && <DeclarationComposition data={declarations.data} language={language} />}
          </HomepageInsightCard>
        </div>
      </section>

      <section className="mt-16" aria-labelledby="evidence-title">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between sm:gap-8">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-slate-500">{locale.homepage.evidence.eyebrow}</p>
            <h2 id="evidence-title" className="mt-3 text-2xl font-black tracking-[-0.04em] text-ink sm:text-3xl">{locale.homepage.evidence.title}</h2>
          </div>
          <p className="max-w-lg text-sm leading-6 text-slate-500">{locale.homepage.evidence.description}</p>
        </div>

        <div className="mt-7 grid gap-5">
          <Panel title={locale.panels.assets.title} eyebrow={locale.panels.assets.eyebrow} description={locale.homepage.evidence.assetsDescription}>
            {(!deferred || assets.loading) && <ChartSkeleton compact />}
            {assets.error && <SliceError onRetry={assets.reload} />}
            {assets.data && <Suspense fallback={<ChartSkeleton compact />}><AssetChart items={assets.data.items} emptyLabel={locale.panels.assets.empty} chartLabel={locale.panels.assets.title} language={language} compact /></Suspense>}
          </Panel>

          <section ref={genderPositionsRef} className="dashboard-card min-w-0 p-6 sm:p-8" aria-labelledby="gender-positions-title">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-[#b24b67]">{locale.panels.genderPositions.eyebrow}</p>
            <div className="mt-2">
              <h3 id="gender-positions-title" className="text-xl font-bold tracking-tight text-ink">{locale.panels.genderPositions.title}</h3>
              <p className="mt-3 text-sm leading-6 text-slate-500">{locale.panels.genderPositions.description}</p>
              <div className="mt-5">
                {(!deferred || gender.loading || !genderPositionsVisible) && <ChartSkeleton compact />}
                {gender.error && <SliceError onRetry={gender.reload} />}
                {gender.data && genderPositionsVisible && <Suspense fallback={<ChartSkeleton compact />}><GenderPositionChart positions={gender.data.positions} emptyLabel={locale.panels.genderPositions.empty} language={language} chartLabel={locale.accessibility.genderPositionsChart} legendLabel={locale.accessibility.genderPositionsLegend} womenLabel={locale.panels.genderPositions.women} parityLabel={locale.panels.genderPositions.parity} peopleLabel={locale.panels.genderPositions.people} noteLabel={locale.panels.genderPositions.note} compact /></Suspense>}
              </div>
            </div>
          </section>
        </div>
      </section>

      <section className="mt-16 grid items-stretch gap-5 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)]" aria-label={locale.homepage.supportingEvidence}>
        <Panel title={locale.panels.declarationTypes.title} eyebrow={locale.panels.declarationTypes.eyebrow} description={locale.homepage.evidence.declarationsDescription}>
          {(!deferred || declarations.loading) && <ChartSkeleton compact table />}
          {declarations.error && <SliceError onRetry={declarations.reload} />}
          {declarations.data && <DeclarationTable data={declarations.data} language={language} />}
        </Panel>
        <div className="flex h-full flex-col gap-5">
          <Panel className="lg:flex-1" title={locale.panels.snapshotMeaning.title} eyebrow={locale.panels.snapshotMeaning.eyebrow} description={locale.homepage.evidence.methodDescription}>
            <SnapshotMeaning overview={overview} loading={!deferred && !overview} language={language} />
          </Panel>
          <Panel title={locale.panels.snapshotCoverage.title} eyebrow={locale.panels.snapshotCoverage.eyebrow} description={locale.panels.snapshotCoverage.description}>
            <SnapshotCoverage overview={overview} loading={!overview} language={language} />
          </Panel>
        </div>
      </section>

      <section className="mt-16" aria-labelledby="explore-next-title">
        <div className="max-w-2xl">
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-emerald">{locale.homepage.exploreNext.eyebrow}</p>
          <h2 id="explore-next-title" className="mt-3 text-2xl font-black tracking-[-0.04em] text-ink sm:text-3xl">{locale.homepage.exploreNext.title}</h2>
          <p className="mt-3 text-sm leading-6 text-slate-500">{locale.homepage.exploreNext.description}</p>
        </div>
        <div className="mt-7 grid gap-4 md:grid-cols-3">
          <HomepageRouteCard to="/explore" tone="emerald" eyebrow={locale.homepage.exploreNext.highlightsEyebrow} title={locale.homepage.exploreNext.highlightsTitle} description={locale.homepage.exploreNext.highlightsDescription} action={locale.homepage.exploreNext.open} />
          <HomepageRouteCard to="/search" tone="sky" eyebrow={locale.homepage.exploreNext.searchEyebrow} title={locale.homepage.exploreNext.searchTitle} description={locale.homepage.exploreNext.searchDescription} action={locale.homepage.exploreNext.open} />
          <HomepageRouteCard to="/about" tone="violet" eyebrow={locale.homepage.exploreNext.methodsEyebrow} title={locale.homepage.exploreNext.methodsTitle} description={locale.homepage.exploreNext.methodsDescription} action={locale.homepage.exploreNext.open} />
        </div>
      </section>
    </>
  );
}
