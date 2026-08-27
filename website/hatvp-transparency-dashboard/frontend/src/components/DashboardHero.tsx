import { ArrowRight, Search } from "lucide-react";
import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useI18n } from "../context/I18nContext";
import { formatDateTime, formatNumber } from "../formatters";
import type { DashboardOverviewResponse } from "../types";
import { LoadingShell, SliceError } from "./Feedback";

interface DashboardHeroProps {
  overview: DashboardOverviewResponse | null;
  loading: boolean;
  error?: boolean;
  onRetry?: () => void;
}

export function DashboardHero({ overview, loading, error = false, onRetry }: DashboardHeroProps) {
  const { language, locale } = useI18n();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const totalRows = overview ? Object.values(overview.tables).reduce((sum, value) => sum + value, 0) : null;

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = query.trim();
    navigate(value ? `/search?q=${encodeURIComponent(value)}` : "/search");
  }

  return (
    <section className="relative overflow-hidden rounded-[2rem] border border-emerald/15 bg-[#edf7ef] px-5 py-7 shadow-card-raised sm:px-8 sm:py-10 lg:px-12 lg:py-12">
      <div className="pointer-events-none absolute -right-24 -top-32 size-[27rem] rounded-full bg-lime/60 blur-3xl" aria-hidden="true" />
      <div className="relative grid gap-10 lg:grid-cols-[minmax(0,1fr)_minmax(19rem,0.58fr)] lg:items-end lg:gap-14">
        <div className="max-w-3xl">
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-emerald">{locale.hero.eyebrow}</p>
          <h1 className="mt-5 max-w-2xl text-[clamp(2.65rem,7vw,5.7rem)] font-black leading-[0.94] tracking-[-0.07em] text-ink">{locale.hero.title}</h1>
          <p className="mt-6 max-w-2xl text-base leading-7 text-slate-600 sm:text-lg sm:leading-8">{locale.hero.description}</p>

          <form className="mt-8 max-w-2xl" onSubmit={submitSearch}>
            <label className="sr-only" htmlFor="homepage-search">{locale.hero.searchLabel}</label>
            <div className="flex flex-col gap-2 rounded-2xl border border-ink/15 bg-white p-2 shadow-card sm:flex-row sm:items-center">
              <div className="flex min-w-0 flex-1 items-center gap-3 px-3">
                <Search className="size-5 shrink-0 text-emerald" strokeWidth={2} aria-hidden="true" />
                <input
                  id="homepage-search"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder={locale.hero.searchPlaceholder}
                  className="min-w-0 flex-1 bg-transparent py-2.5 text-sm font-semibold text-ink outline-none placeholder:text-slate-400"
                />
              </div>
              <button type="submit" className="inline-flex items-center justify-center gap-2 rounded-xl bg-ink px-5 py-3 text-sm font-bold text-white transition hover:bg-emerald focus-visible:outline-2 focus-visible:outline-offset-3 focus-visible:outline-emerald">
                {locale.hero.searchSubmit}
                <ArrowRight className="size-4" strokeWidth={2.2} aria-hidden="true" />
              </button>
            </div>
          </form>

          <div className="mt-5 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm font-bold text-ink">
            <Link className="inline-flex items-center gap-2 underline decoration-emerald decoration-2 underline-offset-4 transition hover:text-emerald focus-visible:outline-2 focus-visible:outline-offset-3 focus-visible:outline-emerald" to="/explore">
              {locale.hero.primaryAction}
              <ArrowRight className="size-4" strokeWidth={2.2} aria-hidden="true" />
            </Link>
            <Link className="text-slate-600 underline decoration-lime decoration-2 underline-offset-4 transition hover:text-ink focus-visible:outline-2 focus-visible:outline-offset-3 focus-visible:outline-emerald" to="/about">{locale.hero.secondaryAction}</Link>
          </div>
        </div>

        <aside className="relative rounded-[1.5rem] bg-ink p-5 text-white shadow-soft sm:p-7" aria-label={locale.hero.snapshotDetails}>
          <div className="flex items-center justify-between gap-4 border-b border-white/15 pb-5">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-lime">{locale.hero.snapshot}</p>
            <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-slate-300">{locale.hero.liveCoverage}</span>
          </div>
          <dl className="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-1">
            <div>
              <dt className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">{locale.hero.snapshotDate}</dt>
              <dd className="mt-1 text-2xl font-black tracking-tight text-white">
                {loading ? <LoadingShell className="h-8 w-36 rounded-lg" /> : overview?.snapshotDate ?? locale.hero.notAvailable}
              </dd>
            </div>
            <div>
              <dt className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">{locale.hero.coverage}</dt>
              <dd className="mt-1 text-2xl font-black tracking-tight text-white">
                {loading || totalRows === null ? <LoadingShell className="h-8 w-28 rounded-lg" /> : formatNumber(totalRows, language)}
              </dd>
              <p className="mt-1 text-xs text-slate-400">{locale.hero.coverageDetail}</p>
            </div>
            <div className="border-t border-white/15 pt-4 sm:col-span-2 lg:col-span-1">
              <dt className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">{locale.hero.generated}</dt>
              <dd className="mt-1 text-sm font-semibold text-slate-200">
                {loading ? <LoadingShell className="h-5 w-44 rounded-md" /> : overview ? formatDateTime(overview.generatedAt, language) : locale.hero.notAvailable}
              </dd>
            </div>
          </dl>
          {error && onRetry && <div className="mt-6"><SliceError onRetry={onRetry} /></div>}
        </aside>
      </div>
    </section>
  );
}
