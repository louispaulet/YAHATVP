import { useEffect, useState } from "react";
import { fetchHealth } from "../api";
import { ChartSkeleton, SliceError } from "../components/Feedback";
import { useI18n } from "../context/I18nContext";
import { useResource } from "../hooks/useResource";
import type { Locale } from "../config/i18n";
import type { DashboardHealthResponse } from "../types";

function countdown(target: string | null, now: number, labels: Record<string, string>): string {
  if (!target) return labels.unavailable;
  const seconds = Math.max(0, Math.floor((new Date(target).getTime() - now) / 1000));
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remaining = seconds % 60;
  return `${days}${labels.days} ${String(hours).padStart(2, "0")}h ${String(minutes).padStart(2, "0")}m ${String(remaining).padStart(2, "0")}s`;
}

function sourceName(sourceId: string, locale: Locale): string {
  return locale.pipelineHealth.sourceNames[sourceId as "hatvp_website" | "wayback_github"] ?? sourceId;
}

function layerName(layer: string, locale: Locale): string {
  return locale.pipelineHealth.layers[layer as "bronze" | "silver" | "gold"] ?? layer;
}

export function PipelineHealthPage() {
  const { language, locale } = useI18n();
  const health = useResource<DashboardHealthResponse>(fetchHealth);
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, []);
  const data = health.data;
  const number = new Intl.NumberFormat(language === "fr" ? "fr-FR" : "en-GB");
  return <div className="mx-auto max-w-7xl space-y-8 px-5 py-8 lg:px-8 lg:py-12">
    <section className="hero-grid overflow-hidden rounded-[2rem] bg-ink px-6 py-10 text-white shadow-soft sm:px-10 sm:py-14">
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-lime">{locale.pipelineHealth.eyebrow}</p>
      <h1 className="mt-5 max-w-4xl text-4xl font-black leading-[1.02] tracking-[-0.05em] sm:text-6xl">{locale.pipelineHealth.title}</h1>
      <p className="mt-5 max-w-3xl text-base leading-7 text-slate-300">{locale.pipelineHealth.description}</p>
      <div className="mt-8 flex flex-wrap gap-3 text-xs font-bold"><span className="rounded-full bg-white/10 px-4 py-2">{locale.pipelineHealth.snapshot} {data?.snapshotDate ?? locale.hero.notAvailable}</span><span className="rounded-full bg-lime px-4 py-2 text-ink">{locale.pipelineHealth.weekly}</span></div>
    </section>
    {health.loading && <div className="grid gap-4 md:grid-cols-3"><ChartSkeleton /><ChartSkeleton /><ChartSkeleton /></div>}
    {health.error && <SliceError onRetry={health.reload} />}
    {data && <>
      <section className="grid gap-4 md:grid-cols-3">
        <div className="dashboard-card bg-emerald p-6 text-white md:col-span-2"><p className="text-xs font-bold uppercase tracking-[0.15em] text-white/70">{locale.pipelineHealth.nextIngestion}</p><p className="mt-3 text-4xl font-black tabular-nums sm:text-5xl">{countdown(data.nextIngestionAt, now, locale.pipelineHealth.countdown)}</p><p className="mt-3 text-sm text-white/80">{new Intl.DateTimeFormat(language === "fr" ? "fr-FR" : "en-GB", { dateStyle: "full", timeStyle: "short" }).format(new Date(data.nextIngestionAt))}</p></div>
        <div className="dashboard-card p-6"><p className="text-xs font-bold uppercase tracking-[0.15em] text-slate-400">{locale.pipelineHealth.flagged}</p><p className="mt-3 text-4xl font-black text-amber-700">{number.format(data.quality.flaggedRecords)}</p><p className="mt-2 text-sm leading-6 text-slate-500">{locale.pipelineHealth.flaggedDetail}</p></div>
      </section>
      <section className="grid gap-6 lg:grid-cols-2">
        <div className="dashboard-card p-6"><p className="text-xs font-bold uppercase tracking-[0.15em] text-emerald">{locale.pipelineHealth.sourcesEyebrow}</p><h2 className="mt-2 text-2xl font-black">{locale.pipelineHealth.sourcesTitle}</h2><div className="mt-5 divide-y divide-slate-200/80">{data.sources.map((source) => <div className="flex items-center justify-between gap-4 py-4" key={source.sourceId}><span className="text-sm font-semibold text-slate-700">{sourceName(source.sourceId, locale)}</span><span className="text-2xl font-black text-ink">{number.format(source.declarations)}</span></div>)}</div></div>
        <div className="dashboard-card p-6"><p className="text-xs font-bold uppercase tracking-[0.15em] text-emerald">{locale.pipelineHealth.qualityEyebrow}</p><h2 className="mt-2 text-2xl font-black">{locale.pipelineHealth.qualityTitle}</h2><div className="mt-5 space-y-4">{data.layers.map((layer) => <div key={layer.layer}><div className="flex justify-between gap-3 text-sm font-bold"><span>{layerName(layer.layer, locale)}</span><span>{number.format(layer.rows)} {locale.pipelineHealth.rows}</span></div><div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-emerald" style={{ width: `${Math.min(100, Math.max(2, (layer.rows / Math.max(...data.layers.map((item) => item.rows), 1)) * 100))}%` }} /></div><p className="mt-1 text-xs text-slate-500">{number.format(layer.reviewRows)} {locale.pipelineHealth.reviewRows}</p></div>)}</div></div>
      </section>
      <section className="dashboard-card p-6"><div className="flex flex-wrap items-end justify-between gap-3"><div><p className="text-xs font-bold uppercase tracking-[0.15em] text-emerald">{locale.pipelineHealth.anomalyEyebrow}</p><h2 className="mt-2 text-2xl font-black">{locale.pipelineHealth.anomalyTitle}</h2></div><p className="text-sm text-slate-500">{locale.pipelineHealth.qualitySummary.replace("{errors}", number.format(data.quality.errors)).replace("{warnings}", number.format(data.quality.warnings))}</p></div><div className="mt-5 flex flex-wrap gap-3">{data.anomalies.map((anomaly) => <span className="rounded-full bg-slate-100 px-4 py-2 text-sm font-bold text-slate-700" key={anomaly.status}>{anomaly.status}: {number.format(anomaly.rows)}</span>)}</div></section>
    </>}
  </div>;
}
