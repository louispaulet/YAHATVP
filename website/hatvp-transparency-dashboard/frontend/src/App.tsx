import { createContext, lazy, Suspense, useContext, useEffect, useState } from "react";
import { NavLink, Route, Routes, useParams, useSearchParams } from "react-router-dom";
import { fetchAssets, fetchDeclaration, fetchDeclarations, fetchIncome, fetchOverview, fetchSearch } from "./api";
import { defaultLanguage, getLocale, languages, translateDataLabel, type Language, type Locale } from "./config/i18n";
import { formatNumber } from "./formatters";
import type { DashboardBreakdownResponse, DashboardDeclarationResponse, DashboardOverviewResponse, DashboardSearchResponse, DeclarationSearchResult } from "./types";

interface I18nContextValue {
  language: Language;
  locale: Locale;
  setLanguage: (language: Language) => void;
}

const I18nContext = createContext<I18nContextValue | null>(null);

function useI18n(): I18nContextValue {
  const context = useContext(I18nContext);
  if (!context) throw new Error("useI18n must be used within the I18n provider");
  return context;
}

function formatDateTime(value: string, language: Language): string {
  return new Date(value).toLocaleString(language === "fr" ? "fr-FR" : "en-GB");
}

function readLanguagePreference(): Language {
  try {
    return window.localStorage.getItem("hatvp-language") === "fr" ? "fr" : defaultLanguage;
  } catch {
    return defaultLanguage;
  }
}

interface ResourceState<T> {
  data: T | null;
  error: boolean;
  loading: boolean;
  reload: () => void;
}

function useResource<T>(loader: (signal: AbortSignal) => Promise<T>): ResourceState<T> {
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState<Omit<ResourceState<T>, "reload">>({
    data: null,
    error: false,
    loading: true,
  });

  useEffect(() => {
    const controller = new AbortController();
    setState((current) => ({ ...current, loading: true, error: false }));
    loader(controller.signal)
      .then((data) => setState({ data, error: false, loading: false }))
      .catch((reason: unknown) => {
        if (reason instanceof DOMException && reason.name === "AbortError") return;
        setState((current) => ({ ...current, error: true, loading: false }));
      });
    return () => controller.abort();
  }, [attempt, loader]);

  return { ...state, reload: () => setAttempt((value) => value + 1) };
}

function useSearchResource(query: string): ResourceState<DashboardSearchResponse> {
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState<Omit<ResourceState<DashboardSearchResponse>, "reload">>({
    data: null,
    error: false,
    loading: false,
  });

  useEffect(() => {
    if (!query) {
      setState({ data: null, error: false, loading: false });
      return;
    }
    const controller = new AbortController();
    setState((current) => ({ ...current, loading: true, error: false }));
    fetchSearch(query, controller.signal)
      .then((data) => setState({ data, error: false, loading: false }))
      .catch((reason: unknown) => {
        if (reason instanceof DOMException && reason.name === "AbortError") return;
        setState((current) => ({ ...current, error: true, loading: false }));
      });
    return () => controller.abort();
  }, [attempt, query]);

  return { ...state, reload: () => setAttempt((value) => value + 1) };
}

function useDeclarationResource(uuid: string): ResourceState<DashboardDeclarationResponse> {
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState<Omit<ResourceState<DashboardDeclarationResponse>, "reload">>({
    data: null,
    error: false,
    loading: false,
  });

  useEffect(() => {
    if (!uuid) {
      setState({ data: null, error: false, loading: false });
      return;
    }
    const controller = new AbortController();
    setState((current) => ({ ...current, loading: true, error: false }));
    fetchDeclaration(uuid, controller.signal)
      .then((data) => setState({ data, error: false, loading: false }))
      .catch((reason: unknown) => {
        if (reason instanceof DOMException && reason.name === "AbortError") return;
        setState((current) => ({ ...current, error: true, loading: false }));
      });
    return () => controller.abort();
  }, [attempt, uuid]);

  return { ...state, reload: () => setAttempt((value) => value + 1) };
}

