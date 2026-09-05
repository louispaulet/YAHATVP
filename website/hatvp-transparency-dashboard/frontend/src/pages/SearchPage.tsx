import { useCallback, useEffect, useState, type FormEvent } from "react";
import { useSearchParams } from "react-router-dom";
import { fetchSearch } from "../api";
import { SearchResultCard } from "../components/SearchResultCard";
import { ChartSkeleton, SliceError } from "../components/Feedback";
import { useI18n } from "../context/I18nContext";
import { useLookupResource } from "../hooks/useLookupResource";
import { formatNumber } from "../formatters";
import { Search } from "lucide-react";

export function SearchPage() {
  const { language, locale } = useI18n();
  const [params, setParams] = useSearchParams();
  const query = params.get("q")?.trim() ?? "";
  const [input, setInput] = useState(query);
  const loadSearch = useCallback((signal: AbortSignal) => fetchSearch(query, signal), [query]);
  const search = useLookupResource(query, loadSearch);

  useEffect(() => setInput(query), [query]);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextQuery = input.trim();
    setParams(nextQuery ? { q: nextQuery } : {});
  }

  function searchExample(example: string) {
    setInput(example);
    setParams({ q: example });
  }

  return (
    <div className="mx-auto max-w-5xl px-5 py-12 lg:px-8 lg:py-16">
      <section className="hero-grid overflow-hidden rounded-[2rem] bg-ink px-6 py-9 text-white shadow-soft sm:px-10 sm:py-11"><p className="relative z-10 text-xs font-bold uppercase tracking-[0.18em] text-lime">{locale.search.eyebrow}</p><h1 className="relative z-10 mt-4 max-w-3xl text-4xl font-black leading-[1.04] tracking-[-0.04em] sm:text-5xl">{locale.search.title}</h1><p className="relative z-10 mt-5 max-w-2xl text-base leading-7 text-slate-300">{locale.search.description}</p></section>
      <section className="dashboard-card relative z-10 -mt-5 overflow-hidden p-5 sm:p-6"><form onSubmit={submit}><div className="flex flex-col gap-2 sm:flex-row sm:items-baseline sm:justify-between"><label htmlFor="declaration-search" className="text-sm font-bold text-ink">{locale.search.inputLabel}</label><p className="text-xs font-semibold text-emerald">{locale.search.searchTip}</p></div><div className="mt-3 flex flex-col gap-3 sm:flex-row"><div className="flex min-w-0 flex-1 items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm transition focus-within:border-emerald focus-within:ring-4 focus-within:ring-emerald/10"><Search aria-hidden="true" className="size-5 shrink-0 text-emerald" /><input id="declaration-search" value={input} onChange={(event) => setInput(event.target.value)} placeholder={locale.search.placeholder} maxLength={120} autoComplete="off" className="min-w-0 flex-1 bg-transparent text-sm font-semibold text-ink outline-none placeholder:font-normal placeholder:text-slate-400" />{input && <button type="button" onClick={() => { setInput(""); setParams({}); }} className="min-h-10 rounded-lg px-2 py-1 text-xs font-bold text-slate-400 transition hover:bg-slate-100 hover:text-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald" aria-label={locale.search.clear}>{locale.search.clear}</button>}</div><button type="submit" className="min-h-11 rounded-2xl bg-emerald px-6 py-3 text-sm font-bold text-white transition hover:bg-ink focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-emerald">{locale.search.submit}</button></div><p className="mt-3 text-xs leading-5 text-slate-500">{locale.search.hint}</p><details className="mt-4 rounded-xl bg-surface-subtle px-4 py-3"><summary className="cursor-pointer text-sm font-bold text-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald">{locale.search.fieldsDisclosure}</summary><p className="mt-2 text-sm leading-6 text-slate-600">{locale.search.fieldsDescription}</p></details></form></section>
      {!query && <section className="dashboard-card mt-8 p-6 sm:p-8"><p className="text-sm font-bold uppercase tracking-[0.14em] text-slate-400">{locale.search.emptyTitle}</p><p className="mt-3 max-w-2xl text-lg font-semibold leading-7 text-ink">{locale.search.emptyDescription}</p><div className="mt-5 flex flex-wrap gap-2" aria-label={locale.search.examplesLabel}>{locale.search.examples.map((example) => <button key={example} type="button" onClick={() => searchExample(example)} className="rounded-full border border-emerald/20 bg-emerald/5 px-3 py-2 text-sm font-bold text-emerald transition hover:border-emerald hover:bg-emerald hover:text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald">{example}</button>)}</div></section>}
      {query && search.loading && <section className="mt-8 space-y-4" aria-busy="true" aria-live="polite"><p className="sr-only">{locale.search.loadingQuery.replace("{query}", query)}</p><ChartSkeleton /><ChartSkeleton /></section>}
      {query && search.error && <section className="mt-8"><SliceError onRetry={search.reload} /></section>}
      {query && search.data && search.data.results.length === 0 && <section className="dashboard-card mt-8 border-dashed p-6 sm:p-8"><p className="text-sm font-bold uppercase tracking-[0.14em] text-slate-400">{locale.search.noResultsEyebrow}</p><p className="mt-3 text-lg font-semibold text-ink">{locale.search.noResults.replace("{query}", query)}</p></section>}
      {query && search.data && search.data.results.length > 0 && <section className="mt-8" aria-live="polite"><div className="mb-4 flex flex-col gap-2 rounded-2xl border border-emerald/15 bg-emerald/5 px-5 py-4 sm:flex-row sm:items-center sm:justify-between"><div><p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.search.resultsEyebrow}</p><h2 className="mt-1 text-2xl font-black tracking-tight text-ink">{locale.search.resultsFound.replace("{count}", formatNumber(search.data.resultCount, language))}</h2></div><p className="text-sm font-semibold text-slate-600">{locale.search.queryLabel.replace("{query}", query)}</p><p className="text-xs text-slate-500">{locale.search.snapshot.replace("{date}", search.data.snapshotDate || locale.search.notAvailable)}</p></div><div className="space-y-4">{search.data.results.map((result, index) => <SearchResultCard key={`${result.declarationUuid}-${index}`} result={result} />)}</div></section>}
    </div>
  );
}
