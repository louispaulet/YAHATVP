import type { Language } from "../config/i18n";

interface SnapshotContextProps {
  snapshotDate: string | null | undefined;
  generatedAt?: string | null;
  language: Language;
  sourceScope?: string;
  labels: { snapshot: string; generated: string };
  className?: string;
}

function formatDate(value: string | null | undefined, language: Language): string | null {
  if (!value) return null;
  const parsed = new Date(value.includes("T") ? value : `${value}T00:00:00`);
  if (Number.isNaN(parsed.getTime())) return null;
  return new Intl.DateTimeFormat(language === "fr" ? "fr-FR" : "en-GB", { dateStyle: "medium" }).format(parsed);
}

function formatDateTime(value: string | null | undefined, language: Language): string | null {
  if (!value) return null;
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return null;
  return new Intl.DateTimeFormat(language === "fr" ? "fr-FR" : "en-GB", { dateStyle: "medium", timeStyle: "short" }).format(parsed);
}

export function SnapshotContext({ snapshotDate, generatedAt, language, sourceScope, labels, className = "" }: SnapshotContextProps) {
  const snapshot = formatDate(snapshotDate, language);
  const generated = formatDateTime(generatedAt, language);
  if (!snapshot && !generated && !sourceScope) return null;
  return (
    <div className={`flex flex-wrap items-center gap-x-4 gap-y-2 text-xs font-semibold text-slate-500 ${className}`} aria-label={sourceScope}>
      {snapshot && <span><span className="font-bold text-slate-400">{labels.snapshot}</span> {snapshot}</span>}
      {generated && <span><span className="font-bold text-slate-400">{labels.generated}</span> {generated}</span>}
      {sourceScope && <span className="text-emerald">{sourceScope}</span>}
    </div>
  );
}
