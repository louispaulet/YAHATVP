import { NavLink } from "react-router-dom";
import { ArrowUpRight } from "lucide-react";
import { translateDataLabel, type Language, type Locale } from "../config/i18n";
import { formatNumber } from "../formatters";
import type { AgeAnalysisDeclaration, AgeAnalysisResponse } from "../types";

type Labels = Locale["ageAnalysis"];

function dateLabel(value: string | null, language: Language, fallback: string): string {
  if (!value) return fallback;
  return new Intl.DateTimeFormat(language === "fr" ? "fr-FR" : "en-GB", {
    dateStyle: "medium",
  }).format(new Date(`${value}T00:00:00`));
}

function DeclarationCard({ item, title, language, labels }: {
  item: AgeAnalysisDeclaration | null; title: string; language: Language; labels: Labels;
}) {
  if (!item) return <div className="rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-500">{labels.notAvailable}</div>;
  const type = item.typeLabel
    ? translateDataLabel(language, "declarationTypes", item.typeLabel)
    : labels.unknown;
  return (
    <article className="rounded-2xl border border-emerald/20 bg-white p-4">
      <p className="text-xs font-bold uppercase tracking-[0.12em] text-emerald">{title}</p>
      <h3 className="mt-2 font-bold text-ink">{type}</h3>
      <p className="mt-1 text-sm text-slate-500">{labels.filed} {dateLabel(item.filedAt, language, labels.unknown)}</p>
      {item.declarationUuid && <NavLink to={`/declarations/${encodeURIComponent(item.declarationUuid)}`} className="mt-4 inline-flex min-h-10 items-center gap-1 rounded-full border border-emerald/30 px-3 py-2 text-xs font-bold text-emerald transition hover:bg-emerald hover:text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald">{labels.openDeclaration}<ArrowUpRight size={14} strokeWidth={2} aria-hidden="true" /></NavLink>}
    </article>
  );
}

export function AgeDeclarationContext({ context, language, labels }: {
  context: AgeAnalysisResponse["declarationContext"]; language: Language; labels: Labels;
}) {
  return (
    <section className="dashboard-card mt-6 border-emerald/20 bg-emerald/[0.04] p-6 sm:p-7">
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{labels.contextEyebrow}</p>
      <h2 className="mt-2 text-xl font-black tracking-tight text-ink">{labels.contextTitle}</h2>
      <p className="mt-3 max-w-4xl text-sm leading-6 text-slate-600">{labels.contextDescription}</p>
      <div className="mt-5 flex flex-wrap gap-2 text-xs font-bold text-slate-700">
        <span className="rounded-full bg-white px-3 py-2">{formatNumber(context.interestCount, language)} {labels.interestDeclarations}</span>
        <span className="rounded-full bg-white px-3 py-2">{formatNumber(context.assetCount, language)} {labels.assetDeclarations}</span>
      </div>
      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <DeclarationCard item={context.latestInterest} title={labels.primaryInterest} language={language} labels={labels} />
        <DeclarationCard item={context.latestAssets} title={labels.primaryAssets} language={language} labels={labels} />
      </div>
      <details className="mt-5 rounded-2xl border border-slate-200 bg-white p-4">
        <summary className="cursor-pointer rounded-lg text-sm font-bold text-ink focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-emerald">{labels.showHistory} ({formatNumber(context.history.length, language)})</summary>
        <p className="mt-3 text-sm leading-6 text-slate-500">{labels.historyDescription}</p>
        <ul className="mt-4 divide-y divide-slate-100">
          {context.history.map((item) => <li key={item.declarationUuid || `${item.family}-${item.filedAt}`} className="flex flex-col gap-2 py-3 sm:flex-row sm:items-center sm:justify-between"><span className="min-w-0"><span className="font-semibold text-slate-800">{item.typeLabel ? translateDataLabel(language, "declarationTypes", item.typeLabel) : labels.unknown}</span><span className="block text-xs text-slate-500">{dateLabel(item.filedAt, language, labels.unknown)} · {item.isSelected ? labels.selected : labels.priorVersion}</span></span>{item.declarationUuid && <NavLink to={`/declarations/${encodeURIComponent(item.declarationUuid)}`} className="inline-flex min-h-10 w-fit items-center gap-1 text-xs font-bold text-emerald hover:text-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald">{labels.openDeclaration}<ArrowUpRight size={14} strokeWidth={2} aria-hidden="true" /></NavLink>}</li>)}
        </ul>
      </details>
    </section>
  );
}
