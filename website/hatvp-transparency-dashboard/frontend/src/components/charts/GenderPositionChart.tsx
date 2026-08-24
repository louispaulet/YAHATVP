import { Bar, BarChart, CartesianGrid, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Language } from "../../config/i18n";
import { formatNumber, formatPercentage } from "../../formatters";
import type { GenderPosition } from "../../types";

interface Props {
  positions: GenderPosition[];
  emptyLabel: string;
  language: Language;
  chartLabel: string;
  legendLabel: string;
  womenLabel: string;
  parityLabel: string;
  peopleLabel: string;
  noteLabel: string;
}

interface PositionDatum extends GenderPosition {
  total: number;
  womenPercentage: number;
}

interface PositionTickProps {
  x?: number;
  y?: number;
  payload?: { value?: string | number };
}

function wrapPositionLabel(label: string): string[] {
  const words = label.trim().split(/\s+/);
  const lines: string[] = [];
  let current = "";
  for (const word of words) {
    const next = current ? `${current} ${word}` : word;
    if (!current || next.length <= 29) current = next;
    else {
      lines.push(current);
      current = word;
    }
  }
  if (current) lines.push(current);
  if (lines.length <= 2) return lines;
  return [lines[0], `${lines.slice(1).join(" ").slice(0, 27).trimEnd()}…`];
}

function PositionTick({ x = 0, y = 0, payload }: PositionTickProps) {
  const lines = wrapPositionLabel(String(payload?.value ?? ""));
  const lineHeight = 13;
  const firstOffset = -((lines.length - 1) * lineHeight) / 2;
  return (
    <g transform={`translate(${x},${y})`}>
      <text x={-10} textAnchor="end" dominantBaseline="middle" fill="#64748b" fontSize={11}>
        {lines.map((line, index) => <tspan key={`${line}-${index}`} x={-10} dy={index === 0 ? firstOffset : lineHeight}>{line}</tspan>)}
      </text>
    </g>
  );
}

function toChartData(positions: GenderPosition[]): PositionDatum[] {
  return positions.map((item) => {
    const total = item.male + item.female + item.unknown;
    return { ...item, total, womenPercentage: total ? (item.female / total) * 100 : 0 };
  });
}

export default function GenderPositionChart({ positions, emptyLabel, language, chartLabel, legendLabel, womenLabel, parityLabel, peopleLabel, noteLabel }: Props) {
  if (positions.length === 0) return <p className="py-8 text-sm text-slate-500">{emptyLabel}</p>;
  const data = toChartData(positions);
  const chartHeight = Math.max(500, Math.min(820, data.length * 60 + 50));
  const description = data.map((item) => `${item.label}: ${formatPercentage(item.womenPercentage, language)}, ${formatNumber(item.total, language)} ${peopleLabel}`).join("; ");
  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-slate-600" aria-label={legendLabel}>
        <span className="flex items-center gap-2"><span aria-hidden="true" className="size-3 shrink-0 rounded-full bg-[#d96c86]" />{womenLabel}</span>
        <span className="flex items-center gap-2"><span aria-hidden="true" className="w-5 border-t-2 border-dashed border-slate-400" />{parityLabel}</span>
      </div>
      <div className="w-full min-w-0" role="img" aria-label={`${chartLabel}: ${description}`}>
        <div className="min-w-0" style={{ height: `${chartHeight}px` }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ top: 8, right: 24, bottom: 8, left: 8 }}>
              <CartesianGrid horizontal={false} stroke="#e2e8f0" strokeDasharray="4 4" />
              <XAxis type="number" domain={[0, 100]} ticks={[0, 25, 50, 75, 100]} tickFormatter={(value) => `${value}%`} allowDecimals={false} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis dataKey="label" type="category" width={220} interval={0} tick={<PositionTick />} axisLine={false} tickLine={false} />
              <ReferenceLine x={50} stroke="#94a3b8" strokeDasharray="4 4" />
              <Tooltip formatter={(value) => formatPercentage(Number(value), language)} />
              <Bar dataKey="womenPercentage" name={womenLabel} fill="#d96c86" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-6 grid gap-3 border-t border-slate-100 pt-5 sm:grid-cols-2" aria-label={chartLabel}>
          {data.map((item, index) => (
            <div key={item.label} className="min-w-0 rounded-xl border border-slate-100 bg-slate-50/70 p-3">
              <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
                <p className="min-w-0 flex-1 break-words text-sm font-semibold text-slate-700">{index + 1}. {item.label}</p>
                <p className="shrink-0 whitespace-nowrap text-sm font-bold text-ink">{formatPercentage(item.womenPercentage, language)}</p>
              </div>
              <p className="mt-1 text-xs text-slate-500">{formatNumber(item.total, language)} {peopleLabel}</p>
            </div>
          ))}
        </div>
      </div>
      <p className="border-t border-slate-100 pt-4 text-xs leading-5 text-slate-500">{noteLabel}</p>
    </div>
  );
}
