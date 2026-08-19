import { useCallback, useEffect, useState, type FormEvent } from "react";
import { useSearchParams } from "react-router-dom";
import { fetchAgeAnalysis } from "../api";
import { AgeAssetInventory } from "../components/AgeAssetInventory";
import { AgeDeclarationContext } from "../components/AgeDeclarationContext";
import { AgeIncomePanel } from "../components/AgeIncomePanel";
import { ChartSkeleton } from "../components/Feedback";
import { useI18n } from "../context/I18nContext";
import { formatNumber } from "../formatters";
import { useLookupResource } from "../hooks/useLookupResource";
import type { AgeAnalysisPerson } from "../types";

const DEFAULT_QUERY = "Sébastien Lecornu";

function nameOf(person: AgeAnalysisPerson, fallback: string): string {
  return [person.firstName, person.lastName].filter(Boolean).join(" ") || fallback;
}

function dateOf(value: string | null, language: "en" | "fr", fallback: string): string {
  if (!value) return fallback;
  return new Intl.DateTimeFormat(language === "fr" ? "fr-FR" : "en-GB", {
    dateStyle: "medium",
  }).format(new Date(`${value}T00:00:00`));
}

export function AgeAnalysisPage() {
  const { language, locale } = useI18n();
  const labels = locale.ageAnalysis;
  const [params, setParams] = useSearchParams();
  const query = params.get("q")?.trim() || DEFAULT_QUERY;
  const [input, setInput] = useState(query);
  const load = useCallback((signal: AbortSignal) => fetchAgeAnalysis(query, signal), [query]);
  const analysis = useLookupResource(query, load);

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

  const data = analysis.data;
  const quality = data?.person.qualityStatus
    ? locale.simpleAnalysis.qualityLabels[data.person.qualityStatus as keyof typeof locale.simpleAnalysis.qualityLabels] || labels.unknown
    : labels.unknown;

  return (
    <div className="mx-auto max-w-7xl px-5 py-10 lg:px-8 lg:py-14">
      <section className="hero-grid overflow-hidden rounded-[2rem] bg-ink px-6 py-9 text-white shadow-soft sm:px-10 sm:py-11"><p className="relative z-10 text-xs font-bold uppercase tracking-[0.18em] text-lime">{labels.eyebrow}</p><h1 className="relative z-10 mt-4 max-w-4xl text-4xl font-black leading-[1.04] tracking-[-0.04em] sm:text-5xl">{labels.title}</h1><p className="relative z-10 mt-5 max-w-3xl text-base leading-7 text-slate-300">{labels.description}</p></section>
      <section className="dashboard-card relative z-10 -mt-5 p-5 sm:p-6"><form onSubmit={submit}><label htmlFor="age-analysis-search" className="text-sm font-bold text-ink">{labels.inputLabel}</label><div className="mt-3 flex flex-col gap-3 sm:flex-row"><div className="flex min-w-0 flex-1 items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3 focus-within:border-emerald focus-within:ring-2 focus-within:ring-emerald/30"><span aria-hidden="true" className="text-xl text-emerald">⌕</span><input id="age-analysis-search" value={input} onChange={(event) => setInput(event.target.value)} placeholder={labels.placeholder} maxLength={120} className="min-w-0 flex-1 bg-transparent text-sm font-semibold text-ink outline-none placeholder:font-normal placeholder:text-slate-400" /></div><button type="submit" className="rounded-2xl bg-emerald px-6 py-3 text-sm font-bold text-white transition hover:bg-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald">{labels.submit}</button></div><p className="mt-3 text-xs leading-5 text-slate-500">{labels.hint}</p></form></section>
      {analysis.loading && <div className="mt-8 space-y-6"><ChartSkeleton /><ChartSkeleton /></div>}
      {analysis.error && <section className="dashboard-card mt-8 border-amber-200 bg-amber-50 p-6"><p className="font-bold text-amber-950">{labels.notFound}</p><p className="mt-2 text-sm text-amber-900">{labels.loadError}</p><button type="button" onClick={analysis.reload} className="mt-4 rounded-full bg-ink px-4 py-2 text-xs font-bold text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ink">{locale.errors.tryAgain}</button></section>}
      {data && <>
        {data.matches.length > 1 && <section className="mt-8"><p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{labels.matches}</p><div className="mt-3 flex flex-wrap gap-3">{data.matches.map((match) => <button type="button" key={match.personKey || match.primaryUuid} onClick={() => selectMatch(match)} className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-bold text-ink transition hover:border-emerald hover:text-emerald focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald">{nameOf(match, locale.search.unknownDeclarant)} <span className="ml-1 text-xs font-normal text-slate-500">· {formatNumber(match.declarationCount, language)} {labels.declarations}</span></button>)}</div></section>}
        <section className="dashboard-card mt-8 p-6 sm:p-7"><p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{labels.profileTitle}</p><div className="mt-3 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between"><div><h2 className="text-3xl font-black tracking-tight text-ink">{nameOf(data.person, locale.search.unknownDeclarant)}</h2><p className="mt-2 text-sm text-slate-500">{formatNumber(data.person.declarationCount, language)} {labels.declarations}</p></div><span className="w-fit rounded-full bg-amber-100 px-3 py-1.5 text-xs font-bold text-amber-900">{quality}</span></div><dl className="mt-6 grid gap-5 border-t border-slate-100 pt-5 sm:grid-cols-3"><div><dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{labels.dateOfBirth}</dt><dd className="mt-1 text-sm font-semibold text-slate-700">{dateOf(data.person.dateOfBirth, language, labels.unknown)}</dd></div><div><dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{labels.currentAge}</dt><dd className="mt-1 text-sm font-semibold text-slate-700">{data.person.ageYears === null ? labels.unknown : formatNumber(data.person.ageYears, language)}</dd></div><div><dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{labels.dobQuality}</dt><dd className="mt-1 text-sm font-semibold text-slate-700">{quality}</dd></div></dl></section>
        <AgeDeclarationContext context={data.declarationContext} language={language} labels={labels} />
        <AgeIncomePanel income={data.incomeByYear} language={language} labels={labels} />
        <AgeAssetInventory assets={data.assetInventory} language={language} labels={labels} />
      </>}
    </div>
  );
}
