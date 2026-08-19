import { formatNumber } from "../formatters";
import { useI18n } from "../context/I18nContext";
import type { DashboardOverviewResponse } from "../types";

export function DashboardHero({ overview, loading }: { overview: DashboardOverviewResponse | null; loading: boolean }) {
  const { language, locale } = useI18n();
  const totalRows = overview ? Object.values(overview.tables).reduce((sum, value) => sum + value, 0) : null;

  return (
    <section className="hero-grid relative isolate overflow-hidden rounded-[2rem] bg-ink px-6 py-10 text-white shadow-soft sm:px-10 sm:py-14">
      <div className="absolute -right-20 -top-32 size-[30rem] rounded-full bg-emerald/10 blur-3xl" aria-hidden="true" />
      <div className="relative z-10 grid gap-10 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-xs font-bold uppercase tracking-[0.16em] text-lime"><span className="size-2 rounded-full bg-lime" /> {locale.hero.eyebrow}</div>
          <h1 className="mt-7 max-w-xl text-4xl font-black leading-[1.02] tracking-[-0.05em] sm:text-6xl">{locale.hero.title}</h1>
          <p className="mt-5 max-w-xl text-base leading-7 text-slate-300">{locale.hero.description}</p>
        </div>
        <div className="flex flex-wrap gap-3 text-sm lg:max-w-sm lg:justify-end">
        <span className="rounded-full bg-white/10 px-4 py-2 font-semibold text-slate-200">{locale.hero.snapshot} {loading ? <span className="loading-shell-dark inline-block h-4 w-24 rounded-full align-middle" /> : overview?.snapshotDate ?? locale.hero.notAvailable}</span>
        <span className="rounded-full bg-lime px-4 py-2 font-bold text-ink">{loading ? <span className="loading-shell-dark inline-block h-4 w-28 rounded-full align-middle" /> : totalRows === null ? locale.hero.notAvailable : formatNumber(totalRows, language)} {!loading && totalRows !== null ? locale.hero.totalRows : ""}</span>
        </div>
      </div>
    </section>
  );
}
