import issues from "../data/qualityIssues.json";
import { useI18n } from "../context/I18nContext";
import { ExternalLink } from "lucide-react";

type QualityIssue = (typeof issues)[number];

function formatDate(value: string, language: string): string {
  return new Intl.DateTimeFormat(language === "fr" ? "fr-FR" : "en-GB", {
    dateStyle: "medium",
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
}

type DurationUnits = {
  year: string;
  years: string;
  month: string;
  months: string;
  day: string;
  days: string;
};

function daysInMonth(year: number, month: number): number {
  return new Date(Date.UTC(year, month + 1, 0)).getUTCDate();
}

function addCalendarYears(date: Date, years: number): Date {
  const year = date.getUTCFullYear() + years;
  const month = date.getUTCMonth();
  return new Date(Date.UTC(year, month, Math.min(date.getUTCDate(), daysInMonth(year, month))));
}

function addCalendarMonths(date: Date, months: number): Date {
  const absoluteMonth = date.getUTCFullYear() * 12 + date.getUTCMonth() + months;
  const year = Math.floor(absoluteMonth / 12);
  const month = absoluteMonth % 12;
  return new Date(Date.UTC(year, month, Math.min(date.getUTCDate(), daysInMonth(year, month))));
}

function currentMadridDate(): Date {
  const parts = Object.fromEntries(new Intl.DateTimeFormat("en", {
    timeZone: "Europe/Madrid",
    year: "numeric",
    month: "numeric",
    day: "numeric",
  }).formatToParts(new Date()).map(({ type, value }) => [type, value]));
  return new Date(Date.UTC(Number(parts.year), Number(parts.month) - 1, Number(parts.day)));
}

function formatOpenDuration(value: string, language: string, units: DurationUnits): string {
  const start = new Date(`${value}T00:00:00Z`);
  const end = currentMadridDate();
  if (end <= start) return `0 ${units.days}`;
  const number = new Intl.NumberFormat(language === "fr" ? "fr-FR" : "en-GB");
  let years = end.getUTCFullYear() - start.getUTCFullYear();
  let cursor = addCalendarYears(start, years);
  if (cursor > end) cursor = addCalendarYears(start, --years);
  let months = (end.getUTCFullYear() - cursor.getUTCFullYear()) * 12 + end.getUTCMonth() - cursor.getUTCMonth();
  let monthCursor = addCalendarMonths(cursor, months);
  if (monthCursor > end) monthCursor = addCalendarMonths(cursor, --months);
  const days = Math.floor((end.getTime() - monthCursor.getTime()) / 86_400_000);
  const parts = years ? [`${number.format(years)} ${years === 1 ? units.year : units.years}`] : [];
  if (months) parts.push(`${number.format(months)} ${months === 1 ? units.month : units.months}`);
  if (days || !parts.length) parts.push(`${number.format(days)} ${days === 1 ? units.day : units.days}`);
  return parts.join(", ");
}

function IssueLinks({ links, label, noLink }: { links: string[]; label: string; noLink: string }) {
  if (!links.length) return <span className="text-slate-400">{noLink}</span>;
  return <div className="flex flex-col items-start gap-2">{links.map((link, index) => <a key={link} className="inline-flex min-h-10 items-center gap-1 text-sm font-bold text-emerald underline decoration-lime underline-offset-4 hover:text-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald" href={link} target="_blank" rel="noreferrer">{label} {links.length > 1 ? index + 1 : <ExternalLink size={13} strokeWidth={2} aria-hidden="true" />}</a>)}</div>;
}

function StatusBadge({ solved, label }: { solved: boolean; label: string }) {
  return <span className={`inline-flex rounded-full px-3 py-1 text-xs font-bold ${solved ? "bg-emerald/10 text-emerald" : "bg-amber-100 text-amber-900"}`}>{label}</span>;
}

export function QualityIssuesPage() {
  const { language, locale } = useI18n();
  const solvedCount = issues.filter((issue) => issue.solved).length;
  const openCount = issues.length - solvedCount;
  const duration = (issue: QualityIssue) => formatOpenDuration(issue.contactDate, language, locale.qualityIssues.durationUnits);

  return <div className="mx-auto max-w-7xl px-5 py-12 lg:px-8 lg:py-16">
    <section className="hero-grid overflow-hidden rounded-[2rem] bg-ink px-6 py-9 text-white shadow-soft sm:px-10 sm:py-11">
      <p className="relative z-10 text-xs font-bold uppercase tracking-[0.18em] text-lime">{locale.qualityIssues.eyebrow}</p>
      <h1 className="relative z-10 mt-4 max-w-4xl text-4xl font-black leading-[1.04] tracking-[-0.04em] sm:text-5xl">{locale.qualityIssues.title}</h1>
      <p className="relative z-10 mt-5 max-w-3xl text-base leading-7 text-slate-300">{locale.qualityIssues.description}</p>
    </section>
    <div className="relative z-10 -mt-5 grid gap-4 sm:grid-cols-3">
      <div className="dashboard-card p-5"><p className="text-xs font-bold uppercase tracking-[0.14em] text-slate-400">{locale.qualityIssues.reported}</p><p className="mt-2 text-3xl font-black">{issues.length}</p></div>
      <div className="dashboard-card p-5"><p className="text-xs font-bold uppercase tracking-[0.14em] text-slate-400">{locale.qualityIssues.solved}</p><p className="mt-2 text-3xl font-black text-emerald">{solvedCount}</p></div>
      <div className="dashboard-card p-5"><p className="text-xs font-bold uppercase tracking-[0.14em] text-slate-400">{locale.qualityIssues.open}</p><p className="mt-2 text-3xl font-black text-amber-700">{openCount}</p></div>
    </div>
    <section className="dashboard-card mt-8 overflow-hidden">
      <div className="border-b border-slate-200/80 px-5 py-5 sm:px-6"><p className="text-sm leading-6 text-slate-600">{locale.qualityIssues.privacyNote}</p></div>
      <div className="overflow-x-auto"><table className="quality-table w-full border-collapse text-left"><thead className="bg-slate-50/80"><tr>{[locale.qualityIssues.columns.issueType, locale.qualityIssues.columns.contactDate, locale.qualityIssues.columns.declaration, locale.qualityIssues.columns.status, locale.qualityIssues.columns.duration].map((heading) => <th key={heading} className="sticky top-0 px-5 py-4 text-xs font-bold uppercase tracking-[0.12em] text-slate-500 sm:px-6">{heading}</th>)}</tr></thead><tbody className="divide-y divide-slate-200/80">{issues.map((issue) => <tr key={`${issue.contactDate}-${issue.issueType}-${issue.declarationLinks.join("-")}`} className="align-top transition hover:bg-slate-50/70"><td data-label={locale.qualityIssues.columns.issueType} className="px-5 py-5 text-sm font-bold text-ink sm:px-6">{issue.issueType}</td><td data-label={locale.qualityIssues.columns.contactDate} className="whitespace-nowrap px-5 py-5 text-sm text-slate-600 sm:px-6">{formatDate(issue.contactDate, language)}</td><td data-label={locale.qualityIssues.columns.declaration} className="px-5 py-5 sm:px-6"><IssueLinks links={issue.declarationLinks} label={locale.qualityIssues.openLink} noLink={locale.qualityIssues.noLink} /></td><td data-label={locale.qualityIssues.columns.status} className="px-5 py-5 sm:px-6"><StatusBadge solved={issue.solved} label={issue.solved ? locale.qualityIssues.solvedLabel : locale.qualityIssues.notSolved} /></td><td data-label={locale.qualityIssues.columns.duration} className="whitespace-nowrap px-5 py-5 text-sm font-semibold text-slate-600 sm:px-6">{duration(issue)}</td></tr>)}</tbody></table></div>
    </section>
  </div>;
}
