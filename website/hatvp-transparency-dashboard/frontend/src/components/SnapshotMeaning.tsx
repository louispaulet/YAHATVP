import { formatDateTime } from "../formatters";
import { Link } from "react-router-dom";
import type { Language } from "../config/i18n";
import { useI18n } from "../context/I18nContext";
import type { DashboardOverviewResponse } from "../types";
import { LoadingShell } from "./Feedback";

interface SnapshotMeaningProps {
  overview: DashboardOverviewResponse | null;
  loading: boolean;
  language: Language;
}

export function SnapshotMeaning({ overview, loading, language }: SnapshotMeaningProps) {
  const { locale } = useI18n();
  return (
    <div className="space-y-4 text-sm leading-6 text-slate-600">
      <details className="rounded-2xl bg-surface-subtle px-4 py-3">
        <summary className="cursor-pointer font-bold text-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald">{locale.homepage.evidence.readSnapshot}</summary>
        <p className="mt-2">{locale.homepage.evidence.readSnapshotDescription}</p>
      </details>
      <p>{locale.panels.snapshotMeaning.counts}</p>
      <p>{locale.panels.snapshotMeaning.amounts}</p>
      <div className="rounded-2xl bg-lime/30 p-4 font-semibold text-ink">
        {locale.panels.snapshotMeaning.lastGenerated}: {loading ? <LoadingShell className="inline-block h-4 w-32 rounded-full align-middle" /> : overview ? formatDateTime(overview.generatedAt, language) : locale.hero.notAvailable}
      </div>
      <Link className="inline-flex font-bold text-emerald underline decoration-lime underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald" to="/about">{locale.homepage.evidence.coverageLink} →</Link>
    </div>
  );
}