function navClass({ isActive }: { isActive: boolean }): string {
  return isActive
    ? "relative px-1 py-2 text-sm font-semibold text-ink transition after:absolute after:inset-x-1 after:-bottom-[0.35rem] after:h-0.5 after:rounded-full after:bg-emerald focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-emerald"
    : "relative px-1 py-2 text-sm font-semibold text-slate-500 transition hover:text-ink focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-emerald";
}

const IncomeAssetsChart = lazy(() => import("./charts").then(({ IncomeAssetsChart: Chart }) => ({ default: Chart })));
const AssetChart = lazy(() => import("./charts").then(({ AssetChart: Chart }) => ({ default: Chart })));

function LanguageSwitcher() {
  const { language, locale, setLanguage } = useI18n();

  return (
    <div className="flex items-center gap-1 rounded-full border border-slate-200 bg-slate-100/70 p-1" aria-label={locale.languageSwitcher.label}>
      {languages.map((option) => (
        <button
          key={option}
          type="button"
          aria-label={locale.languageSwitcher.options[option]}
          aria-pressed={language === option}
          title={locale.languageSwitcher.options[option]}
          onClick={() => setLanguage(option)}
          className={language === option ? "rounded-full bg-white px-2.5 py-1 text-xs font-bold text-ink shadow-sm" : "rounded-full px-2.5 py-1 text-xs font-bold text-slate-500 transition hover:bg-white hover:text-ink"}
        >
          {option.toUpperCase()}
        </button>
      ))}
    </div>
  );
}

