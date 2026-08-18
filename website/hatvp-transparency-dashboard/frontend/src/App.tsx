import { useEffect, useMemo, useState } from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import { fetchDashboard } from "./api";
import type { BreakdownItem, DashboardResponse } from "./types";

const numberFormatter = new Intl.NumberFormat("fr-FR");
const currencyFormatter = new Intl.NumberFormat("fr-FR", {
  style: "currency",
  currency: "EUR",
  maximumFractionDigits: 0,
});

function formatNumber(value: number): string {
  return numberFormatter.format(value);
}

function formatCurrency(value: number): string {
  return currencyFormatter.format(value);
}

function displayLabel(value: string): string {
  return value
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function navClass({ isActive }: { isActive: boolean }): string {
  return isActive
    ? "rounded-full bg-ink px-4 py-2 text-sm font-semibold text-white"
    : "rounded-full px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-white hover:text-ink";
}

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-canvas text-ink">
      <header className="border-b border-slate-200/80 bg-canvas/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5 lg:px-8">
          <NavLink to="/" className="flex items-center gap-3">
            <span className="grid size-10 place-items-center rounded-2xl bg-ink text-lg font-black text-lime">
              H
            </span>
            <span>
              <span className="block text-xs font-bold uppercase tracking-[0.22em] text-slate-500">HATVP</span>
              <span className="block text-sm font-semibold">Transparency dashboard</span>
            </span>
          </NavLink>
          <nav className="flex items-center gap-1 rounded-full border border-slate-200 bg-slate-100/70 p-1">
            <NavLink to="/" end className={navClass}>Overview</NavLink>
            <NavLink to="/about" className={navClass}>About the data</NavLink>
          </nav>
        </div>
      </header>
      <main>{children}</main>
      <footer className="mx-auto flex max-w-7xl flex-col gap-2 px-5 py-10 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between lg:px-8">
        <span>Built from public HATVP declarations.</span>
        <a className="font-semibold text-slate-700 underline decoration-lime underline-offset-4" href="https://www.hatvp.fr/" target="_blank" rel="noreferrer">
          hatvp.fr
        </a>
      </footer>
    </div>
  );
}

function MetricCard({ label, value, detail, accent }: { label: string; value: number; detail: string; accent: string }) {
  return (
    <article className="dashboard-card relative overflow-hidden p-6">
      <span className={`absolute inset-x-0 top-0 h-1 ${accent}`} />
      <p className="text-sm font-semibold text-slate-500">{label}</p>
      <p className="mt-4 text-4xl font-black tracking-tight text-ink">{formatNumber(value)}</p>
      <p className="mt-2 text-xs font-medium uppercase tracking-[0.14em] text-slate-400">{detail}</p>
    </article>
  );
}

function BreakdownList({ items, currency, emptyLabel }: { items: BreakdownItem[]; currency: boolean; emptyLabel: string }) {
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
              <span className="truncate font-semibold text-slate-700">{displayLabel(item.label)}</span>
              <span className="shrink-0 font-bold text-ink">{currency ? formatCurrency(amount) : formatNumber(item.rows)}</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-slate-100">
              <div className="h-full rounded-full bg-emerald" style={{ width: `${width}%` }} />
            </div>
            <p className="mt-1 text-xs text-slate-400">{formatNumber(item.rows)} rows</p>
          </div>
        );
      })}
    </div>
  );
}

const pieColors = ["var(--color-emerald)", "var(--color-sky)"];

