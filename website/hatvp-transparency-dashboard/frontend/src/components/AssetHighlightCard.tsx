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
    <article className="dashboard-card flex min-h-72 flex-col p-5">
      <div className="flex items-start justify-between gap-3">
        <span className="text-4xl font-black tracking-[-0.06em] text-slate-200">{String(rank).padStart(2, "0")}</span>
        {item.reviewRequired && <span className="rounded-full bg-amber-100 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide text-amber-900">{locale.explore.review}</span>}
      </div>
      <p className="mt-5 text-xs font-bold uppercase tracking-[0.12em] text-emerald">{section}</p>
      <p className="mt-2 text-xl font-black tracking-tight text-ink">{formatCurrency(item.amount, language)}</p>
      <p className="mt-2 min-h-10 text-sm leading-5 text-slate-600">{item.assetName ?? locale.explore.unknownAsset}</p>
      <div className="mt-5 border-t border-slate-100 pt-4"><p className="font-bold text-ink">{name}</p><p className="mt-1 text-xs leading-5 text-slate-500">{item.mandate ?? locale.explore.unknownMandate}</p></div>
      {item.declarationUuid && <Link className="mt-auto pt-5 text-xs font-bold text-ink underline decoration-lime decoration-2 underline-offset-4" to={`/declarations/${item.declarationUuid}`}>{locale.explore.openDeclaration}</Link>}
    </article>
  );
}
