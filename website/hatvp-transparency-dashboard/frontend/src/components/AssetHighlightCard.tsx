import { ArrowRight, TriangleAlert } from "lucide-react";
import { Link } from "react-router-dom";
import { translateDataLabel } from "../config/i18n";
import { useI18n } from "../context/I18nContext";
import { formatCurrency } from "../formatters";
import type { AssetHighlight } from "../types";

export function AssetHighlightCard({ item, rank }: { item: AssetHighlight; rank: number }) {
  const { language, locale } = useI18n();
  const name = `${item.firstName ?? ""} ${item.lastName ?? ""}`.trim() || locale.explore.unknownName;
  const section = item.section ? translateDataLabel(language, "assetSections", item.section) : locale.explore.unknownAsset;
  return (
    <article className="explore-card explore-card--asset flex min-h-[20rem] flex-col p-5 sm:p-[1.375rem]">
      <div className="flex items-start justify-between gap-3">
        <span className="explore-card-rank">#{String(rank).padStart(2, "0")}</span>
        {item.reviewRequired && <span className="explore-review-badge"><TriangleAlert size={13} strokeWidth={1.9} aria-hidden="true" />{locale.explore.review}</span>}
      </div>
      <p className="explore-card-category explore-card-category--asset mt-5">{section}</p>
      <p className="mt-3 font-display text-[1.65rem] font-bold tracking-tight text-ink tabular-nums">{formatCurrency(item.amount, language)}</p>
      <p className="mt-2 text-sm leading-6 text-slate-600">{item.assetName ?? locale.explore.unknownAsset}</p>
      <div className="mt-5 border-t border-slate-100 pt-4"><p className="font-bold text-ink">{name}</p><p className="mt-1 text-[0.8125rem] leading-6 text-slate-600">{item.mandate ?? locale.explore.unknownMandate}</p></div>
      {item.declarationUuid && <Link className="explore-card-action mt-auto" to={`/declarations/${item.declarationUuid}`}>{locale.explore.openDeclaration}<ArrowRight size={14} strokeWidth={1.9} aria-hidden="true" /></Link>}
    </article>
  );
}
