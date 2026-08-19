import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import type { Language } from "../../config/i18n";
import { formatNumber } from "../../formatters";
import type { BreakdownItem } from "../../types";

const colors = ["#1f9d75", "#d96c86"];

interface Props {
  items: BreakdownItem[];
  unknownRows: number;
  emptyLabel: string;
  language: Language;
  chartLabel: string;
  legendLabel: string;
  maleLabel: string;
  femaleLabel: string;
  unknownNote: string;
}

function fillTemplate(template: string, count: string): string {
  return template.replace("{count}", count);
}

export default function GenderRatioChart({ items, unknownRows, emptyLabel, language, chartLabel, legendLabel, maleLabel, femaleLabel, unknownNote }: Props) {
  const labels: Record<string, string> = { male: maleLabel, female: femaleLabel };
  const data = items.filter((item) => labels[item.label]).map((item) => ({ ...item, displayLabel: labels[item.label] }));
  if (data.length === 0) return <p className="py-8 text-sm text-slate-500">{emptyLabel}</p>;
  const total = data.reduce((sum, item) => sum + item.rows, 0);
  const description = data.map((item) => `${item.displayLabel} ${formatNumber(item.rows, language)}`).join("; ");
  return (
    <div className="space-y-5">
      <div className="flex flex-col items-center gap-7 sm:flex-row">
        <div className="h-56 w-full min-w-0 sm:h-60" role="img" aria-label={`${chartLabel}: ${description}`}>
          <ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={data} dataKey="rows" nameKey="displayLabel" innerRadius={62} outerRadius={92} paddingAngle={3}>{data.map((item, index) => <Cell key={item.label} fill={colors[index]} />)}</Pie><Tooltip formatter={(value) => formatNumber(Number(value), language)} /></PieChart></ResponsiveContainer>
        </div>
        <div className="w-full min-w-0 space-y-4" aria-label={legendLabel}>{data.map((item, index) => <div key={item.label} className="flex items-center justify-between gap-4"><div className="flex min-w-0 items-center gap-2.5"><span aria-hidden="true" className="size-3 shrink-0 rounded-full" style={{ backgroundColor: colors[index] }} /><span className="break-words text-sm font-semibold text-slate-700">{item.displayLabel}</span></div><span className="shrink-0 text-sm font-bold text-ink">{formatNumber(item.rows, language)} · {total ? ((item.rows / total) * 100).toFixed(1) : "0.0"}%</span></div>)}</div>
      </div>
      {unknownRows > 0 && <p className="border-t border-slate-100 pt-4 text-xs leading-5 text-slate-500">{fillTemplate(unknownNote, formatNumber(unknownRows, language))}</p>}
    </div>
  );
}
