import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { translateDataLabel } from "./config/i18n";
import type { Language } from "./config/i18n";
import { formatCurrency, formatNumber } from "./formatters";
import type { BreakdownItem } from "./types";

const chartColors = ["#1f9d75", "#54b8d0", "#8c76c7", "#d0a640"];

interface IncomeAssetsChartProps {
  incomeItems: BreakdownItem[];
  assetItems: BreakdownItem[];
  incomeTotal: number;
  assetTotal: number;
  incomeYearCount: number;
  emptyLabel: string;
  language: Language;
  chartLabel: string;
  legendLabel: string;
  rowsLabel: string;
  incomeLabel: string;
  assetsLabel: string;
  incomeExplanation: string;
  assetsExplanation: string;
  comparisonNote: string;
}

function sumBreakdownRows(items: BreakdownItem[]): number {
  return items.reduce((sum, item) => sum + item.rows, 0);
}

function fillTemplate(template: string, values: Record<string, string>): string {
  return Object.entries(values).reduce((result, [key, value]) => result.replaceAll(`{${key}}`, value), template);
}

export function IncomeAssetsChart({ incomeItems, assetItems, incomeTotal, assetTotal, incomeYearCount, emptyLabel, language, chartLabel, legendLabel, rowsLabel, incomeLabel, assetsLabel, incomeExplanation, assetsExplanation, comparisonNote }: IncomeAssetsChartProps) {
  if (incomeItems.length === 0 && assetItems.length === 0) return <p className="py-8 text-sm text-slate-500">{emptyLabel}</p>;
  const averageIncome = incomeYearCount > 0 ? Math.max(0, incomeTotal) / incomeYearCount : Math.max(0, incomeTotal);
  const observedAssets = Math.max(0, assetTotal);
  const chartData = [
    { label: "income", displayLabel: incomeLabel, rows: sumBreakdownRows(incomeItems), value: averageIncome },
    { label: "assets", displayLabel: assetsLabel, rows: sumBreakdownRows(assetItems), value: observedAssets },
  ];
  const total = chartData.reduce((sum, item) => sum + item.value, 0);
  const chartDescription = chartData
    .map((item) => `${item.displayLabel} ${formatCurrency(item.value, language)}`)
    .join("; ");

  return (
    <div className="space-y-5">
      <div className="flex flex-col items-center gap-7 sm:flex-row sm:items-center">
        <div aria-label={`${chartLabel}: ${chartDescription}`} className="h-56 w-full min-w-0 sm:h-60" role="img">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={chartData} dataKey="value" nameKey="displayLabel" innerRadius={62} outerRadius={92} paddingAngle={3} animationBegin={120} animationDuration={900}>
                {chartData.map((item, index) => <Cell key={item.label} fill={chartColors[index % chartColors.length]} />)}
              </Pie>
              <Tooltip formatter={(value) => formatCurrency(Number(value), language)} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="w-full min-w-0 space-y-4" aria-label={legendLabel}>
          {chartData.map((item, index) => {
            const percentage = total > 0 ? (item.value / total) * 100 : 100 / chartData.length;
            return (
              <div key={item.label} className="flex items-start justify-between gap-4">
                <div className="flex min-w-0 items-start gap-2.5">
                  <span aria-hidden="true" className="mt-1.5 size-3 shrink-0 rounded-full" style={{ backgroundColor: chartColors[index % chartColors.length] }} />
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-slate-700">{item.displayLabel}</p>
                    <p className="mt-1 text-xs text-slate-400">{formatNumber(item.rows, language)} {rowsLabel} · {percentage.toFixed(1)}%</p>
                  </div>
                </div>
                <span className="shrink-0 text-right text-sm font-bold text-ink">{formatCurrency(item.value, language)}</span>
              </div>
            );
          })}
        </div>
      </div>
      <div className="border-t border-slate-100 pt-4 text-xs leading-5 text-slate-500">
        <p>{fillTemplate(incomeExplanation, { average: formatCurrency(averageIncome, language), total: formatCurrency(Math.max(0, incomeTotal), language), years: formatNumber(incomeYearCount, language) })}</p>
        <p className="mt-1">{fillTemplate(assetsExplanation, { assets: formatCurrency(observedAssets, language) })}</p>
        <p className="mt-1">{comparisonNote}</p>
      </div>
    </div>
  );
}

interface AssetChartProps {
  items: BreakdownItem[];
  emptyLabel: string;
  language: Language;
}

export function AssetChart({ items, emptyLabel, language }: AssetChartProps) {
  if (items.length === 0) return <p className="py-8 text-sm text-slate-500">{emptyLabel}</p>;
  const chartData = items.map((item) => ({
    ...item,
    displayLabel: translateDataLabel(language, "assetSections", item.label),
    value: item.totalValue ?? item.rows,
  }));
  return (
    <div className="w-full min-w-0" role="img" aria-label={emptyLabel}>
      <div className="h-[25rem] min-w-0">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ top: 4, right: 20, bottom: 4, left: 8 }}>
            <CartesianGrid horizontal={false} stroke="#e2e8f0" strokeDasharray="4 4" />
            <XAxis type="number" tickFormatter={(value) => formatCurrency(Number(value), language)} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis dataKey="displayLabel" type="category" width={126} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip formatter={(value) => formatCurrency(Number(value), language)} />
            <Bar dataKey="value" radius={[0, 8, 8, 0]} animationBegin={160} animationDuration={1000}>
              {chartData.map((item, index) => <Cell key={item.label} fill={chartColors[index % chartColors.length]} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-5 grid gap-3 sm:grid-cols-2" aria-label="Asset chart values">
        {chartData.map((item) => (
          <div key={item.label} className="flex min-w-0 items-center justify-between gap-3 text-sm">
            <span className="min-w-0 truncate font-semibold text-slate-700">{item.displayLabel}</span>
            <span className="shrink-0 font-bold text-ink">{formatCurrency(item.value, language)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
