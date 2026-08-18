import { formatDateTime } from "../formatters";
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
      <p>{locale.panels.snapshotMeaning.counts}</p>
      <p>{locale.panels.snapshotMeaning.amounts}</p>
      <p className="rounded-2xl bg-lime/30 p-4 font-semibold text-ink">
        {locale.panels.snapshotMeaning.lastGenerated}: {loading ? <LoadingShell className="inline-block h-4 w-32 rounded-full align-middle" /> : overview ? formatDateTime(overview.generatedAt, language) : locale.hero.notAvailable}
      </p>
    </div>
  );
}
