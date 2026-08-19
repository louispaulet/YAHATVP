import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useState } from "react";
import { fetchSimpleAnalysis } from "../api";
import { formatCurrency, formatNumber } from "../formatters";
import { ChartSkeleton, SliceError } from "../components/Feedback";
import { Panel } from "../components/Panel";
import { useResource } from "../hooks/useResource";
import { useI18n } from "../context/I18nContext";
import type { SimpleAnalysisLeader, SimpleAnalysisResponse } from "../types";

function displayName(leader: SimpleAnalysisLeader, fallback: string): string {
  return [leader.firstName, leader.lastName].filter(Boolean).join(" ") || fallback;
}

function displayDate(value: string | null, language: "en" | "fr", fallback: string): string {
  if (!value) return fallback;
  return new Intl.DateTimeFormat(language === "fr" ? "fr-FR" : "en-GB", {
    dateStyle: "medium",
  }).format(new Date(`${value}T00:00:00`));
}

function QualityBadge({ status, labels, fallback }: { status: string | null; labels: Record<string, string>; fallback: string }) {
  const review = status && status !== "valid";
  return <span className={`inline-flex max-w-full break-words rounded-full px-2.5 py-1 text-center text-[0.7rem] font-bold leading-4 ${review ? "bg-amber-100 text-amber-900" : "bg-emerald/10 text-emerald"}`}>{labels[status || ""] || fallback}</span>;
}

function Leaderboard({ leaders, title, eyebrow, locale, language }: { leaders: SimpleAnalysisLeader[]; title: string; eyebrow: string; locale: ReturnType<typeof useI18n>["locale"]; language: "en" | "fr" }) {
  return (
    <Panel title={title} eyebrow={eyebrow}>
      {leaders.length === 0 && <p className="py-8 text-sm text-slate-500">{locale.simpleAnalysis.emptyLeaders}</p>}
      {leaders.length > 0 && <table className="w-full table-fixed border-collapse text-left text-[0.72rem] sm:text-sm"><colgroup><col className="w-[7%]" /><col className="w-[39%]" /><col className="w-[10%]" /><col className="w-[20%]" /><col className="w-[24%]" /></colgroup><thead><tr className="border-b border-slate-100 text-[0.62rem] uppercase tracking-[0.1em] text-slate-400 sm:text-xs"><th className="pb-3 pr-2">#</th><th className="pb-3 pr-2">{locale.search.resultEyebrow}</th><th className="pb-3 pr-2">{locale.simpleAnalysis.age}</th><th className="pb-3 pr-2">{locale.simpleAnalysis.dateOfBirth}</th><th className="pb-3">{locale.simpleAnalysis.quality}</th></tr></thead><tbody>{leaders.map((leader, index) => <tr key={`${leader.declarationUuid}-${index}`} className="border-b border-slate-100 last:border-0"><td className="py-3 pr-2 align-top font-mono text-xs text-slate-400">{index + 1}</td><td className="py-3 pr-2 align-top"><p className="break-words font-bold text-ink">{displayName(leader, locale.search.unknownDeclarant)}</p><p className="mt-1 break-words text-xs text-slate-500">{leader.mandate || leader.organ || locale.search.notAvailable}</p></td><td className="py-3 pr-2 align-top font-bold whitespace-nowrap text-ink">{formatNumber(leader.ageYears, language)}</td><td className="py-3 pr-2 align-top break-words text-slate-600">{displayDate(leader.dateOfBirth, language, locale.search.notAvailable)}</td><td className="py-3 align-top"><QualityBadge status={leader.qualityStatus} labels={locale.simpleAnalysis.qualityLabels} fallback={locale.search.notAvailable} /></td></tr>)}</tbody></table>}
    </Panel>
  );
}

type SalaryBin = SimpleAnalysisResponse["ageBins"][number];

function SalaryChart({ bins, language, locale }: { bins: SalaryBin[]; language: "en" | "fr"; locale: ReturnType<typeof useI18n>["locale"] }) {
  return <div role="img" aria-label={locale.simpleAnalysis.chartLabel} className="h-[26rem] min-w-0"><ResponsiveContainer width="100%" height="100%"><BarChart data={bins} margin={{ top: 8, right: 16, bottom: 8, left: 8 }}><CartesianGrid vertical={false} stroke="#e2e8f0" strokeDasharray="4 4" /><XAxis dataKey="label" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} /><YAxis tickFormatter={(value) => formatCurrency(Number(value), language)} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} width={72} /><Tooltip formatter={(value) => formatCurrency(Number(value), language)} /><Legend /><Bar dataKey="averageSalary" name={locale.simpleAnalysis.average} fill="#1f9d75" radius={[8, 8, 0, 0]} /><Bar dataKey="medianSalary" name={locale.simpleAnalysis.median} fill="#8ed7e8" radius={[8, 8, 0, 0]} /></BarChart></ResponsiveContainer></div>;
}