function Layout({ children }: { children: React.ReactNode }) {
  const { locale } = useI18n();

  return (
    <div className="flex min-h-screen flex-col bg-canvas text-ink">
      <header className="border-b border-slate-200/80 bg-canvas/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-5 py-5 sm:flex-row sm:items-center sm:justify-between lg:px-8">
          <NavLink to="/" className="flex items-center gap-3">
            <span className="flex size-10 items-center justify-center rounded-2xl bg-emerald/10 text-2xl leading-none" aria-hidden="true">⚖️</span>
            <span>
              <span className="block text-xs font-bold uppercase tracking-[0.22em] text-slate-500">HATVP</span>
              <span className="block text-sm font-semibold">{locale.brand.name}</span>
            </span>
          </NavLink>
          <div className="flex flex-wrap items-center justify-between gap-x-6 gap-y-2 sm:justify-end">
            <nav aria-label={locale.nav.label} className="flex flex-wrap items-center gap-x-4 gap-y-1 sm:gap-x-6">
              <NavLink to="/" end className={navClass}>{locale.nav.overview}</NavLink>
              <NavLink to="/search" className={navClass}>{locale.nav.search}</NavLink>
              <NavLink to="/explore" className={navClass}>{locale.nav.explore}</NavLink>
              <NavLink to="/about" className={navClass}>{locale.nav.about}</NavLink>
            </nav>
            <LanguageSwitcher />
          </div>
        </div>
      </header>
      <main className="flex-1">{children}</main>
      <footer className="mt-auto border-t border-slate-200/80">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-5 py-8 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between lg:px-8">
          <span>{locale.footer.builtFrom}</span>
          <div className="flex flex-wrap gap-x-4 gap-y-2">
            <a className="font-semibold text-slate-700 underline decoration-lime underline-offset-4" href="https://github.com/louispaulet/YAHATVP/tree/main" target="_blank" rel="noreferrer">
              {locale.footer.project}
            </a>
            <a className="font-semibold text-slate-700 underline decoration-lime underline-offset-4" href="https://www.hatvp.fr/" target="_blank" rel="noreferrer">
              hatvp.fr
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

function MetricCard({ label, value, detail, accent, language }: { label: string; value: number; detail: string; accent: string; language: Language }) {
  return (
    <article className="dashboard-card relative overflow-hidden p-6">
      <span className={`absolute inset-x-0 top-0 h-1 ${accent}`} />
      <p className="text-sm font-semibold text-slate-500">{label}</p>
      <p className="mt-4 text-4xl font-black tracking-tight text-ink">{formatNumber(value, language)}</p>
      <p className="mt-2 text-xs font-medium uppercase tracking-[0.14em] text-slate-400">{detail}</p>
    </article>
  );
}

function LoadingShell({ className }: { className: string }) {
  const { locale } = useI18n();
  return <div className={`loading-shell ${className}`} role="status" aria-label={locale.loading.label} />;
}

function SliceError({ onRetry }: { onRetry: () => void }) {
  const { locale } = useI18n();
  return (
    <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5 text-sm text-amber-950">
      <p>{locale.errors.sliceLoad}</p>
      <button type="button" onClick={onRetry} className="mt-3 rounded-full bg-ink px-4 py-2 text-xs font-bold text-white transition hover:bg-slate-700">
        {locale.errors.tryAgain}
      </button>
    </div>
  );
}

function Panel({ title, eyebrow, children }: { title: string; eyebrow: string; children: React.ReactNode }) {
  return (
    <section className="dashboard-card p-6 sm:p-7">
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{eyebrow}</p>
      <h2 className="mt-2 text-xl font-black tracking-tight text-ink">{title}</h2>
      <div className="mt-6">{children}</div>
    </section>
  );
}

function MetricSkeleton() {
  return (
    <article className="dashboard-card p-6">
      <LoadingShell className="h-4 w-28 rounded-full" />
      <LoadingShell className="mt-5 h-10 w-32 rounded-xl" />
      <LoadingShell className="mt-3 h-3 w-24 rounded-full" />
    </article>
  );
}

function ChartSkeleton({ table = false }: { table?: boolean }) {
  return (
    <div className="space-y-4" aria-busy="true">
      <LoadingShell className={table ? "h-4 w-3/4 rounded-full" : "h-56 w-full rounded-[1.5rem]"} />
      {table && <><LoadingShell className="h-4 w-full rounded-full" /><LoadingShell className="h-4 w-5/6 rounded-full" /><LoadingShell className="h-4 w-2/3 rounded-full" /></>}
    </div>
  );
}

function SourceLinkCard({ link }: { link: Locale["about"]["sources"]["links"][number] }) {
  const isDownload = link.kind === "download";
  const actionIcon = isDownload ? "↓" : "↗";
  const cardClass = isDownload ? "hover:border-emerald/40 hover:shadow-soft" : "hover:border-slate-300 hover:shadow-soft";
  const badgeClass = isDownload ? "bg-lime/60 text-ink" : "bg-slate-100 text-slate-500";
  const iconClass = isDownload ? "bg-emerald text-white" : "bg-slate-100 text-slate-600";

  return (
    <a
      className={`dashboard-card group flex h-full flex-col p-5 transition hover:-translate-y-0.5 ${cardClass}`}
      href={link.href}
      target={isDownload ? undefined : "_blank"}
      rel={isDownload ? undefined : "noreferrer"}
      download={isDownload ? "" : undefined}
    >
      <span className="flex flex-wrap items-start justify-between gap-3">
        <span className="min-w-0 flex-1 text-sm font-bold text-ink">{link.label}</span>
        <span className={`max-w-full rounded-full px-2.5 py-1 text-center text-[0.65rem] font-bold uppercase leading-5 tracking-[0.12em] ${badgeClass}`}>{link.type}</span>
      </span>
      <span className="mt-3 block text-sm leading-6 text-slate-500">{link.description}</span>
      <span className="mt-auto flex items-center gap-2 border-t border-slate-100 pt-5 text-xs font-bold uppercase tracking-[0.12em] text-slate-700">
        <span aria-hidden="true" className={`inline-flex size-7 items-center justify-center rounded-full text-base ${iconClass}`}>{actionIcon}</span>
        {link.action}
      </span>
    </a>
  );
}

function DashboardPage() {
  const { language, locale } = useI18n();
  const overview = useResource<DashboardOverviewResponse>(fetchOverview);
  const income = useResource<DashboardBreakdownResponse>(fetchIncome);
  const assets = useResource<DashboardBreakdownResponse>(fetchAssets);
  const declarations = useResource<DashboardBreakdownResponse>(fetchDeclarations);
  const totalRows = overview.data ? Object.values(overview.data.tables).reduce((sum, value) => sum + value, 0) : null;

  return (
    <div className="mx-auto max-w-7xl px-5 py-10 lg:px-8 lg:py-14">
      <section className="hero-grid overflow-hidden rounded-[2rem] bg-ink px-6 py-9 text-white shadow-soft sm:px-10 sm:py-12">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-xs font-bold uppercase tracking-[0.16em] text-lime">
            <span className="size-2 rounded-full bg-lime" /> {locale.hero.eyebrow}
          </div>
          <h1 className="mt-7 max-w-xl text-4xl font-black leading-[1.02] tracking-[-0.04em] sm:text-6xl">{locale.hero.title}</h1>
          <p className="mt-5 max-w-lg text-base leading-7 text-slate-300">{locale.hero.description}</p>
        </div>
        <div className="relative z-10 mt-10 flex flex-wrap gap-3 text-sm sm:mt-0 sm:justify-end">
          <span className="rounded-full bg-white/10 px-4 py-2 font-semibold text-slate-200">
            {locale.hero.snapshot} {overview.loading ? <span className="loading-shell-dark inline-block h-4 w-24 rounded-full align-middle" /> : overview.data?.snapshotDate ?? locale.hero.notAvailable}
          </span>
          <span className="rounded-full bg-lime px-4 py-2 font-bold text-ink">
            {overview.loading ? <span className="loading-shell-dark inline-block h-4 w-28 rounded-full align-middle" /> : totalRows === null ? locale.hero.notAvailable : formatNumber(totalRows, language)} {overview.loading || totalRows !== null ? locale.hero.totalRows : ""}
          </span>
        </div>
      </section>

      <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {overview.loading && [0, 1, 2, 3].map((key) => <MetricSkeleton key={key} />)}
        {overview.error && <div className="sm:col-span-2 lg:col-span-4"><SliceError onRetry={overview.reload} /></div>}
        {overview.data && <>
          <MetricCard language={language} label={locale.metrics.declarations.label} value={overview.data.tables.declarations} detail={locale.metrics.declarations.detail} accent="bg-emerald" />
          <MetricCard language={language} label={locale.metrics.people.label} value={overview.data.tables.people} detail={locale.metrics.people.detail} accent="bg-lime" />
          <MetricCard language={language} label={locale.metrics.incomes.label} value={overview.data.tables.incomes} detail={locale.metrics.incomes.detail} accent="bg-sky" />
          <MetricCard language={language} label={locale.metrics.assets.label} value={overview.data.tables.assets} detail={locale.metrics.assets.detail} accent="bg-violet" />
        </>}
      </section>

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

      <section className="mt-6 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <Panel title={locale.panels.declarationTypes.title} eyebrow={locale.panels.declarationTypes.eyebrow}>
          {declarations.loading && <ChartSkeleton table />}
          {declarations.error && <SliceError onRetry={declarations.reload} />}
          {declarations.data && <div className="overflow-x-auto">
            <table className="w-full min-w-[22rem] text-left text-sm">
              <thead className="border-b border-slate-200 text-xs uppercase tracking-[0.14em] text-slate-400"><tr><th className="pb-3 font-bold">{locale.panels.declarationTypes.type}</th><th className="pb-3 text-right font-bold">{locale.panels.declarationTypes.rows}</th></tr></thead>
              <tbody className="divide-y divide-slate-100">{declarations.data.items.map((item) => <tr key={item.label}><td className="py-3 font-semibold text-slate-700">{translateDataLabel(language, "declarationTypes", item.label)}</td><td className="py-3 text-right font-bold text-ink">{formatNumber(item.rows, language)}</td></tr>)}</tbody>
            </table>
            {declarations.data.items.length === 0 && <p className="py-6 text-sm text-slate-500">{locale.panels.declarationTypes.empty}</p>}
          </div>}
        </Panel>
        <Panel title={locale.panels.snapshotMeaning.title} eyebrow={locale.panels.snapshotMeaning.eyebrow}>
          <div className="space-y-4 text-sm leading-6 text-slate-600">
            <p>{locale.panels.snapshotMeaning.counts}</p>
            <p>{locale.panels.snapshotMeaning.amounts}</p>
            <p className="rounded-2xl bg-lime/30 p-4 font-semibold text-ink">
              {locale.panels.snapshotMeaning.lastGenerated}: {overview.loading ? <span className="loading-shell inline-block h-4 w-32 rounded-full align-middle" /> : overview.data ? formatDateTime(overview.data.generatedAt, language) : locale.hero.notAvailable}
            </p>
          </div>
        </Panel>
      </section>
    </div>
  );
}

function AboutPage() {
  const { locale } = useI18n();
  return (
    <div className="mx-auto max-w-3xl px-5 py-16 lg:px-8 lg:py-24">
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.about.eyebrow}</p>
      <h1 className="mt-4 text-4xl font-black tracking-tight sm:text-5xl">{locale.about.title}</h1>
      <div className="mt-8 space-y-6 text-base leading-8 text-slate-600">
        {locale.about.paragraphs.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
        <p>{locale.about.sourcePrefix}</p>
      </div>
      <section className="mt-12">
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.about.sources.eyebrow}</p>
        <h2 className="mt-2 text-2xl font-black tracking-tight text-ink">{locale.about.sources.title}</h2>
        <p className="mt-3 text-sm leading-6 text-slate-600">{locale.about.sources.description}</p>
        <div className="mt-5 grid gap-4 sm:grid-cols-3">
          {locale.about.sources.links.map((link) => <SourceLinkCard key={link.href} link={link} />)}
        </div>
      </section>
      <a className="dashboard-card group mt-6 block p-5 transition hover:-translate-y-0.5 hover:border-emerald/40 hover:shadow-soft" href={locale.about.project.href} target="_blank" rel="noreferrer">
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.about.project.eyebrow}</p>
        <span className="mt-2 flex items-start justify-between gap-3 text-sm font-bold text-ink"><span>{locale.about.project.title}</span><span aria-hidden="true" className="text-emerald transition group-hover:translate-x-0.5">↗</span></span>
        <span className="mt-3 block text-sm leading-6 text-slate-500">{locale.about.project.description}</span>
      </a>
      <div className="mt-10 grid gap-4 sm:grid-cols-2">
        <div className="dashboard-card p-5"><p className="text-xs font-bold uppercase tracking-[0.14em] text-slate-400">{locale.about.curatedTables}</p><p className="mt-2 text-2xl font-black">4</p><p className="mt-1 text-sm text-slate-500">{locale.about.curatedTablesDetail}</p></div>
        <div className="dashboard-card p-5"><p className="text-xs font-bold uppercase tracking-[0.14em] text-slate-400">{locale.about.updateRhythm}</p><p className="mt-2 text-2xl font-black">{locale.about.updateRhythmValue}</p><p className="mt-1 text-sm text-slate-500">{locale.about.updateRhythmDetail}</p></div>
      </div>
    </div>
  );
}

