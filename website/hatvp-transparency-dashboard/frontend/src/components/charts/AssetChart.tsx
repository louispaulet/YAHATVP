import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { translateDataLabel, type Language } from "../../config/i18n";
import { formatCurrency } from "../../formatters";
import type { BreakdownItem } from "../../types";

const chartColors = ["#1f9d75", "#54b8d0", "#8c76c7", "#d0a640"];

export default function AssetChart({ items, emptyLabel, language }: { items: BreakdownItem[]; emptyLabel: string; language: Language }) {
  if (items.length === 0) return <p className="py-8 text-sm text-slate-500">{emptyLabel}</p>;
  const chartData = items.map((item) => ({ ...item, displayLabel: translateDataLabel(language, "assetSections", item.label), value: item.totalValue ?? item.rows }));
  const chartHeight = Math.max(300, Math.min(440, chartData.length * 36 + 44));
  return (
    <div className="w-full min-w-0" role="img" aria-label={emptyLabel}>
      <div className="min-w-0" style={{ height: `${chartHeight}px` }}><ResponsiveContainer width="100%" height="100%"><BarChart data={chartData} layout="vertical" margin={{ top: 4, right: 12, bottom: 4, left: 8 }}><CartesianGrid horizontal={false} stroke="#e2e8f0" strokeDasharray="4 4" /><XAxis type="number" tickFormatter={(value) => formatCurrency(Number(value), language)} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} /><YAxis dataKey="displayLabel" type="category" width={142} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} /><Tooltip formatter={(value) => formatCurrency(Number(value), language)} /><Bar dataKey="value" radius={[0, 8, 8, 0]} animationBegin={160} animationDuration={1000}>{chartData.map((item, index) => <Cell key={item.label} fill={chartColors[index % chartColors.length]} />)}</Bar></BarChart></ResponsiveContainer></div>
      <div className="mt-6 grid gap-x-6 gap-y-2 border-t border-slate-100 pt-5 sm:grid-cols-2" aria-label="Asset chart values">{chartData.map((item) => <div key={item.label} className="flex min-w-0 items-center justify-between gap-3 text-sm"><span className="min-w-0 truncate font-semibold text-slate-700">{item.displayLabel}</span><span className="shrink-0 font-bold text-ink">{formatCurrency(item.value, language)}</span></div>)}</div>
    </div>
  );
}
