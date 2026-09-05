import { NavLink } from "react-router-dom";
import { ArrowUpRight } from "lucide-react";
import { translateDataLabel } from "../config/i18n";
import { useI18n } from "../context/I18nContext";
import { declarationDate, declarationName, searchValue } from "./declarationFormatters";
import type { DeclarationSearchResult } from "../types";

export function SearchResultCard({ result }: { result: DeclarationSearchResult }) {
  const { language, locale } = useI18n();
  const name = declarationName(result, locale.search.unknownDeclarant);
  const date = declarationDate(result.dateDeposited, language, locale.search.notAvailable);
  const type = result.declarationType
    ? translateDataLabel(language, "declarationTypes", result.declarationType)
    : locale.search.notAvailable;

  return (
    <article className="dashboard-card p-5 transition hover:border-emerald/40 hover:shadow-soft sm:p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div><p className="text-xs font-bold uppercase tracking-[0.16em] text-emerald">{locale.search.resultEyebrow}</p><h2 className="mt-2 text-xl font-black tracking-tight text-ink">{name}</h2></div>
        <span className="max-w-full rounded-full bg-lime/60 px-3 py-1.5 text-xs font-bold leading-5 text-ink sm:text-right">{type}</span>
      </div>
      <dl className="mt-6 grid gap-x-5 gap-y-4 border-t border-slate-100 pt-5 sm:grid-cols-2 lg:grid-cols-4">
        <div><dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.search.fields.mandate}</dt><dd className="mt-1 text-sm font-semibold text-slate-700">{searchValue(result.mandate, locale.search.notAvailable)}</dd></div>
        <div><dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.search.fields.organ}</dt><dd className="mt-1 text-sm font-semibold text-slate-700">{searchValue(result.organ || result.organDeclaration, locale.search.notAvailable)}</dd></div>
        <div><dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.search.fields.date}</dt><dd className="mt-1 text-sm font-semibold text-slate-700">{date}</dd></div>
        <div><dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.search.fields.identifier}</dt><dd className="mt-1 break-all font-mono text-xs font-semibold text-slate-700">{searchValue(result.declarationUuid, locale.search.notAvailable)}</dd></div>
      </dl>
      {result.declarationUuid && <NavLink to={`/declarations/${encodeURIComponent(result.declarationUuid)}`} className="mt-5 flex min-h-11 items-center justify-between gap-3 border-t border-slate-100 pt-5 text-sm font-bold text-emerald transition hover:text-ink focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-emerald"><span>{locale.search.viewDeclaration}</span><ArrowUpRight size={16} strokeWidth={2} aria-hidden="true" /></NavLink>}
    </article>
  );
}
