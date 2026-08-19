import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Language, Locale } from "../config/i18n";
import { formatCurrency } from "../formatters";
import type { AgeAnalysisResponse } from "../types";
import { Panel } from "./Panel";

type Labels = Locale["ageAnalysis"];
type IncomeYear = AgeAnalysisResponse["incomeByYear"][number];

function sourceKind(value: string | null, labels: Labels): string {
  const kinds = labels.incomeKinds as Record<string, string>;
  return kinds[value || ""] || labels.incomeKinds.income;
}

function period(start: string | null, end: string | null, labels: Labels): string | null {
  if (!start && !end) return null;
  return `${start || labels.unknown} → ${end || labels.current}`;
}

function IncomeSources({ year, language, labels }: {
  year: IncomeYear; language: Language; labels: Labels;
}) {
  return (
    <article className="rounded-2xl border border-slate-100 bg-canvas/70 p-4 sm:p-5">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="text-lg font-black text-ink">{year.year}</h3>
        <span className="text-sm font-black text-emerald">{formatCurrency(year.combinedAmount, language)} <span className="font-medium text-slate-500">{labels.sourceReported}</span></span>
      </div>
      <ul className="mt-4 grid gap-3 lg:grid-cols-2">
        {year.sources.map((source) => <li key={source.sourceId} className="rounded-xl border border-slate-200 bg-white p-4"><div className="flex items-start justify-between gap-3"><span className="rounded-full bg-slate-100 px-2.5 py-1 text-[0.68rem] font-bold uppercase tracking-wide text-slate-600">{sourceKind(source.kind, labels)}</span><span className="shrink-0 font-black text-ink">{formatCurrency(source.amount, language)}</span></div><p className="mt-3 font-bold leading-5 text-slate-800">{source.label || labels.unknown}</p>{source.employer && <p className="mt-1 text-sm text-slate-500">{source.employer}</p>}<dl className="mt-3 space-y-1 text-xs text-slate-500">{period(source.startDate, source.endDate, labels) && <div><dt className="inline font-semibold">{labels.period}: </dt><dd className="inline">{period(source.startDate, source.endDate, labels)}</dd></div>}{source.basis && <div><dt className="inline font-semibold">{labels.basis}: </dt><dd className="inline">{source.basis}</dd></div>}</dl></li>)}
      </ul>
    </article>
  );
}

export function AgeIncomePanel({ income, language, labels }: {
  income: AgeAnalysisResponse["incomeByYear"]; language: Language; labels: Labels;
}) {
  const hasReview = income.some((year) => year.sources.some((source) => !source.metricEligible));
  return (
    <div className="mt-6">
      <Panel title={labels.incomeTitle} eyebrow={labels.incomeEyebrow}>
        <p className="max-w-4xl text-sm leading-6 text-slate-500">{labels.incomeDescription}</p>
        {hasReview && <aside className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950"><p className="font-bold">{labels.reviewWarningTitle}</p><p className="mt-1 leading-6">{labels.reviewWarningDescription}</p></aside>}
        {income.length === 0 && <p className="py-8 text-sm text-slate-500">{labels.noIncome}</p>}
        {income.length > 0 && <><div role="img" aria-label={labels.incomeChartLabel} className="mt-6 h-72 min-w-0"><ResponsiveContainer width="100%" height="100%"><BarChart data={income} margin={{ top: 8, right: 8, bottom: 8, left: 0 }}><CartesianGrid vertical={false} stroke="#e2e8f0" strokeDasharray="4 4" /><XAxis dataKey="year" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} /><YAxis tickFormatter={(value) => formatCurrency(Number(value), language)} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} width={74} /><Tooltip formatter={(value) => [formatCurrency(Number(value), language), labels.sourceReportedTotal]} /><Bar dataKey="combinedAmount" name={labels.sourceReportedTotal} fill="#1f9d75" radius={[8, 8, 0, 0]} /></BarChart></ResponsiveContainer></div><div className="mt-6 space-y-4">{income.map((year) => <IncomeSources key={year.year} year={year} language={language} labels={labels} />)}</div></>}
      </Panel>
    </div>
  );
}
