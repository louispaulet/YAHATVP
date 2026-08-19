import { fetchHighlights } from "../api";
import { AmendedHighlightCard } from "../components/AmendedHighlightCard";
import { AssetHighlightCard } from "../components/AssetHighlightCard";
import { ChartSkeleton, SliceError } from "../components/Feedback";
import { HighlightSection } from "../components/HighlightSection";
import { IncomeHighlightCard } from "../components/IncomeHighlightCard";
import { useI18n } from "../context/I18nContext";
import { useResource } from "../hooks/useResource";
import type { DashboardHighlightsResponse } from "../types";

export function ExplorePage() {
  const { locale } = useI18n();
  const highlights = useResource<DashboardHighlightsResponse>(fetchHighlights);
  return (
    <div className="mx-auto max-w-7xl space-y-12 px-5 py-8 lg:px-8 lg:py-12">
      <section className="hero-grid overflow-hidden rounded-[2rem] bg-ink px-6 py-10 text-white shadow-soft sm:px-10 sm:py-14">
        <div className="max-w-3xl">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-lime">{locale.explore.eyebrow}</p>
          <h1 className="mt-5 text-4xl font-black leading-[1.02] tracking-[-0.05em] sm:text-6xl">{locale.explore.title}</h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-slate-300">{locale.explore.description}</p>
          <div className="mt-8 flex flex-wrap gap-3 text-xs font-bold"><span className="rounded-full bg-white/10 px-4 py-2">{locale.explore.snapshot} {highlights.data?.snapshotDate ?? locale.hero.notAvailable}</span><span className="rounded-full bg-lime px-4 py-2 text-ink">{locale.explore.method}</span></div>
        </div>
      </section>
      {highlights.loading && <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4"><ChartSkeleton /><ChartSkeleton /><ChartSkeleton /><ChartSkeleton /></div>}
      {highlights.error && <SliceError onRetry={highlights.reload} />}
      {highlights.data && <>
        <HighlightSection eyebrow={locale.explore.incomeEyebrow} title={locale.explore.incomeTitle} description={locale.explore.incomeDescription}>
          {highlights.data.incomeChanges.map((item, index) => <IncomeHighlightCard key={`${item.declarationUuid}-${item.toYear}`} item={item} rank={index + 1} />)}
        </HighlightSection>
        <HighlightSection eyebrow={locale.explore.assetsEyebrow} title={locale.explore.assetsTitle} description={locale.explore.assetsDescription}>
          {highlights.data.unusualAssets.map((item, index) => <AssetHighlightCard key={`${item.declarationUuid}-${index}`} item={item} rank={index + 1} />)}
        </HighlightSection>
        <HighlightSection eyebrow={locale.explore.amendedEyebrow} title={locale.explore.amendedTitle} description={locale.explore.amendedDescription}>
          {highlights.data.amendedRecords.map((item, index) => <AmendedHighlightCard key={`${item.declarationUuid}-${index}`} item={item} rank={index + 1} />)}
        </HighlightSection>
      </>}
    </div>
  );
}
