import { formatNumber } from "../formatters";
import type { Language } from "../config/i18n";

interface MetricCardProps {
  label: string;
  value: number;
  detail: string;
  accent: string;
  language: Language;
}

export function MetricCard({ label, value, detail, accent, language }: MetricCardProps) {
  return (
    <article className="dashboard-card relative overflow-hidden p-6 transition duration-200 hover:-translate-y-0.5 hover:shadow-lg">
      <span className={`absolute inset-x-0 top-0 h-1 ${accent}`} />
      <p className="text-sm font-semibold text-slate-500">{label}</p>
      <p className="mt-4 text-4xl font-black tracking-[-0.04em] text-ink">{formatNumber(value, language)}</p>
      <p className="mt-2 text-xs font-medium uppercase tracking-[0.14em] text-slate-400">{detail}</p>
    </article>
  );
}
