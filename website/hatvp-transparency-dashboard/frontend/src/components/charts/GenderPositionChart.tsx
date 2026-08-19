import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Language } from "../../config/i18n";
import { formatNumber } from "../../formatters";
import type { GenderPosition } from "../../types";

interface Props {
  positions: GenderPosition[];
  emptyLabel: string;
  language: Language;
  chartLabel: string;
  maleLabel: string;
  femaleLabel: string;
}

export default function GenderPositionChart({ positions, emptyLabel, language, chartLabel, maleLabel, femaleLabel }: Props) {
  if (positions.length === 0) return <p className="py-8 text-sm text-slate-500">{emptyLabel}</p>;
  return (
    <div className="w-full min-w-0" role="img" aria-label={chartLabel}>
      <div className="h-[27rem] min-w-0"><ResponsiveContainer width="100%" height="100%"><BarChart data={positions} layout="vertical" margin={{ top: 4, right: 16, bottom: 4, left: 8 }}><CartesianGrid horizontal={false} stroke="#e2e8f0" strokeDasharray="4 4" /><XAxis type="number" allowDecimals={false} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} /><YAxis dataKey="label" type="category" width={150} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} /><Tooltip formatter={(value) => formatNumber(Number(value), language)} /><Bar dataKey="male" name={maleLabel} fill="#1f9d75" radius={[0, 6, 6, 0]} /><Bar dataKey="female" name={femaleLabel} fill="#d96c86" radius={[0, 6, 6, 0]} /></BarChart></ResponsiveContainer></div>
      <div className="mt-5 grid gap-3 sm:grid-cols-2" aria-label={chartLabel}>{positions.map((item) => <div key={item.label} className="min-w-0 text-sm"><p className="truncate font-semibold text-slate-700">{item.label}</p><p className="mt-1 text-xs text-slate-500">{maleLabel}: {formatNumber(item.male, language)} · {femaleLabel}: {formatNumber(item.female, language)}</p></div>)}</div>
    </div>
  );
}
