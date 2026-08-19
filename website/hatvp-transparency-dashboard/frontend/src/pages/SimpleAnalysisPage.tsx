import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useState } from "react";
import { fetchSimpleAnalysis } from "../api";
import { formatCurrency, formatNumber } from "../formatters";
import { ChartSkeleton, SliceError } from "../components/Feedback";
import { useResource } from "../hooks/useResource";
import { useI18n } from "../context/I18nContext";
import type { SimpleAnalysisLeader, SimpleAnalysisResponse } from "../types";

function displayName(leader: SimpleAnalysisLeader, fallback: string): string {
  return [leader.firstName, leader.lastName].filter(Boolean).join(" ") || fallback;
}

function displayDate(value: string | null, language: "en" | "fr", fallback: string): string {
  if (!value) return fallback;
  return new Intl.DateTimeFormat(language === "fr" ? "fr-FR" : "en-GB", { dateStyle: "medium" }).format(new Date(`${value}T00:00:00`));
}

function QualityBadge({ status, labels, fallback }: { status: string | null; labels: Record<string, string>; fallback: string }) {
  const review = status && status !== "valid";
  return <span className={`inline-flex max-w-full break-words rounded-full px-2.5 py-1 text-center text-[0.7rem] font-bold leading-4 ${review ? "bg-amber-100 text-amber-900" : "bg-sky/20 text-ink"}`}>{labels[status || ""] || fallback}</span>;
}

