import type { Language } from "../config/i18n";
import { formatNumber } from "../formatters";

interface MetricCardProps {
  label: string;
  value: number;
  detail?: string;
  unit?: string;
  caveat?: string;
  accent: string;
  language: Language;
}

export function MetricCard({ label, value, detail, unit, caveat, accent, language }: MetricCardProps) {
  return (
    <div className="min-w-0 border-l-2 border-white/25 pl-4 first:border-l-0 first:pl-0 sm:pl-5">
      <span className={`mb-4 block size-2.5 rounded-full ${accent}`} aria-hidden="true" />
      <p className="text-sm font-semibold text-slate-300">{label}</p>
      <p className="mt-2 text-3xl font-black tracking-[-0.05em] text-white sm:text-4xl">{formatNumber(value, language)}</p>
      {(detail || unit) && <p className="mt-1 text-xs font-medium uppercase tracking-[0.13em] text-slate-400">{detail || unit}</p>}
      {caveat && <p className="mt-2 max-w-[15rem] text-xs leading-5 text-slate-400">{caveat}</p>}
    </div>
  );
}
