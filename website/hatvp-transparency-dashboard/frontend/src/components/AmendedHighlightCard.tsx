import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import { useI18n } from "../context/I18nContext";
import type { AmendedRecordHighlight } from "../types";

export function AmendedHighlightCard({ item, rank }: { item: AmendedRecordHighlight; rank: number }) {
  const { locale } = useI18n();
  const name = `${item.firstName ?? ""} ${item.lastName ?? ""}`.trim() || locale.explore.unknownName;
  return (
    <article className="explore-card explore-card--amended flex min-h-[18rem] flex-col p-5 sm:p-[1.375rem]">
      <span className="explore-card-rank">#{String(rank).padStart(2, "0")}</span>
      <p className="mt-5 text-[1.0625rem] font-bold text-ink">{name}</p>
      <p className="mt-1 min-h-10 text-[0.8125rem] leading-6 text-slate-600">{item.mandate ?? locale.explore.unknownMandate}</p>
      <div className="mt-5 grid grid-cols-2 gap-3">
        <div className="explore-stat-tile explore-stat-tile--neutral"><p className="text-xs text-slate-500">{locale.explore.filings}</p><strong className="mt-2 block text-2xl text-ink tabular-nums">{item.filingCount}</strong></div>
        <div className="explore-stat-tile explore-stat-tile--sky"><p className="text-xs text-slate-600">{locale.explore.amendments}</p><strong className="mt-2 block text-2xl text-ink tabular-nums">{item.amendedCount}</strong></div>
      </div>
      {item.declarationUuid && <Link className="explore-card-action mt-auto" to={`/declarations/${item.declarationUuid}`}>{locale.explore.openLatest}<ArrowRight size={14} strokeWidth={1.9} aria-hidden="true" /></Link>}
    </article>
  );
}