function Leaderboard({ leaders, title, eyebrow, locale, language }: { leaders: SimpleAnalysisLeader[]; title: string; eyebrow: string; locale: ReturnType<typeof useI18n>["locale"]; language: "en" | "fr" }) {
  return <section className="analysis-leaderboard"><p className="text-xs font-bold uppercase tracking-[0.16em] text-emerald">{eyebrow}</p><h2 className="mt-2 text-xl font-black tracking-tight text-ink">{title}</h2><div className="mt-5">{leaders.length === 0 && <p className="py-8 text-sm text-slate-500">{locale.simpleAnalysis.emptyLeaders}</p>}{leaders.length > 0 && <table className="w-full table-fixed border-collapse text-left text-[0.72rem] sm:text-sm"><colgroup><col className="w-[7%]" /><col className="w-[39%]" /><col className="w-[10%]" /><col className="w-[20%]" /><col className="w-[24%]" /></colgroup><thead><tr className="border-b border-slate-200 text-[0.62rem] uppercase tracking-[0.1em] text-slate-400 sm:text-xs"><th className="pb-3 pr-2">#</th><th className="pb-3 pr-2">{locale.search.resultEyebrow}</th><th className="pb-3 pr-2">{locale.simpleAnalysis.age}</th><th className="pb-3 pr-2">{locale.simpleAnalysis.dateOfBirth}</th><th className="pb-3">{locale.simpleAnalysis.quality}</th></tr></thead><tbody>{leaders.map((leader, index) => <tr key={`${leader.declarationUuid}-${index}`} className="border-b border-slate-100 last:border-0"><td className="py-3 pr-2 align-top font-mono text-xs text-slate-400">{index + 1}</td><td className="py-3 pr-2 align-top"><p className="break-words font-bold text-ink">{displayName(leader, locale.search.unknownDeclarant)}</p><p className="mt-1 break-words text-xs text-slate-500">{leader.mandate || leader.organ || locale.search.notAvailable}</p></td><td className="py-3 pr-2 align-top font-bold whitespace-nowrap text-ink">{formatNumber(leader.ageYears, language)}</td><td className="py-3 pr-2 align-top break-words text-slate-600">{displayDate(leader.dateOfBirth, language, locale.search.notAvailable)}</td><td className="py-3 align-top"><QualityBadge status={leader.qualityStatus} labels={locale.simpleAnalysis.qualityLabels} fallback={locale.search.notAvailable} /></td></tr>)}</tbody></table>}</div></section>;
}

type SalaryBin = SimpleAnalysisResponse["ageBins"][number];

function SalaryChart({ bins, language, locale }: { bins: SalaryBin[]; language: "en" | "fr"; locale: ReturnType<typeof useI18n>["locale"] }) {
  return <div role="img" aria-label={locale.simpleAnalysis.chartLabel} className="h-[21rem] min-w-0 sm:h-[25rem]"><ResponsiveContainer width="100%" height="100%"><LineChart data={bins} margin={{ top: 12, right: 16, bottom: 8, left: 0 }}><CartesianGrid vertical={false} stroke="#dbe3eb" strokeDasharray="3 5" /><XAxis dataKey="label" tick={{ fontSize: 11, fill: "#536275" }} axisLine={{ stroke: "#cbd5e1" }} tickLine={false} /><YAxis tickFormatter={(value) => formatCurrency(Number(value), language)} tick={{ fontSize: 11, fill: "#536275" }} axisLine={false} tickLine={false} width={72} /><Tooltip formatter={(value) => formatCurrency(Number(value), language)} /><Legend verticalAlign="top" align="right" iconType="plainline" wrapperStyle={{ fontSize: "12px", paddingBottom: "16px" }} /><Line type="monotone" dataKey="averageSalary" name={locale.simpleAnalysis.average} stroke="#0f3b78" strokeWidth={3} dot={{ r: 3, fill: "#f9fafb", strokeWidth: 2 }} activeDot={{ r: 5 }} /><Line type="monotone" dataKey="medianSalary" name={locale.simpleAnalysis.median} stroke="#5f8fc8" strokeWidth={2.5} strokeDasharray="5 5" dot={false} activeDot={{ r: 5 }} /></LineChart></ResponsiveContainer></div>;
}

export function SimpleAnalysisPage() {
  const { language, locale } = useI18n();
  const [excludeZeroSalary, setExcludeZeroSalary] = useState(true);
  const analysis = useResource(fetchSimpleAnalysis);
  const data = analysis.data;
  const salaryBins = !data ? [] : excludeZeroSalary ? data.ageBins : data.ageBinsIncludingZero.length > 0 ? data.ageBinsIncludingZero : data.ageBins;
  return <div className="analysis-page mx-auto max-w-[90rem] px-5 py-10 lg:px-10 lg:py-14">
    {analysis.loading && <div className="space-y-6"><ChartSkeleton /><ChartSkeleton /></div>}
    {analysis.error && <SliceError onRetry={analysis.reload} />}
    {data && <>
      <section className="analysis-overview-grid border-b border-slate-200 pb-10 lg:gap-14">
        <div className="analysis-intro"><p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.simpleAnalysis.eyebrow}</p><h1 className="mt-5 max-w-xl text-4xl font-black leading-[1.02] tracking-[-0.045em] text-[#102c57] sm:text-5xl lg:text-[3.6rem]">{locale.simpleAnalysis.title}</h1><p className="mt-6 max-w-lg text-base leading-7 text-slate-600">{locale.simpleAnalysis.description}</p><div className="mt-9 border-l-2 border-sky pl-4"><p className="text-sm font-bold text-ink">{locale.simpleAnalysis.reference}: {displayDate(data.referenceDate, language, locale.search.notAvailable)}</p><p className="mt-1 text-sm text-slate-500">{locale.simpleAnalysis.anomalyNote}</p></div></div>
        <section className="analysis-chart-hero" aria-labelledby="salary-by-age-heading"><div className="flex flex-wrap items-start justify-between gap-4"><div><p className="text-xs font-bold uppercase tracking-[0.16em] text-[#0f3b78]">{locale.simpleAnalysis.salaryEyebrow}</p><h2 id="salary-by-age-heading" className="mt-1 text-xl font-black tracking-tight text-ink">{locale.simpleAnalysis.salaryTitle}</h2></div><label className="analysis-toggle"><input type="checkbox" checked={excludeZeroSalary} onChange={(event) => setExcludeZeroSalary(event.target.checked)} className="size-4 accent-[#0f3b78]" />{locale.simpleAnalysis.excludeZeroSalary}</label></div><p className="mt-4 max-w-2xl text-sm leading-6 text-slate-500">{locale.simpleAnalysis.salaryDescription}</p>{salaryBins.length === 0 && <p className="py-8 text-sm text-slate-500">{locale.simpleAnalysis.emptySalary}</p>}{salaryBins.length > 0 && <SalaryChart bins={salaryBins} language={language} locale={locale} />}</section>
      </section>
      <section className="analysis-leaderboards grid gap-10 border-b border-slate-200 py-10 lg:grid-cols-2 lg:gap-14"><Leaderboard leaders={data.youngest} title={locale.simpleAnalysis.youngestTitle} eyebrow={locale.simpleAnalysis.youngestEyebrow} locale={locale} language={language} /><Leaderboard leaders={data.oldest} title={locale.simpleAnalysis.oldestTitle} eyebrow={locale.simpleAnalysis.oldestEyebrow} locale={locale} language={language} /></section>
      {salaryBins.length > 0 && <section className="analysis-bin-summary border-b border-slate-200 py-8"><p className="text-xs font-bold uppercase tracking-[0.16em] text-slate-500">{locale.simpleAnalysis.salaryEyebrow}</p><div className="mt-4 grid gap-x-7 gap-y-4 sm:grid-cols-2 lg:grid-cols-4">{salaryBins.map((bin) => <div key={bin.label} className="border-l border-slate-200 pl-4"><p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{bin.label}</p><p className="mt-2 text-sm font-bold text-ink">{formatCurrency(bin.averageSalary, language)} / {formatCurrency(bin.medianSalary, language)}</p><p className="mt-1 text-xs text-slate-500">{formatNumber(bin.rows, language)} {locale.simpleAnalysis.rows}</p></div>)}</div></section>}
      <section className="analysis-zero-salary py-10" aria-labelledby="zero-salary-heading"><p className="text-xs font-bold uppercase tracking-[0.16em] text-[#0f3b78]">{locale.simpleAnalysis.zeroSalaryEyebrow}</p><h2 id="zero-salary-heading" className="mt-2 text-2xl font-black tracking-tight text-ink">{locale.simpleAnalysis.zeroSalaryTitle}</h2><p className="mb-6 mt-4 max-w-3xl text-sm leading-6 text-slate-500">{locale.simpleAnalysis.zeroSalaryDescription}</p>{data.zeroSalaryBins.length === 0 && <p className="py-8 text-sm text-slate-500">{locale.simpleAnalysis.emptyZeroSalary}</p>}{data.zeroSalaryBins.length > 0 && <div role="img" aria-label={locale.simpleAnalysis.zeroSalaryChartLabel} className="h-[22rem] min-w-0"><ResponsiveContainer width="100%" height="100%"><BarChart data={data.zeroSalaryBins} margin={{ top: 8, right: 16, bottom: 8, left: 8 }}><CartesianGrid vertical={false} stroke="#dbe3eb" strokeDasharray="3 5" /><XAxis dataKey="label" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} /><YAxis allowDecimals={false} tickFormatter={(value) => formatNumber(Number(value), language)} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} width={56} /><Tooltip formatter={(value) => formatNumber(Number(value), language)} /><Bar dataKey="rows" name={locale.simpleAnalysis.zeroSalaryCount} fill="#b5c8e6" radius={[3, 3, 0, 0]} /></BarChart></ResponsiveContainer></div>}</section>
    </>}
  </div>;
}
