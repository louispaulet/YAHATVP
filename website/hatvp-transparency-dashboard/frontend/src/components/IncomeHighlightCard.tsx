import { ArrowRight, TriangleAlert } from "lucide-react";
import { Link } from "react-router-dom";
import { useI18n } from "../context/I18nContext";
import { formatCurrency } from "../formatters";
import type { IncomeChangeHighlight } from "../types";

export function IncomeHighlightCard({ item, rank }: { item: IncomeChangeHighlight; rank: number }) {
  const { language, locale } = useI18n();
  const name = `${item.firstName ?? ""} ${item.lastName ?? ""}`.trim() || locale.explore.unknownName;
  const change = `${item.absoluteChange > 0 ? "+" : ""}${formatCurrency(item.absoluteChange, language)}`;
  return (
    <article className="explore-card explore-card--income flex min-h-[20rem] flex-col p-5 sm:p-[1.375rem]">
      <div className="flex items-start justify-between gap-3">
        <span className="explore-card-rank">#{String(rank).padStart(2, "0")}</span>
        {item.reviewRequired && <span className="explore-review-badge"><TriangleAlert size={13} strokeWidth={1.9} aria-hidden="true" />{locale.explore.review}</span>}
      </div>
      <p className="mt-5 text-[1.0625rem] font-bold text-ink">{name}</p>
      <p className="mt-1 min-h-10 text-[0.8125rem] leading-6 text-slate-600">{item.mandate ?? locale.explore.unknownMandate}</p>
      <div className="explore-stat-panel mt-5 grid grid-cols-[1fr_auto_1fr] items-center gap-2">
        <p className="text-xs text-slate-500">{item.fromYear}<strong className="mt-1 block text-base text-ink tabular-nums">{formatCurrency(item.fromAmount, language)}</strong></p>
        <ArrowRight className="text-slate-400" size={15} strokeWidth={1.8} aria-hidden="true" />
        <p className="text-xs text-slate-500">{item.toYear}<strong className="mt-1 block text-base text-ink tabular-nums">{formatCurrency(item.toAmount, language)}</strong></p>
      </div>
      <p className="mt-4 text-xs font-semibold text-slate-500">{locale.explore.change}<strong className="ml-2 text-sm text-emerald tabular-nums">{change}</strong></p>
      {item.declarationUuid && <Link className="explore-card-action mt-auto" to={`/declarations/${item.declarationUuid}`}>{locale.explore.openDeclaration}<ArrowRight size={14} strokeWidth={1.9} aria-hidden="true" /></Link>}
    </article>
  );
}
