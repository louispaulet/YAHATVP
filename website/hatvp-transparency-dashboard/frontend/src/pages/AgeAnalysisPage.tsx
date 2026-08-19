import { useCallback, useEffect, useState, type FormEvent } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useSearchParams } from "react-router-dom";
import { fetchAgeAnalysis } from "../api";
import { formatCurrency, formatNumber } from "../formatters";
import { ChartSkeleton } from "../components/Feedback";
import { Panel } from "../components/Panel";
import { useI18n } from "../context/I18nContext";
import { useLookupResource } from "../hooks/useLookupResource";
import type { AgeAnalysisPerson } from "../types";

const DEFAULT_QUERY = "Sébastien Lecornu";

function nameOf(person: AgeAnalysisPerson, fallback: string): string {
  return [person.firstName, person.lastName].filter(Boolean).join(" ") || fallback;
}

function dateOf(value: string | null, language: "en" | "fr", fallback: string): string {
  if (!value) return fallback;
  return new Intl.DateTimeFormat(language === "fr" ? "fr-FR" : "en-GB", { dateStyle: "medium" }).format(new Date(`${value}T00:00:00`));
}

function qualityLabel(status: string | null, labels: Record<string, string>, fallback: string): string {
  return labels[status || ""] || fallback;
}

export function AgeAnalysisPage() {
  const { language, locale } = useI18n();
  const [params, setParams] = useSearchParams();
  const query = params.get("q")?.trim() || DEFAULT_QUERY;
  const [input, setInput] = useState(query);
  const loadAnalysis = useCallback((signal: AbortSignal) => fetchAgeAnalysis(query, signal), [query]);
  const analysis = useLookupResource(query, loadAnalysis);
  const data = analysis.data;

  useEffect(() => setInput(query), [query]);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextQuery = input.trim();
    setParams(nextQuery ? { q: nextQuery } : {});
  }

  function selectMatch(person: AgeAnalysisPerson) {
    const nextQuery = nameOf(person, "");
    if (nextQuery) setParams({ q: nextQuery });
  }

  return (
    <div className="mx-auto max-w-7xl px-5 py-10 lg:px-8 lg:py-14">
      <section className="hero-grid overflow-hidden rounded-[2rem] bg-ink px-6 py-9 text-white shadow-soft sm:px-10 sm:py-11"><p className="relative z-10 text-xs font-bold uppercase tracking-[0.18em] text-lime">{locale.ageAnalysis.eyebrow}</p><h1 className="relative z-10 mt-4 max-w-3xl text-4xl font-black leading-[1.04] tracking-[-0.04em] sm:text-5xl">{locale.ageAnalysis.title}</h1><p className="relative z-10 mt-5 max-w-3xl text-base leading-7 text-slate-300">{locale.ageAnalysis.description}</p></section>
      <section className="dashboard-card relative z-10 -mt-5 p-5 sm:p-6"><form onSubmit={submit}><label htmlFor="age-analysis-search" className="text-sm font-bold text-ink">{locale.ageAnalysis.inputLabel}</label><div className="mt-3 flex flex-col gap-3 sm:flex-row"><div className="flex min-w-0 flex-1 items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3"><span aria-hidden="true" className="text-xl text-emerald">⌕</span><input id="age-analysis-search" value={input} onChange={(event) => setInput(event.target.value)} placeholder={locale.ageAnalysis.placeholder} maxLength={120} className="min-w-0 flex-1 bg-transparent text-sm font-semibold text-ink outline-none placeholder:font-normal placeholder:text-slate-400" /></div><button type="submit" className="rounded-2xl bg-emerald px-6 py-3 text-sm font-bold text-white transition hover:bg-ink">{locale.ageAnalysis.submit}</button></div><p className="mt-3 text-xs leading-5 text-slate-500">{locale.ageAnalysis.hint}</p></form></section>
      {analysis.loading && <div className="mt-8 space-y-6"><ChartSkeleton /><ChartSkeleton /></div>}
      {analysis.error && <section className="dashboard-card mt-8 border-amber-200 bg-amber-50 p-6"><p className="font-bold text-amber-950">{locale.ageAnalysis.notFound}</p><p className="mt-2 text-sm text-amber-900">{locale.ageAnalysis.loadError}</p><button type="button" onClick={analysis.reload} className="mt-4 rounded-full bg-ink px-4 py-2 text-xs font-bold text-white">{locale.errors.tryAgain}</button></section>}
      {data && <>
        {data.matches.length > 1 && <section className="mt-8"><p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.ageAnalysis.matches}</p><div className="mt-3 flex flex-wrap gap-3">{data.matches.map((match) => <button type="button" key={match.personKey || match.primaryUuid} onClick={() => selectMatch(match)} className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-bold text-ink transition hover:border-emerald hover:text-emerald">{nameOf(match, locale.search.unknownDeclarant)} <span className="ml-1 text-xs font-normal text-slate-500">· {formatNumber(match.declarationCount, language)} {locale.ageAnalysis.declarations}</span></button>)}</div></section>}
        <section className="dashboard-card mt-8 p-6 sm:p-7"><p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.ageAnalysis.profileTitle}</p><div className="mt-3 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between"><div><h2 className="text-3xl font-black tracking-tight text-ink">{nameOf(data.person, locale.search.unknownDeclarant)}</h2><p className="mt-2 text-sm text-slate-500">{formatNumber(data.person.declarationCount, language)} {locale.ageAnalysis.declarations}</p></div><span className="w-fit rounded-full bg-amber-100 px-3 py-1.5 text-xs font-bold text-amber-900">{qualityLabel(data.person.qualityStatus, locale.simpleAnalysis.qualityLabels, locale.ageAnalysis.unknown)}</span></div><dl className="mt-6 grid gap-5 border-t border-slate-100 pt-5 sm:grid-cols-3"><div><dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.ageAnalysis.dateOfBirth}</dt><dd className="mt-1 text-sm font-semibold text-slate-700">{dateOf(data.person.dateOfBirth, language, locale.ageAnalysis.unknown)}</dd></div><div><dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.ageAnalysis.currentAge}</dt><dd className="mt-1 text-sm font-semibold text-slate-700">{data.person.ageYears === null ? locale.ageAnalysis.unknown : formatNumber(data.person.ageYears, language)}</dd></div><div><dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.ageAnalysis.dobQuality}</dt><dd className="mt-1 text-sm font-semibold text-slate-700">{qualityLabel(data.person.qualityStatus, locale.simpleAnalysis.qualityLabels, locale.ageAnalysis.unknown)}</dd></div></dl></section>
        <section className="mt-6 grid gap-6 lg:grid-cols-[1.15fr_0.85fr]"><Panel title={locale.ageAnalysis.incomeTitle} eyebrow={locale.ageAnalysis.incomeEyebrow}><p className="mb-6 text-sm leading-6 text-slate-500">{locale.ageAnalysis.incomeDescription}</p>{data.incomeByYear.length === 0 && <p className="py-8 text-sm text-slate-500">{locale.ageAnalysis.noIncome}</p>}{data.incomeByYear.length > 0 && <><div role="img" aria-label={locale.ageAnalysis.incomeTitle} className="h-64 min-w-0"><ResponsiveContainer width="100%" height="100%"><BarChart data={data.incomeByYear} margin={{ top: 8, right: 8, bottom: 8, left: 8 }}><CartesianGrid vertical={false} stroke="#e2e8f0" strokeDasharray="4 4" /><XAxis dataKey="year" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} /><YAxis tickFormatter={(value) => formatCurrency(Number(value), language)} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} width={72} /><Tooltip formatter={(value) => formatCurrency(Number(value), language)} /><Bar dataKey="combinedAmount" name={locale.ageAnalysis.combined} fill="#1f9d75" radius={[8, 8, 0, 0]} /></BarChart></ResponsiveContainer></div><div className="mt-5 space-y-4">{data.incomeByYear.map((year) => <div key={year.year} className="rounded-2xl bg-canvas p-4"><div className="flex items-baseline justify-between gap-3"><h3 className="font-bold text-ink">{year.year}</h3><span className="whitespace-nowrap text-sm font-black text-emerald">{formatCurrency(year.combinedAmount, language)}</span></div><div className="mt-3 space-y-2">{year.sources.map((source, index) => <div key={`${source.source}-${source.label}-${index}`} className="flex items-start justify-between gap-3 text-xs"><span className="min-w-0"><span className="block font-semibold text-slate-700">{source.label || locale.ageAnalysis.unknown}</span><span className="block text-slate-400">{source.source || locale.ageAnalysis.unknown}</span></span><span className="shrink-0 font-bold text-slate-600">{formatCurrency(source.amount, language)}</span></div>)}</div></div>)}</div></>}</Panel><Panel title={locale.ageAnalysis.occupationTitle} eyebrow={locale.ageAnalysis.occupationEyebrow}><p className="mb-6 text-sm leading-6 text-slate-500">{locale.ageAnalysis.occupationDescription}</p>{data.occupationsByYear.length === 0 && <p className="py-8 text-sm text-slate-500">{locale.ageAnalysis.noOccupations}</p>}{data.occupationsByYear.length > 0 && <div className="space-y-4">{data.occupationsByYear.map((year) => <article key={year.year} className="rounded-2xl border border-slate-100 p-4"><div className="flex items-baseline justify-between gap-3"><h3 className="font-bold text-ink">{year.year}</h3><span className="text-xs font-bold text-slate-400">{formatNumber(year.count, language)} {locale.ageAnalysis.occupationCount}</span></div><ul className="mt-3 space-y-2">{year.occupations.map((occupation, index) => <li key={`${occupation.label}-${occupation.source}-${index}`} className="flex items-start justify-between gap-3 text-sm"><span className="font-semibold text-slate-700">{occupation.label || locale.ageAnalysis.unknown}<span className="ml-2 text-xs font-normal text-slate-400">{occupation.source || locale.ageAnalysis.unknown}</span></span><span className="shrink-0 text-xs font-bold text-slate-400">×{occupation.rows}</span></li>)}</ul></article>)}</div>}</Panel></section>
        <Panel title={locale.ageAnalysis.assetTitle} eyebrow={locale.ageAnalysis.assetEyebrow}><p className="mb-6 max-w-3xl text-sm leading-6 text-slate-500">{locale.ageAnalysis.assetDescription}</p>{data.assetTimeline.length === 0 && <p className="py-8 text-sm text-slate-500">{locale.ageAnalysis.noAssets}</p>}{data.assetTimeline.length > 0 && <ol className="relative ml-3 border-l-2 border-emerald/30 pl-7">{data.assetTimeline.map((event) => <li key={event.year} className="relative pb-8 last:pb-0"><span aria-hidden="true" className="absolute -left-[2.15rem] top-1 size-3 rounded-full border-4 border-canvas bg-emerald" /><div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"><div><p className="text-xs font-bold uppercase tracking-[0.15em] text-emerald">{event.year} · {locale.ageAnalysis.relativeAge} {event.relativeAge}</p><div className="mt-3 grid gap-3 sm:grid-cols-2">{event.assets.map((asset, index) => <div key={`${asset.source}-${asset.name}-${index}`} className="rounded-2xl bg-canvas p-4"><p className="font-bold text-ink">{asset.name || locale.ageAnalysis.unknown}</p><p className="mt-1 text-xs text-slate-500">{asset.source || locale.ageAnalysis.unknown}</p>{asset.value !== null && <p className="mt-3 text-sm font-black text-emerald">{formatCurrency(asset.value, language)} <span className="font-normal text-slate-400">· {locale.ageAnalysis.assetValue}</span></p>}</div>)}</div></div></div></li>)}</ol>}</Panel>
      </>}
    </div>
  );
}
