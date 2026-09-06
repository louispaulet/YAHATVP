import { useCallback } from "react";
import { NavLink, useParams } from "react-router-dom";
import { fetchDeclaration } from "../api";
import { declarationDate, declarationName, searchValue } from "../components/declarationFormatters";
import { ChartSkeleton, SliceError } from "../components/Feedback";
import { useI18n } from "../context/I18nContext";
import { useLookupResource } from "../hooks/useLookupResource";
import { DeclarationView } from "../components/DeclarationView";
import { SnapshotContext } from "../components/SnapshotContext";
import { ArrowLeft } from "lucide-react";

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
      <NavLink to="/search" className="inline-flex min-h-10 items-center gap-2 text-sm font-bold text-emerald transition hover:text-ink focus-visible:outline-2 focus-visible:outline-offset-3 focus-visible:outline-emerald"><ArrowLeft size={16} strokeWidth={2} aria-hidden="true" />{locale.declaration.back}</NavLink>
      <section className="mt-7 overflow-hidden rounded-[2rem] bg-ink px-6 py-9 text-white shadow-soft sm:px-10 sm:py-11"><p className="relative z-10 text-xs font-bold uppercase tracking-[0.18em] text-lime">{locale.declaration.eyebrow}</p>{declaration.loading && <ChartSkeleton />}{result && <><div className="relative z-10 mt-4 flex flex-wrap items-center gap-3"><h1 className="max-w-3xl text-4xl font-black leading-[1.04] tracking-[-0.04em] sm:text-5xl">{name}</h1><span className="rounded-full bg-white/10 px-3 py-1.5 text-xs font-bold text-slate-200">{result.isAmended === "true" ? locale.declaration.amended : locale.declaration.original}</span></div><p className="relative z-10 mt-5 max-w-2xl text-base leading-7 text-slate-300">{locale.declaration.description}</p></>}</section>
      {declaration.error && <section className="mt-8"><SliceError onRetry={declaration.reload} /></section>}
      {result && <>
        <section className="dashboard-card relative z-10 mt-4 p-5 sm:p-6"><SnapshotContext snapshotDate={declaration.data?.snapshotDate} generatedAt={declaration.data?.generatedAt} language={language} labels={locale.snapshotContext} sourceScope={locale.snapshotContext.officialScope} className="mb-5" /><div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3"><div><p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.search.fields.identifier}</p><p className="mt-1 break-all font-mono text-xs font-semibold text-slate-700">{searchValue(result.declarationUuid, locale.search.notAvailable)}</p></div><div><p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.declaration.fields.type}</p><p className="mt-1 text-sm font-semibold text-slate-700">{searchValue(result.declarationType, locale.search.notAvailable)}</p></div><div><p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.search.fields.mandate}</p><p className="mt-1 text-sm font-semibold text-slate-700">{searchValue(result.mandate, locale.search.notAvailable)}</p></div><div><p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.search.fields.organ}</p><p className="mt-1 text-sm font-semibold text-slate-700">{searchValue(result.organ || result.organDeclaration, locale.search.notAvailable)}</p></div><div><p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.search.fields.date}</p><p className="mt-1 text-sm font-semibold text-slate-700">{date}</p></div><div><p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.declaration.fields.status}</p><p className="mt-1 text-sm font-semibold text-slate-700">{result.isAmended === "true" ? locale.declaration.amended : locale.declaration.original}</p></div></div></section>
        {declaration.data && <DeclarationView rawXml={declaration.data.rawXml} language={language} locale={locale} amended={result.isAmended === "true"} />}
      </>}
    </div>
  );
}