function ExplorePage() {
  const { locale } = useI18n();
  return (
    <div className="mx-auto max-w-3xl px-5 py-16 lg:px-8 lg:py-24">
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.explore.eyebrow}</p>
      <h1 className="mt-4 text-4xl font-black tracking-tight sm:text-5xl">{locale.explore.title}</h1>
      <p className="mt-8 max-w-2xl text-base leading-8 text-slate-600">{locale.explore.description}</p>
      <div className="dashboard-card mt-10 border-dashed p-6 sm:p-8">
        <p className="text-sm font-bold uppercase tracking-[0.14em] text-slate-400">{locale.explore.status}</p>
        <p className="mt-3 text-lg font-semibold text-ink">{locale.explore.next}</p>
      </div>
    </div>
  );
}

function searchValue(value: string | null, fallback: string): string {
  return value?.trim() || fallback;
}

function declarationName(result: DeclarationSearchResult, fallback: string): string {
  return [result.civilite, result.firstName, result.lastName].filter(Boolean).join(" ") || fallback;
}

function SearchResultCard({ result }: { result: DeclarationSearchResult }) {
  const { language, locale } = useI18n();
  const name = declarationName(result, locale.search.unknownDeclarant);
  const date = result.dateDeposited
    ? new Date(`${result.dateDeposited}T00:00:00`).toLocaleDateString(language === "fr" ? "fr-FR" : "en-GB")
    : locale.search.notAvailable;
  const declarationType = result.declarationType
    ? translateDataLabel(language, "declarationTypes", result.declarationType)
    : locale.search.notAvailable;

  return (
    <article className="dashboard-card p-5 transition hover:border-emerald/40 hover:shadow-soft sm:p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-emerald">{locale.search.resultEyebrow}</p>
          <h2 className="mt-2 text-xl font-black tracking-tight text-ink">{name}</h2>
        </div>
        <span className="max-w-full rounded-full bg-lime/60 px-3 py-1.5 text-xs font-bold leading-5 text-ink sm:text-right">{declarationType}</span>
      </div>
      <dl className="mt-6 grid gap-x-5 gap-y-4 border-t border-slate-100 pt-5 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.search.fields.mandate}</dt>
          <dd className="mt-1 text-sm font-semibold text-slate-700">{searchValue(result.mandate, locale.search.notAvailable)}</dd>
        </div>
        <div>
          <dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.search.fields.organ}</dt>
          <dd className="mt-1 text-sm font-semibold text-slate-700">{searchValue(result.organ || result.organDeclaration, locale.search.notAvailable)}</dd>
        </div>
        <div>
          <dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.search.fields.date}</dt>
          <dd className="mt-1 text-sm font-semibold text-slate-700">{date}</dd>
        </div>
        <div>
          <dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.search.fields.identifier}</dt>
          <dd className="mt-1 break-all font-mono text-xs font-semibold text-slate-700">{searchValue(result.declarationUuid, locale.search.notAvailable)}</dd>
        </div>
      </dl>
      {result.declarationUuid && <NavLink to={`/declarations/${encodeURIComponent(result.declarationUuid)}`} className="mt-5 flex items-center justify-between border-t border-slate-100 pt-5 text-sm font-bold text-emerald transition hover:text-ink focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-emerald"><span>{locale.search.viewDeclaration}</span><span aria-hidden="true">↗</span></NavLink>}
    </article>
  );
}

