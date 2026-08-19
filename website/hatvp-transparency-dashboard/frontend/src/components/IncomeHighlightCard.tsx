import { Link } from "react-router-dom";
import { useI18n } from "../context/I18nContext";
import { formatCurrency } from "../formatters";
import type { IncomeChangeHighlight } from "../types";

export function IncomeHighlightCard({ item, rank }: { item: IncomeChangeHighlight; rank: number }) {
  const { language, locale } = useI18n();
  const name = `${item.firstName ?? ""} ${item.lastName ?? ""}`.trim() || locale.explore.unknownName;
  const change = `${item.absoluteChange > 0 ? "+" : ""}${formatCurrency(item.absoluteChange, language)}`;
  return (
    <article className="dashboard-card flex min-h-72 flex-col p-5">
      <div className="flex items-start justify-between gap-3">
        <span className="text-4xl font-black tracking-[-0.06em] text-slate-200">{String(rank).padStart(2, "0")}</span>
        {item.reviewRequired && <span className="rounded-full bg-amber-100 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide text-amber-900">{locale.explore.review}</span>}
      </div>
      <p className="mt-5 text-lg font-bold text-ink">{name}</p>
      <p className="mt-1 min-h-10 text-xs leading-5 text-slate-500">{item.mandate ?? locale.explore.unknownMandate}</p>
      <div className="mt-5 grid grid-cols-2 gap-3 border-y border-slate-100 py-4">
        <p className="text-xs text-slate-500">{item.fromYear}<strong className="mt-1 block text-base text-ink">{formatCurrency(item.fromAmount, language)}</strong></p>
        <p className="text-xs text-slate-500">{item.toYear}<strong className="mt-1 block text-base text-ink">{formatCurrency(item.toAmount, language)}</strong></p>
      </div>
      <p className="mt-4 text-xs font-semibold text-slate-500">{locale.explore.change}<strong className="ml-2 text-sm text-emerald">{change}</strong></p>
      {item.declarationUuid && <Link className="mt-auto pt-5 text-xs font-bold text-ink underline decoration-lime decoration-2 underline-offset-4" to={`/declarations/${item.declarationUuid}`}>{locale.explore.openDeclaration}</Link>}
    </article>
  );
}
