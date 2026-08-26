import { formatCurrency, formatNumber } from "../../formatters";
import type { Language } from "../../config/i18n";
import type { BreakdownItem } from "../../types";

const chartColors = ["#1f9d75", "#54b8d0"];
interface Props {
  incomeItems: BreakdownItem[]; assetItems: BreakdownItem[]; incomeTotal: number; assetTotal: number;
  incomeYearCount: number; emptyLabel: string; language: Language; chartLabel: string; legendLabel: string;
  rowsLabel: string; incomeLabel: string; assetsLabel: string; incomeExplanation: string; assetsExplanation: string; comparisonNote: string;
}

const sumRows = (items: BreakdownItem[]) => items.reduce((sum, item) => sum + item.rows, 0);
const fillTemplate = (template: string, values: Record<string, string>) => Object.entries(values).reduce((result, [key, value]) => result.replaceAll(`{${key}}`, value), template);

export default function IncomeAssetsChart({ incomeItems, assetItems, incomeTotal, assetTotal, incomeYearCount, emptyLabel, language, chartLabel, legendLabel, rowsLabel, incomeLabel, assetsLabel, incomeExplanation, assetsExplanation, comparisonNote }: Props) {
  if (incomeItems.length === 0 && assetItems.length === 0) return <p className="py-8 text-sm text-slate-500">{emptyLabel}</p>;
  const averageIncome = incomeYearCount > 0 ? Math.max(0, incomeTotal) / incomeYearCount : Math.max(0, incomeTotal);
  const chartData = [{ label: "income", displayLabel: incomeLabel, rows: sumRows(incomeItems), value: averageIncome }, { label: "assets", displayLabel: assetsLabel, rows: sumRows(assetItems), value: Math.max(0, assetTotal) }];
  const scale = Math.max(...chartData.map((item) => item.value), 1);
  const chartDescription = chartData.map((item) => `${item.displayLabel} ${formatCurrency(item.value, language)}`).join("; ");

  return (
    <div className="space-y-5">
      <div aria-label={`${chartLabel}: ${chartDescription}`} className="space-y-5" role="img">
        {chartData.map((item, index) => {
          const width = item.value > 0 ? Math.max((item.value / scale) * 100, 4) : 0;
          return (
            <div key={item.label}>
              <div className="flex items-end justify-between gap-3">
                <div className="flex min-w-0 items-center gap-2.5">
                  <span aria-hidden="true" className="size-3 shrink-0 rounded-full" style={{ backgroundColor: chartColors[index] }} />
                  <p className="break-words text-sm font-semibold leading-5 text-slate-700">{item.displayLabel}</p>
                </div>
                <span className="shrink-0 whitespace-nowrap text-right text-lg font-black tracking-tight text-ink">{formatCurrency(item.value, language)}</span>
              </div>
              <div className="mt-2 h-3 overflow-hidden rounded-full bg-slate-100" aria-hidden="true"><div className="h-full rounded-full transition-[width] duration-700" style={{ width: `${width}%`, backgroundColor: chartColors[index] }} /></div>
              <p className="mt-1 text-xs text-slate-400">{formatNumber(item.rows, language)} {rowsLabel}</p>
            </div>
          );
        })}
      </div>
      <div className="border-t border-slate-100 pt-4 text-xs leading-5 text-slate-500" aria-label={legendLabel}><p>{fillTemplate(incomeExplanation, { average: formatCurrency(averageIncome, language), total: formatCurrency(Math.max(0, incomeTotal), language), years: formatNumber(incomeYearCount, language) })}</p><p className="mt-1">{fillTemplate(assetsExplanation, { assets: formatCurrency(Math.max(0, assetTotal), language) })}</p><p className="mt-1">{comparisonNote}</p></div>
    </div>
  );
}
