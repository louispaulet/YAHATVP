import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import { fetchDashboard } from "./api";
import { defaultLanguage, getLocale, languages, translateDataLabel, type DataLabelCategory, type Language, type Locale } from "./config/i18n";
import type { BreakdownItem, DashboardResponse } from "./types";

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

function formatNumber(value: number, language: Language): string {
  return new Intl.NumberFormat(language === "fr" ? "fr-FR" : "en-GB").format(value);
}

function formatCurrency(value: number, language: Language): string {
  return new Intl.NumberFormat(language === "fr" ? "fr-FR" : "en-GB", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(value);
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

function navClass({ isActive }: { isActive: boolean }): string {
  return isActive
    ? "rounded-full bg-ink px-4 py-2 text-sm font-semibold text-white"
    : "rounded-full px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-white hover:text-ink";
}

const logoSrc = `${import.meta.env.BASE_URL}hatvp-mark.webp`;

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
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5 lg:px-8">
          <NavLink to="/" className="flex items-center gap-3">
            <img className="size-10 rounded-2xl object-cover" src={logoSrc} alt="" aria-hidden="true" />
            <span>
              <span className="block text-xs font-bold uppercase tracking-[0.22em] text-slate-500">HATVP</span>
              <span className="block text-sm font-semibold">{locale.brand.name}</span>
            </span>
          </NavLink>
          <div className="flex items-center gap-2">
            <nav className="flex items-center gap-1 rounded-full border border-slate-200 bg-slate-100/70 p-1">
              <NavLink to="/" end className={navClass}>{locale.nav.overview}</NavLink>
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

function BreakdownList({ items, currency, emptyLabel, labelCategory }: { items: BreakdownItem[]; currency: boolean; emptyLabel: string; labelCategory: DataLabelCategory }) {
  const { language, locale } = useI18n();
  const max = Math.max(...items.map((item) => Math.abs(item.totalValue ?? item.rows)), 1);
  if (items.length === 0) return <p className="py-8 text-sm text-slate-500">{emptyLabel}</p>;
  return (
    <div className="space-y-5">
      {items.map((item) => {
        const amount = item.totalValue ?? item.rows;
        const width = Math.max(4, Math.round((Math.abs(amount) / max) * 100));
        return (
          <div key={item.label}>
            <div className="mb-2 flex items-center justify-between gap-3 text-sm">
              <span className="truncate font-semibold text-slate-700">{translateDataLabel(language, labelCategory, item.label)}</span>
              <span className="shrink-0 font-bold text-ink">{currency ? formatCurrency(amount, language) : formatNumber(item.rows, language)}</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-slate-100">
              <div className="h-full rounded-full bg-emerald" style={{ width: `${width}%` }} />
            </div>
            <p className="mt-1 text-xs text-slate-400">{formatNumber(item.rows, language)} {locale.accessibility.rows}</p>
          </div>
        );
      })}
    </div>
  );
}

const pieColors = ["var(--color-emerald)", "var(--color-sky)"];

function IncomePieChart({ items, emptyLabel }: { items: BreakdownItem[]; emptyLabel: string }) {
  const { language, locale } = useI18n();
  if (items.length === 0) return <p className="py-8 text-sm text-slate-500">{emptyLabel}</p>;

  const values = items.map((item) => Math.max(0, item.totalValue ?? item.rows));
  const total = values.reduce((sum, value) => sum + value, 0);
  let cursor = 0;
  const segments = values.map((value, index) => {
    const share = total > 0 ? value / total : 1 / values.length;
    const start = cursor;
    cursor += share * 100;
    return `${pieColors[index % pieColors.length]} ${start}% ${cursor}%`;
  });
  const chartLabel = items
    .map((item, index) => {
      const percentage = total > 0 ? (values[index] / total) * 100 : 100 / values.length;
      return `${translateDataLabel(language, "incomeStreams", item.label)} ${formatCurrency(values[index], language)}, ${percentage.toFixed(1)}%`;
    })
    .join("; ");

  return (
    <div className="flex flex-col items-center gap-7 sm:flex-row sm:items-center">
      <div
        aria-label={`${locale.accessibility.incomeChart}: ${chartLabel}`}
        className="size-44 shrink-0 rounded-full shadow-inner ring-8 ring-white sm:size-52"
        role="img"
        style={{ background: `conic-gradient(${segments.join(", ")})` }}
      />
      <div className="w-full min-w-0 space-y-4" aria-label={locale.accessibility.incomeLegend}>
        {items.map((item, index) => {
          const amount = values[index];
          const percentage = total > 0 ? (amount / total) * 100 : 100 / values.length;
          return (
            <div key={item.label} className="flex items-start justify-between gap-4">
              <div className="flex min-w-0 items-start gap-2.5">
                <span
                  aria-hidden="true"
                  className="mt-1.5 size-3 shrink-0 rounded-full"
                  style={{ backgroundColor: pieColors[index % pieColors.length] }}
                />
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold text-slate-700">{translateDataLabel(language, "incomeStreams", item.label)}</p>
                  <p className="mt-1 text-xs text-slate-400">{formatNumber(item.rows, language)} {locale.accessibility.rows} · {percentage.toFixed(1)}%</p>
                </div>
              </div>
              <span className="shrink-0 text-right text-sm font-bold text-ink">{formatCurrency(amount, language)}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function IncomeBreakdown({ items, emptyLabel }: { items: BreakdownItem[]; emptyLabel: string }) {
  return items.length === 2 ? (
    <IncomePieChart items={items} emptyLabel={emptyLabel} />
  ) : (
    <BreakdownList items={items} currency labelCategory="incomeStreams" emptyLabel={emptyLabel} />
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
      <span className="flex items-start justify-between gap-3">
        <span className="text-sm font-bold text-ink">{link.label}</span>
        <span className={`shrink-0 rounded-full px-2.5 py-1 text-[0.65rem] font-bold uppercase tracking-[0.12em] ${badgeClass}`}>{link.type}</span>
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
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    setError(false);
    const controller = new AbortController();
    fetchDashboard(controller.signal)
      .then(setData)
      .catch((reason: unknown) => {
        if (reason instanceof DOMException && reason.name === "AbortError") return;
        setError(true);
      })
      .finally(() => setLoading(false));
    return () => controller.abort();
  };

  useEffect(() => load(), []);

  const totalRows = useMemo(() => data ? Object.values(data.tables).reduce((sum, value) => sum + value, 0) : 0, [data]);

  if (loading) {
    return <div className="mx-auto max-w-7xl px-5 py-16 lg:px-8"><div className="h-56 animate-pulse rounded-[2rem] bg-slate-200/70" /></div>;
  }
  if (error || !data) {
    return (
      <div className="mx-auto max-w-2xl px-5 py-24 text-center lg:px-8">
        <span className="text-5xl">◌</span>
        <h1 className="mt-6 text-3xl font-black">{locale.errors.title}</h1>
        <p className="mt-3 text-slate-600">{error ? locale.errors.load : locale.errors.noData}</p>
        <button onClick={load} className="mt-7 rounded-full bg-ink px-5 py-3 text-sm font-bold text-white transition hover:bg-slate-700">{locale.errors.tryAgain}</button>
      </div>
    );
  }

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
          <span className="rounded-full bg-white/10 px-4 py-2 font-semibold text-slate-200">{locale.hero.snapshot} {data.snapshotDate ?? locale.hero.notAvailable}</span>
          <span className="rounded-full bg-lime px-4 py-2 font-bold text-ink">{formatNumber(totalRows, language)} {locale.hero.totalRows}</span>
        </div>
      </section>

      <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard language={language} label={locale.metrics.declarations.label} value={data.tables.declarations} detail={locale.metrics.declarations.detail} accent="bg-emerald" />
        <MetricCard language={language} label={locale.metrics.people.label} value={data.tables.people} detail={locale.metrics.people.detail} accent="bg-lime" />
        <MetricCard language={language} label={locale.metrics.incomes.label} value={data.tables.incomes} detail={locale.metrics.incomes.detail} accent="bg-sky" />
        <MetricCard language={language} label={locale.metrics.assets.label} value={data.tables.assets} detail={locale.metrics.assets.detail} accent="bg-violet" />
      </section>

      <section className="mt-8 grid gap-6 lg:grid-cols-2">
        <Panel title={locale.panels.income.title} eyebrow={locale.panels.income.eyebrow}>
          <IncomeBreakdown items={data.incomeByStream} emptyLabel={locale.panels.income.empty} />
        </Panel>
        <Panel title={locale.panels.assets.title} eyebrow={locale.panels.assets.eyebrow}>
          <BreakdownList items={data.assetsBySection} currency labelCategory="assetSections" emptyLabel={locale.panels.assets.empty} />
        </Panel>
      </section>

      <section className="mt-6 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <Panel title={locale.panels.declarationTypes.title} eyebrow={locale.panels.declarationTypes.eyebrow}>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[22rem] text-left text-sm">
              <thead className="border-b border-slate-200 text-xs uppercase tracking-[0.14em] text-slate-400"><tr><th className="pb-3 font-bold">{locale.panels.declarationTypes.type}</th><th className="pb-3 text-right font-bold">{locale.panels.declarationTypes.rows}</th></tr></thead>
              <tbody className="divide-y divide-slate-100">{data.declarationsByType.map((item) => <tr key={item.label}><td className="py-3 font-semibold text-slate-700">{translateDataLabel(language, "declarationTypes", item.label)}</td><td className="py-3 text-right font-bold text-ink">{formatNumber(item.rows, language)}</td></tr>)}</tbody>
            </table>
            {data.declarationsByType.length === 0 && <p className="py-6 text-sm text-slate-500">{locale.panels.declarationTypes.empty}</p>}
          </div>
        </Panel>
        <Panel title={locale.panels.snapshotMeaning.title} eyebrow={locale.panels.snapshotMeaning.eyebrow}>
          <div className="space-y-4 text-sm leading-6 text-slate-600">
            <p>{locale.panels.snapshotMeaning.counts}</p>
            <p>{locale.panels.snapshotMeaning.amounts}</p>
            <p className="rounded-2xl bg-lime/30 p-4 font-semibold text-ink">{locale.panels.snapshotMeaning.lastGenerated}: {formatDateTime(data.generatedAt, language)}</p>
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
      <Layout><Routes><Route path="/" element={<DashboardPage />} /><Route path="/about" element={<AboutPage />} /><Route path="*" element={<NotFoundPage />} /></Routes></Layout>
    </I18nContext.Provider>
  );
}