export function SimpleAnalysisPage() {
  const { language, locale } = useI18n();
  const [excludeZeroSalary, setExcludeZeroSalary] = useState(true);
  const analysis = useResource(fetchSimpleAnalysis);
  const data = analysis.data;
  const salaryBins = !data
    ? []
    : excludeZeroSalary
      ? data.ageBins
      : data.ageBinsIncludingZero.length > 0
        ? data.ageBinsIncludingZero
        : data.ageBins;
  return (
    <div className="mx-auto max-w-7xl px-5 py-10 lg:px-8 lg:py-14">
      <section className="hero-grid overflow-hidden rounded-[2rem] bg-ink px-6 py-9 text-white shadow-soft sm:px-10 sm:py-11"><p className="relative z-10 text-xs font-bold uppercase tracking-[0.18em] text-lime">{locale.simpleAnalysis.eyebrow}</p><h1 className="relative z-10 mt-4 max-w-3xl text-4xl font-black leading-[1.04] tracking-[-0.04em] sm:text-5xl">{locale.simpleAnalysis.title}</h1><p className="relative z-10 mt-5 max-w-3xl text-base leading-7 text-slate-300">{locale.simpleAnalysis.description}</p>{data && <p className="relative z-10 mt-6 text-xs font-semibold uppercase tracking-[0.12em] text-lime">{locale.simpleAnalysis.reference}: {displayDate(data.referenceDate, language, locale.search.notAvailable)}</p>}</section>
      {analysis.loading && <div className="mt-8 space-y-6"><ChartSkeleton /><ChartSkeleton /></div>}
      {analysis.error && <div className="mt-8"><SliceError onRetry={analysis.reload} /></div>}
      {data && <>
        <section className="mt-8 grid gap-6 lg:grid-cols-2"><Leaderboard leaders={data.youngest} title={locale.simpleAnalysis.youngestTitle} eyebrow={locale.simpleAnalysis.youngestEyebrow} locale={locale} language={language} /><Leaderboard leaders={data.oldest} title={locale.simpleAnalysis.oldestTitle} eyebrow={locale.simpleAnalysis.oldestEyebrow} locale={locale} language={language} /></section>
        <Panel title={locale.simpleAnalysis.salaryTitle} eyebrow={locale.simpleAnalysis.salaryEyebrow}>
          <div className="mb-6 flex flex-wrap items-start justify-between gap-4"><p className="max-w-3xl text-sm leading-6 text-slate-500">{locale.simpleAnalysis.salaryDescription}</p><label className="inline-flex shrink-0 cursor-pointer items-center gap-2 rounded-full border border-slate-200 bg-canvas px-3 py-2 text-xs font-bold text-ink"><input type="checkbox" checked={excludeZeroSalary} onChange={(event) => setExcludeZeroSalary(event.target.checked)} className="size-4 accent-emerald" />{locale.simpleAnalysis.excludeZeroSalary}</label></div>
          {salaryBins.length === 0 && <p className="py-8 text-sm text-slate-500">{locale.simpleAnalysis.emptySalary}</p>}
          {salaryBins.length > 0 && <SalaryChart bins={salaryBins} language={language} locale={locale} />}
          {salaryBins.length > 0 && <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">{salaryBins.map((bin) => <div key={bin.label} className="rounded-2xl bg-canvas p-4"><p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{bin.label}</p><p className="mt-2 text-sm font-bold text-ink">{formatCurrency(bin.averageSalary, language)} / {formatCurrency(bin.medianSalary, language)}</p><p className="mt-1 text-xs text-slate-500">{formatNumber(bin.rows, language)} {locale.simpleAnalysis.rows}</p></div>)}</div>}
          <p className="mt-6 border-t border-slate-100 pt-4 text-xs leading-5 text-slate-500">{locale.simpleAnalysis.anomalyNote}</p>
        </Panel>
        <div className="mt-6"><Panel title={locale.simpleAnalysis.zeroSalaryTitle} eyebrow={locale.simpleAnalysis.zeroSalaryEyebrow}>
          <p className="mb-6 max-w-3xl text-sm leading-6 text-slate-500">{locale.simpleAnalysis.zeroSalaryDescription}</p>
          {data.zeroSalaryBins.length === 0 && <p className="py-8 text-sm text-slate-500">{locale.simpleAnalysis.emptyZeroSalary}</p>}
          {data.zeroSalaryBins.length > 0 && <div role="img" aria-label={locale.simpleAnalysis.zeroSalaryChartLabel} className="h-[22rem] min-w-0"><ResponsiveContainer width="100%" height="100%"><BarChart data={data.zeroSalaryBins} margin={{ top: 8, right: 16, bottom: 8, left: 8 }}><CartesianGrid vertical={false} stroke="#e2e8f0" strokeDasharray="4 4" /><XAxis dataKey="label" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} /><YAxis allowDecimals={false} tickFormatter={(value) => formatNumber(Number(value), language)} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} width={56} /><Tooltip formatter={(value) => formatNumber(Number(value), language)} /><Bar dataKey="rows" name={locale.simpleAnalysis.zeroSalaryCount} fill="#b8a5e8" radius={[8, 8, 0, 0]} /></BarChart></ResponsiveContainer></div>}
        </Panel></div>
      </>}
    </div>
  );
}
