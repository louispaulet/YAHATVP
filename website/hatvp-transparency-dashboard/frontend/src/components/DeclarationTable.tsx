import { formatNumber } from "../formatters";
import { translateDataLabel, type Language } from "../config/i18n";
import { useI18n } from "../context/I18nContext";
import type { DashboardBreakdownResponse } from "../types";

export function DeclarationTable({ data, language }: { data: DashboardBreakdownResponse; language: Language }) {
  const { locale } = useI18n();
  return (
    <div className="overflow-x-auto">
      <table className="w-full table-fixed text-left text-sm">
        <thead className="border-b border-slate-200 text-xs uppercase tracking-[0.14em] text-slate-400"><tr><th className="w-full pb-3 font-bold">{locale.panels.declarationTypes.type}</th><th className="w-20 pb-3 text-right font-bold">{locale.panels.declarationTypes.rows}</th></tr></thead>
        <tbody className="divide-y divide-slate-100">{data.items.map((item) => <tr key={item.label}><td className="break-words py-3 font-semibold text-slate-700">{translateDataLabel(language, "declarationTypes", item.label)}</td><td className="w-20 whitespace-nowrap py-3 text-right font-bold text-ink">{formatNumber(item.rows, language)}</td></tr>)}</tbody>
      </table>
      {data.items.length === 0 && <p className="py-6 text-sm text-slate-500">{locale.panels.declarationTypes.empty}</p>}
    </div>
  );
}
