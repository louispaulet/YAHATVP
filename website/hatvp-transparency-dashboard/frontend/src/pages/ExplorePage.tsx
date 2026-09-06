import { CalendarDays, FilePenLine, ShieldCheck, TrendingUp } from "lucide-react";
import { fetchHighlights } from "../api";
import { AmendedHighlightCard } from "../components/AmendedHighlightCard";
import { ExploreCardSkeleton, SliceError } from "../components/Feedback";
import { HighlightSection } from "../components/HighlightSection";
import { IncomeHighlightCard } from "../components/IncomeHighlightCard";
import { useI18n } from "../context/I18nContext";
import { useResource } from "../hooks/useResource";
import type { DashboardHighlightsResponse } from "../types";
import { SnapshotContext } from "../components/SnapshotContext";

export function ExplorePage() {
  const { language, locale } = useI18n();
  const highlights = useResource<DashboardHighlightsResponse>(fetchHighlights);
  return (
    <div className="mx-auto max-w-7xl space-y-20 px-5 py-8 sm:px-6 lg:px-8 lg:py-14">
      <section className="explore-hero overflow-hidden bg-ink text-white">
        <div className="relative z-10 max-w-3xl">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-lime">{locale.explore.eyebrow}</p>
          <h1 className="mt-5 text-4xl font-black leading-[1.02] tracking-[-0.05em] sm:text-6xl">{locale.explore.title}</h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-slate-300">{locale.explore.description}</p>
        </div>
        <div className="explore-hero-meta relative z-10">
          <div className="explore-meta-card">
            <span className="explore-meta-icon explore-meta-icon--lime"><CalendarDays size={18} strokeWidth={1.8} aria-hidden="true" /></span>
            <div>
              <span className="explore-meta-label">{locale.explore.snapshot}</span>
              <strong className="explore-meta-value tabular-nums">{highlights.data?.snapshotDate ?? locale.hero.notAvailable}</strong>
            </div>
          </div>
          <div className="explore-meta-card explore-meta-card--method">
            <span className="explore-meta-icon explore-meta-icon--lime"><ShieldCheck size={18} strokeWidth={1.8} aria-hidden="true" /></span>
            <span className="explore-meta-label">{locale.explore.method}</span>
          </div>
        </div>
      </section>
      {highlights.data && <SnapshotContext snapshotDate={highlights.data.snapshotDate} generatedAt={highlights.data.generatedAt} language={language} labels={locale.snapshotContext} sourceScope={locale.snapshotContext.officialScope} />}
      <nav className="flex flex-wrap gap-2 text-sm font-bold" aria-label={locale.explore.contentsLabel}>
        <a className="rounded-full bg-surface-subtle px-3 py-2 text-ink hover:bg-lime focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald" href="#income-signals">{locale.explore.incomeTitle}</a>
        <a className="rounded-full bg-surface-subtle px-3 py-2 text-ink hover:bg-lime focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald" href="#amended-signals">{locale.explore.amendedTitle}</a>
      </nav>
      {highlights.loading && <div className="explore-card-grid" aria-busy="true"><ExploreCardSkeleton /><ExploreCardSkeleton /><ExploreCardSkeleton /><ExploreCardSkeleton /></div>}
      {highlights.error && <SliceError onRetry={highlights.reload} />}
      {highlights.data && <>
        <HighlightSection id="income-signals" tone="income" icon={TrendingUp} eyebrow={locale.explore.incomeEyebrow} title={locale.explore.incomeTitle} description={locale.explore.incomeDescription} countLabel={`${highlights.data.incomeChanges.length} ${locale.explore.recordsLabel}`} meaning={locale.explore.incomeMeaning} meaningTitle={locale.explore.meaningTitle}>
          {highlights.data.incomeChanges.map((item, index) => <IncomeHighlightCard key={`${item.declarationUuid}-${item.toYear}`} item={item} rank={index + 1} />)}
        </HighlightSection>
        <HighlightSection id="amended-signals" tone="amended" icon={FilePenLine} eyebrow={locale.explore.amendedEyebrow} title={locale.explore.amendedTitle} description={locale.explore.amendedDescription} countLabel={`${highlights.data.amendedRecords.length} ${locale.explore.recordsLabel}`} meaning={locale.explore.amendedMeaning} meaningTitle={locale.explore.meaningTitle}>
          {highlights.data.amendedRecords.map((item, index) => <AmendedHighlightCard key={`${item.declarationUuid}-${index}`} item={item} rank={index + 1} />)}
        </HighlightSection>
      </>}
    </div>
  );
}
