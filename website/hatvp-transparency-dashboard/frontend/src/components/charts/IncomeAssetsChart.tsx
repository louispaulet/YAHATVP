import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
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
  const total = chartData.reduce((sum, item) => sum + item.value, 0);
  const chartDescription = chartData.map((item) => `${item.displayLabel} ${formatCurrency(item.value, language)}`).join("; ");

  return (
    <div className="space-y-5">
      <div className="flex flex-col items-center gap-7 sm:flex-row sm:items-center">
        <div aria-label={`${chartLabel}: ${chartDescription}`} className="h-56 w-full min-w-0 sm:h-60" role="img"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={chartData} dataKey="value" nameKey="displayLabel" innerRadius={62} outerRadius={92} paddingAngle={3} animationBegin={120} animationDuration={900}>{chartData.map((item, index) => <Cell key={item.label} fill={chartColors[index]} />)}</Pie><Tooltip formatter={(value) => formatCurrency(Number(value), language)} /></PieChart></ResponsiveContainer></div>
        <div className="w-full min-w-0 space-y-4" aria-label={legendLabel}>{chartData.map((item, index) => { const percentage = total > 0 ? (item.value / total) * 100 : 100 / chartData.length; return <div key={item.label} className="flex items-start justify-between gap-4"><div className="flex min-w-0 flex-1 items-start gap-2.5"><span aria-hidden="true" className="mt-1.5 size-3 shrink-0 rounded-full" style={{ backgroundColor: chartColors[index] }} /><div className="min-w-0"><p className="break-words text-sm font-semibold leading-5 text-slate-700">{item.displayLabel}</p><p className="mt-1 text-xs text-slate-400">{formatNumber(item.rows, language)} {rowsLabel} · {percentage.toFixed(1)}%</p></div></div><span className="shrink-0 whitespace-nowrap text-right text-sm font-bold text-ink">{formatCurrency(item.value, language)}</span></div>; })}</div>
      </div>
      <div className="border-t border-slate-100 pt-4 text-xs leading-5 text-slate-500"><p>{fillTemplate(incomeExplanation, { average: formatCurrency(averageIncome, language), total: formatCurrency(Math.max(0, incomeTotal), language), years: formatNumber(incomeYearCount, language) })}</p><p className="mt-1">{fillTemplate(assetsExplanation, { assets: formatCurrency(Math.max(0, assetTotal), language) })}</p><p className="mt-1">{comparisonNote}</p></div>
    </div>
  );
}
