import { formatNumber } from "../formatters";
import { translateDataLabel, type Language } from "../config/i18n";
import { useI18n } from "../context/I18nContext";
import type { DashboardBreakdownResponse } from "../types";

function isAmended(label: string): boolean {
  return /modificative|amended/i.test(label);
}

export function DeclarationComposition({ data, language }: { data: DashboardBreakdownResponse; language: Language }) {
  const { locale } = useI18n();
  const totalRows = data.items.reduce((sum, item) => sum + item.rows, 0);
  const amendedRows = data.items.filter((item) => isAmended(item.label)).reduce((sum, item) => sum + item.rows, 0);
  const originalRows = Math.max(totalRows - amendedRows, 0);
  const originalWidth = totalRows > 0 ? (originalRows / totalRows) * 100 : 0;
  const amendedWidth = totalRows > 0 ? (amendedRows / totalRows) * 100 : 0;
  const visibleItems = data.items.slice(0, 4);
  const hiddenItemCount = Math.max(data.items.length - visibleItems.length, 0);

  if (data.items.length === 0) return <p className="py-8 text-sm text-slate-500">{locale.panels.declarationTypes.empty}</p>;

  return (
    <div className="space-y-5">
      <div role="img" aria-label={`${locale.accessibility.declarationComposition}: ${formatNumber(originalRows, language)} ${locale.homepage.composition.original}, ${formatNumber(amendedRows, language)} ${locale.homepage.composition.amended}`}>
        <div className="flex h-4 overflow-hidden rounded-full bg-slate-100">
          {originalWidth > 0 && <span className="bg-emerald" style={{ width: `${originalWidth}%` }} />}
          {amendedWidth > 0 && <span className="bg-sky" style={{ width: `${amendedWidth}%` }} />}
        </div>
        <div className="mt-4 grid gap-3 sm:grid-cols-2" aria-label={locale.accessibility.declarationLegend}>
          <div className="flex items-start gap-2.5"><span className="mt-1 size-3 shrink-0 rounded-full bg-emerald" aria-hidden="true" /><div><p className="text-sm font-bold text-ink">{formatNumber(originalRows, language)}</p><p className="text-xs leading-5 text-slate-500">{locale.homepage.composition.original}</p></div></div>
          <div className="flex items-start gap-2.5"><span className="mt-1 size-3 shrink-0 rounded-full bg-sky" aria-hidden="true" /><div><p className="text-sm font-bold text-ink">{formatNumber(amendedRows, language)}</p><p className="text-xs leading-5 text-slate-500">{locale.homepage.composition.amended}</p></div></div>
        </div>
      </div>
      <div className="border-t border-slate-100 pt-4">
        <p className="text-xs leading-5 text-slate-500">{locale.homepage.composition.explanation}</p>
        <ul className="mt-4 space-y-2" aria-label={locale.panels.declarationTypes.title}>
          {visibleItems.map((item) => <li key={item.label} className="flex min-w-0 items-center justify-between gap-4 text-sm"><span className="min-w-0 break-words font-semibold text-slate-700">{translateDataLabel(language, "declarationTypes", item.label)}</span><span className="shrink-0 font-bold text-ink">{formatNumber(item.rows, language)}</span></li>)}
        </ul>
        {hiddenItemCount > 0 && <p className="mt-3 text-xs font-semibold text-slate-400">{locale.homepage.composition.more.replace("{count}", formatNumber(hiddenItemCount, language))}</p>}
      </div>
    </div>
  );
}