function IncomePieChart({ items, emptyLabel }: { items: BreakdownItem[]; emptyLabel: string }) {
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
      return `${displayLabel(item.label)} ${formatCurrency(values[index])}, ${percentage.toFixed(1)}%`;
    })
    .join("; ");

  return (
    <div className="flex flex-col items-center gap-7 sm:flex-row sm:items-center">
      <div
        aria-label={`Income totals by stream: ${chartLabel}`}
        className="size-44 shrink-0 rounded-full shadow-inner ring-8 ring-white sm:size-52"
        role="img"
        style={{ background: `conic-gradient(${segments.join(", ")})` }}
      />
      <div className="w-full min-w-0 space-y-4" aria-label="Income stream legend">
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
                  <p className="truncate text-sm font-semibold text-slate-700">{displayLabel(item.label)}</p>
                  <p className="mt-1 text-xs text-slate-400">{formatNumber(item.rows)} rows · {percentage.toFixed(1)}%</p>
                </div>
              </div>
              <span className="shrink-0 text-right text-sm font-bold text-ink">{formatCurrency(amount)}</span>
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
    <BreakdownList items={items} currency emptyLabel={emptyLabel} />
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

function DashboardPage() {
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    setError(null);
    const controller = new AbortController();
    fetchDashboard(controller.signal)
      .then(setData)
      .catch((reason: unknown) => {
        if (reason instanceof DOMException && reason.name === "AbortError") return;
        setError(reason instanceof Error ? reason.message : "Dashboard data could not be loaded.");
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
        <h1 className="mt-6 text-3xl font-black">The dashboard is taking a pause.</h1>
        <p className="mt-3 text-slate-600">{error ?? "No data is available yet."}</p>
        <button onClick={load} className="mt-7 rounded-full bg-ink px-5 py-3 text-sm font-bold text-white transition hover:bg-slate-700">Try again</button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-5 py-10 lg:px-8 lg:py-14">
      <section className="hero-grid overflow-hidden rounded-[2rem] bg-ink px-6 py-9 text-white shadow-soft sm:px-10 sm:py-12">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-xs font-bold uppercase tracking-[0.16em] text-lime">
            <span className="size-2 rounded-full bg-lime" /> Public data, made clearer
          </div>
          <h1 className="mt-7 max-w-xl text-4xl font-black leading-[1.02] tracking-[-0.04em] sm:text-6xl">A clearer view of public declarations.</h1>
          <p className="mt-5 max-w-lg text-base leading-7 text-slate-300">Explore the latest curated HATVP snapshot through a small set of transparent, source-linked aggregates.</p>
        </div>
        <div className="relative z-10 mt-10 flex flex-wrap gap-3 text-sm sm:mt-0 sm:justify-end">
          <span className="rounded-full bg-white/10 px-4 py-2 font-semibold text-slate-200">Snapshot {data.snapshotDate ?? "not available"}</span>
          <span className="rounded-full bg-lime px-4 py-2 font-bold text-ink">{formatNumber(totalRows)} total rows</span>
        </div>
      </section>

      <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Declarations" value={data.tables.declarations} detail="latest snapshot" accent="bg-emerald" />
        <MetricCard label="People" value={data.tables.people} detail="declarant records" accent="bg-lime" />
        <MetricCard label="Income rows" value={data.tables.incomes} detail="declared values" accent="bg-sky" />
        <MetricCard label="Asset rows" value={data.tables.assets} detail="observed assets" accent="bg-violet" />
      </section>

      <section className="mt-8 grid gap-6 lg:grid-cols-2">
        <Panel title="Income, by stream" eyebrow="Declared amounts">
          <IncomeBreakdown items={data.incomeByStream} emptyLabel="No income rows were found in this snapshot." />
        </Panel>
        <Panel title="Assets, by section" eyebrow="Observed values">
          <BreakdownList items={data.assetsBySection} currency emptyLabel="No asset rows were found in this snapshot." />
        </Panel>
      </section>

      <section className="mt-6 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <Panel title="Declaration types" eyebrow="Composition">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[22rem] text-left text-sm">
              <thead className="border-b border-slate-200 text-xs uppercase tracking-[0.14em] text-slate-400"><tr><th className="pb-3 font-bold">Type</th><th className="pb-3 text-right font-bold">Rows</th></tr></thead>
              <tbody className="divide-y divide-slate-100">{data.declarationsByType.map((item) => <tr key={item.label}><td className="py-3 font-semibold text-slate-700">{displayLabel(item.label)}</td><td className="py-3 text-right font-bold text-ink">{formatNumber(item.rows)}</td></tr>)}</tbody>
            </table>
            {data.declarationsByType.length === 0 && <p className="py-6 text-sm text-slate-500">No declaration types were found.</p>}
          </div>
        </Panel>
        <Panel title="What this snapshot means" eyebrow="Reading the data">
          <div className="space-y-4 text-sm leading-6 text-slate-600">
            <p>Counts are limited to the latest successful snapshot shared across the curated tables.</p>
            <p>Amounts preserve the normalized numeric values produced by the ingestion pipeline. They are presented as indicators, not as a substitute for the source declarations.</p>
            <p className="rounded-2xl bg-lime/30 p-4 font-semibold text-ink">Last generated: {new Date(data.generatedAt).toLocaleString("fr-FR")}</p>
          </div>
        </Panel>
      </section>
    </div>
  );
}

function AboutPage() {
  return (
    <div className="mx-auto max-w-3xl px-5 py-16 lg:px-8 lg:py-24">
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">About the data</p>
      <h1 className="mt-4 text-4xl font-black tracking-tight sm:text-5xl">A small window into a public dataset.</h1>
      <div className="mt-8 space-y-6 text-base leading-8 text-slate-600">
        <p>This dashboard is built from the HATVP open-data pipeline. The pipeline preserves raw source files, normalizes records, checks quality, and publishes four curated BigQuery tables.</p>
        <p>The overview intentionally exposes aggregates only. Personal contact details and raw declaration rows are not part of this public API.</p>
        <p>For the authoritative source and the full declaration context, visit <a className="font-bold text-ink underline decoration-lime underline-offset-4" href="https://www.hatvp.fr/open-data/" target="_blank" rel="noreferrer">HATVP open data</a>.</p>
      </div>
      <div className="mt-10 grid gap-4 sm:grid-cols-2">
        <div className="dashboard-card p-5"><p className="text-xs font-bold uppercase tracking-[0.14em] text-slate-400">Curated tables</p><p className="mt-2 text-2xl font-black">4</p><p className="mt-1 text-sm text-slate-500">declarations, people, incomes, assets</p></div>
        <div className="dashboard-card p-5"><p className="text-xs font-bold uppercase tracking-[0.14em] text-slate-400">Update rhythm</p><p className="mt-2 text-2xl font-black">Weekly</p><p className="mt-1 text-sm text-slate-500">following the ingestion pipeline</p></div>
      </div>
    </div>
  );
}

function NotFoundPage() {
  return <div className="mx-auto max-w-2xl px-5 py-24 text-center lg:px-8"><h1 className="text-4xl font-black">Page not found.</h1><NavLink className="mt-6 inline-block rounded-full bg-ink px-5 py-3 text-sm font-bold text-white" to="/">Back to overview</NavLink></div>;
}

export function App() {
  return <Layout><Routes><Route path="/" element={<DashboardPage />} /><Route path="/about" element={<AboutPage />} /><Route path="*" element={<NotFoundPage />} /></Routes></Layout>;
}
