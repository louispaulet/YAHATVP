import { formatDateTime } from "../formatters";
import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import type { Language } from "../config/i18n";
import { useI18n } from "../context/I18nContext";
import type { DashboardOverviewResponse } from "../types";
import { Disclosure } from "./Disclosure";
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
      <Disclosure summary={locale.homepage.evidence.readSnapshot}>
        <p>{locale.homepage.evidence.readSnapshotDescription}</p>
      </Disclosure>
      <p>{locale.panels.snapshotMeaning.counts}</p>
      <p>{locale.panels.snapshotMeaning.amounts}</p>
      <div className="rounded-2xl bg-lime/30 p-4 font-semibold text-ink">
        {locale.panels.snapshotMeaning.lastGenerated}: {loading ? <LoadingShell className="inline-block h-4 w-32 rounded-full align-middle" /> : overview ? formatDateTime(overview.generatedAt, language) : locale.hero.notAvailable}
      </div>
      <Link className="inline-flex min-h-10 items-center gap-1 font-bold text-emerald underline decoration-lime underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald" to="/about">{locale.homepage.evidence.coverageLink}<ArrowRight size={14} strokeWidth={2} aria-hidden="true" /></Link>
    </div>
  );
}