function SearchPage() {
  const { language, locale } = useI18n();
  const [params, setParams] = useSearchParams();
  const query = params.get("q")?.trim() ?? "";
  const [input, setInput] = useState(query);
  const search = useSearchResource(query);

  useEffect(() => setInput(query), [query]);

  function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextQuery = input.trim();
    setParams(nextQuery ? { q: nextQuery } : {});
  }

  return (
    <div className="mx-auto max-w-5xl px-5 py-12 lg:px-8 lg:py-16">
      <section className="hero-grid overflow-hidden rounded-[2rem] bg-ink px-6 py-9 text-white shadow-soft sm:px-10 sm:py-11">
        <p className="relative z-10 text-xs font-bold uppercase tracking-[0.18em] text-lime">{locale.search.eyebrow}</p>
        <h1 className="relative z-10 mt-4 max-w-3xl text-4xl font-black leading-[1.04] tracking-[-0.04em] sm:text-5xl">{locale.search.title}</h1>
        <p className="relative z-10 mt-5 max-w-2xl text-base leading-7 text-slate-300">{locale.search.description}</p>
      </section>

      <section className="dashboard-card relative z-10 -mt-5 p-5 sm:p-6">
        <form onSubmit={submit}>
          <label htmlFor="declaration-search" className="text-sm font-bold text-ink">{locale.search.inputLabel}</label>
          <div className="mt-3 flex flex-col gap-3 sm:flex-row">
            <div className="flex min-w-0 flex-1 items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3 transition focus-within:border-emerald focus-within:ring-4 focus-within:ring-emerald/10">
              <span aria-hidden="true" className="text-xl text-emerald">⌕</span>
              <input
                id="declaration-search"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder={locale.search.placeholder}
                maxLength={120}
                className="min-w-0 flex-1 bg-transparent text-sm font-semibold text-ink outline-none placeholder:font-normal placeholder:text-slate-400"
              />
            </div>
            <button type="submit" className="rounded-2xl bg-emerald px-6 py-3 text-sm font-bold text-white transition hover:bg-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald">
              {locale.search.submit}
            </button>
          </div>
          <p className="mt-3 text-xs leading-5 text-slate-500">{locale.search.hint}</p>
        </form>
      </section>

      {!query && <section className="dashboard-card mt-8 border-dashed p-6 sm:p-8"><p className="text-sm font-bold uppercase tracking-[0.14em] text-slate-400">{locale.search.emptyTitle}</p><p className="mt-3 text-lg font-semibold text-ink">{locale.search.emptyDescription}</p></section>}
      {query && search.loading && <section className="mt-8 space-y-4" aria-busy="true"><LoadingShell className="h-36 w-full rounded-[1.5rem]" /><LoadingShell className="h-36 w-full rounded-[1.5rem]" /></section>}
      {query && search.error && <section className="mt-8"><SliceError onRetry={search.reload} /></section>}
      {query && search.data && search.data.results.length === 0 && <section className="dashboard-card mt-8 border-dashed p-6 sm:p-8"><p className="text-sm font-bold uppercase tracking-[0.14em] text-slate-400">{locale.search.noResultsEyebrow}</p><p className="mt-3 text-lg font-semibold text-ink">{locale.search.noResults.replace("{query}", query)}</p></section>}
      {query && search.data && search.data.results.length > 0 && <section className="mt-8"><div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between"><div><p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.search.resultsEyebrow}</p><h2 className="mt-2 text-2xl font-black tracking-tight text-ink">{locale.search.resultsFound.replace("{count}", formatNumber(search.data.resultCount, language))}</h2></div><p className="text-xs text-slate-500">{locale.search.snapshot.replace("{date}", search.data.snapshotDate || locale.search.notAvailable)}</p></div><div className="space-y-4">{search.data.results.map((result, index) => <SearchResultCard key={`${result.declarationUuid}-${index}`} result={result} />)}</div></section>}
    </div>
  );
}

