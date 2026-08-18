import { useCallback } from "react";
import { NavLink, useParams } from "react-router-dom";
import { fetchDeclaration } from "../api";
import { declarationDate, declarationName, searchValue } from "../components/declarationFormatters";
import { ChartSkeleton, SliceError } from "../components/Feedback";
import { useI18n } from "../context/I18nContext";
import { useLookupResource } from "../hooks/useLookupResource";
import { formatNumber } from "../formatters";

export function DeclarationPage() {
  const { language, locale } = useI18n();
  const { uuid = "" } = useParams();
  const loadDeclaration = useCallback((signal: AbortSignal) => fetchDeclaration(uuid, signal), [uuid]);
  const declaration = useLookupResource(uuid, loadDeclaration);
  const result = declaration.data?.declaration;
  const name = result ? declarationName(result, locale.search.unknownDeclarant) : locale.search.unknownDeclarant;
  const date = declarationDate(result?.dateDeposited ?? null, language, locale.search.notAvailable);

  return (
    <div className="mx-auto max-w-6xl px-5 py-12 lg:px-8 lg:py-16">
      <NavLink to="/search" className="inline-flex items-center gap-2 text-sm font-bold text-emerald transition hover:text-ink"><span aria-hidden="true">←</span>{locale.declaration.back}</NavLink>
      <section className="mt-7 overflow-hidden rounded-[2rem] bg-ink px-6 py-9 text-white shadow-soft sm:px-10 sm:py-11"><p className="relative z-10 text-xs font-bold uppercase tracking-[0.18em] text-lime">{locale.declaration.eyebrow}</p>{declaration.loading && <ChartSkeleton />}{result && <><h1 className="relative z-10 mt-4 max-w-3xl text-4xl font-black leading-[1.04] tracking-[-0.04em] sm:text-5xl">{name}</h1><p className="relative z-10 mt-5 max-w-2xl text-base leading-7 text-slate-300">{locale.declaration.description}</p></>}</section>
      {declaration.error && <section className="mt-8"><SliceError onRetry={declaration.reload} /></section>}
      {result && <>
        <section className="dashboard-card relative z-10 -mt-5 p-5 sm:p-6"><div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4"><div><p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.search.fields.identifier}</p><p className="mt-1 break-all font-mono text-xs font-semibold text-slate-700">{searchValue(result.declarationUuid, locale.search.notAvailable)}</p></div><div><p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.declaration.fields.type}</p><p className="mt-1 text-sm font-semibold text-slate-700">{searchValue(result.declarationType, locale.search.notAvailable)}</p></div><div><p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.search.fields.mandate}</p><p className="mt-1 text-sm font-semibold text-slate-700">{searchValue(result.mandate, locale.search.notAvailable)}</p></div><div><p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.search.fields.date}</p><p className="mt-1 text-sm font-semibold text-slate-700">{date}</p></div></div></section>
        {declaration.data && <section className="dashboard-card mt-8 overflow-hidden"><div className="flex flex-col gap-3 border-b border-slate-200 px-5 py-5 sm:flex-row sm:items-end sm:justify-between sm:px-6"><div><p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.declaration.sourceEyebrow}</p><h2 className="mt-2 text-2xl font-black tracking-tight text-ink">{locale.declaration.sourceTitle}</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">{locale.declaration.sourceDescription}</p></div><span className="shrink-0 rounded-full bg-slate-100 px-3 py-1.5 text-xs font-bold text-slate-500">{formatNumber(declaration.data.rawXml.length, language)} {locale.declaration.characters}</span></div><pre aria-label={locale.declaration.rawXmlLabel} className="max-h-[70vh] overflow-auto bg-[#101815] p-5 text-xs leading-6 text-slate-200 sm:p-7"><code>{declaration.data.rawXml}</code></pre></section>}
      </>}
    </div>
  );
}
