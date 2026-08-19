import { Link } from "react-router-dom";
import { useI18n } from "../context/I18nContext";
import type { AmendedRecordHighlight } from "../types";

export function AmendedHighlightCard({ item, rank }: { item: AmendedRecordHighlight; rank: number }) {
  const { locale } = useI18n();
  const name = `${item.firstName ?? ""} ${item.lastName ?? ""}`.trim() || locale.explore.unknownName;
  return (
    <article className="dashboard-card flex min-h-64 flex-col p-5">
      <span className="text-4xl font-black tracking-[-0.06em] text-slate-200">{String(rank).padStart(2, "0")}</span>
      <p className="mt-5 text-lg font-bold text-ink">{name}</p>
      <p className="mt-1 min-h-10 text-xs leading-5 text-slate-500">{item.mandate ?? locale.explore.unknownMandate}</p>
      <div className="mt-5 grid grid-cols-2 gap-3 border-y border-slate-100 py-4">
        <p className="text-xs text-slate-500">{locale.explore.filings}<strong className="mt-1 block text-2xl text-ink">{item.filingCount}</strong></p>
        <p className="text-xs text-slate-500">{locale.explore.amendments}<strong className="mt-1 block text-2xl text-emerald">{item.amendedCount}</strong></p>
      </div>
      {item.declarationUuid && <Link className="mt-auto pt-5 text-xs font-bold text-ink underline decoration-lime decoration-2 underline-offset-4" to={`/declarations/${item.declarationUuid}`}>{locale.explore.openLatest}</Link>}
    </article>
  );
}