function DeclarationPage() {
  const { language, locale } = useI18n();
  const { uuid = "" } = useParams();
  const declaration = useDeclarationResource(uuid);
  const result = declaration.data?.declaration;
  const name = result ? declarationName(result, locale.search.unknownDeclarant) : locale.search.unknownDeclarant;
  const date = result?.dateDeposited
    ? new Date(`${result.dateDeposited}T00:00:00`).toLocaleDateString(language === "fr" ? "fr-FR" : "en-GB")
    : locale.search.notAvailable;

  return (
    <div className="mx-auto max-w-6xl px-5 py-12 lg:px-8 lg:py-16">
      <NavLink to="/search" className="inline-flex items-center gap-2 text-sm font-bold text-emerald transition hover:text-ink focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-emerald"><span aria-hidden="true">←</span>{locale.declaration.back}</NavLink>
      <section className="mt-7 overflow-hidden rounded-[2rem] bg-ink px-6 py-9 text-white shadow-soft sm:px-10 sm:py-11">
        <p className="relative z-10 text-xs font-bold uppercase tracking-[0.18em] text-lime">{locale.declaration.eyebrow}</p>
        {declaration.loading && <><LoadingShell className="relative z-10 mt-5 h-10 w-2/3 rounded-xl" /><LoadingShell className="loading-shell-dark relative z-10 mt-4 h-5 w-1/2 rounded-full" /></>}
        {result && <><h1 className="relative z-10 mt-4 max-w-3xl text-4xl font-black leading-[1.04] tracking-[-0.04em] sm:text-5xl">{name}</h1><p className="relative z-10 mt-5 max-w-2xl text-base leading-7 text-slate-300">{locale.declaration.description}</p></>}
      </section>

      {declaration.error && <section className="mt-8"><SliceError onRetry={declaration.reload} /></section>}
      {result && <>
        <section className="dashboard-card relative z-10 -mt-5 p-5 sm:p-6">
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            <div><p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.search.fields.identifier}</p><p className="mt-1 break-all font-mono text-xs font-semibold text-slate-700">{searchValue(result.declarationUuid, locale.search.notAvailable)}</p></div>
            <div><p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.declaration.fields.type}</p><p className="mt-1 text-sm font-semibold text-slate-700">{searchValue(result.declarationType, locale.search.notAvailable)}</p></div>
            <div><p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.search.fields.mandate}</p><p className="mt-1 text-sm font-semibold text-slate-700">{searchValue(result.mandate, locale.search.notAvailable)}</p></div>
            <div><p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.search.fields.date}</p><p className="mt-1 text-sm font-semibold text-slate-700">{date}</p></div>
          </div>
        </section>
        {declaration.data && <section className="dashboard-card mt-8 overflow-hidden">
          <div className="flex flex-col gap-3 border-b border-slate-200 px-5 py-5 sm:flex-row sm:items-end sm:justify-between sm:px-6">
            <div><p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.declaration.sourceEyebrow}</p><h2 className="mt-2 text-2xl font-black tracking-tight text-ink">{locale.declaration.sourceTitle}</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">{locale.declaration.sourceDescription}</p></div>
            <span className="shrink-0 rounded-full bg-slate-100 px-3 py-1.5 text-xs font-bold text-slate-500">{formatNumber(declaration.data.rawXml.length, language)} {locale.declaration.characters}</span>
          </div>
          <pre aria-label={locale.declaration.rawXmlLabel} className="max-h-[70vh] overflow-auto bg-[#101815] p-5 text-xs leading-6 text-slate-200 sm:p-7"><code>{declaration.data.rawXml}</code></pre>
        </section>}
      </>}
    </div>
  );
}

function NotFoundPage() {
  const { locale } = useI18n();
  return <div className="mx-auto max-w-2xl px-5 py-24 text-center lg:px-8"><h1 className="text-4xl font-black">{locale.errors.notFound}</h1><NavLink className="mt-6 inline-block rounded-full bg-ink px-5 py-3 text-sm font-bold text-white" to="/">{locale.errors.backToOverview}</NavLink></div>;
}

export function App() {
  const [language, setLanguage] = useState<Language>(readLanguagePreference);
  const locale = getLocale(language);

  useEffect(() => {
    try {
      window.localStorage.setItem("hatvp-language", language);
    } catch {
      // Language switching still works when browser storage is unavailable.
    }
  }, [language]);

  return (
    <I18nContext.Provider value={{ language, locale, setLanguage }}>
      <Layout><Routes><Route path="/" element={<DashboardPage />} /><Route path="/search" element={<SearchPage />} /><Route path="/declarations/:uuid" element={<DeclarationPage />} /><Route path="/explore" element={<ExplorePage />} /><Route path="/about" element={<AboutPage />} /><Route path="*" element={<NotFoundPage />} /></Routes></Layout>
    </I18nContext.Provider>
  );
}
