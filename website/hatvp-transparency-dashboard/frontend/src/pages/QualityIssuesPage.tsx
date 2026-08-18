import issues from "../data/qualityIssues.json";
import { useI18n } from "../context/I18nContext";

type QualityIssue = (typeof issues)[number];

function formatDate(value: string, language: string): string {
  return new Intl.DateTimeFormat(language === "fr" ? "fr-FR" : "en-GB", {
    dateStyle: "medium",
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
}

function formatOpenDuration(value: string, language: string, dayLabel: string): string {
  const start = Date.parse(`${value}T00:00:00Z`);
  const now = new Date();
  const today = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate());
  const days = Math.max(0, Math.floor((today - start) / 86_400_000));
  return `${new Intl.NumberFormat(language === "fr" ? "fr-FR" : "en-GB").format(days)} ${dayLabel}`;
}

function IssueLinks({ links, label, noLink }: { links: string[]; label: string; noLink: string }) {
  if (!links.length) return <span className="text-slate-400">{noLink}</span>;
  return <div className="flex flex-col items-start gap-2">{links.map((link, index) => <a key={link} className="text-sm font-bold text-emerald underline decoration-lime underline-offset-4 hover:text-ink" href={link} target="_blank" rel="noreferrer">{label} {links.length > 1 ? index + 1 : "↗"}</a>)}</div>;
}

function StatusBadge({ solved, label }: { solved: boolean; label: string }) {
  return <span className={`inline-flex rounded-full px-3 py-1 text-xs font-bold ${solved ? "bg-emerald/10 text-emerald" : "bg-amber-100 text-amber-900"}`}>{label}</span>;
}

export function QualityIssuesPage() {
  const { language, locale } = useI18n();
  const solvedCount = issues.filter((issue) => issue.solved).length;
  const openCount = issues.length - solvedCount;
  const duration = (issue: QualityIssue) => formatOpenDuration(issue.contactDate, language, locale.qualityIssues.days);

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
      <div className="overflow-x-auto"><table className="w-full min-w-[850px] border-collapse text-left"><thead className="bg-slate-50/80"><tr>{[locale.qualityIssues.columns.issueType, locale.qualityIssues.columns.contactDate, locale.qualityIssues.columns.declaration, locale.qualityIssues.columns.status, locale.qualityIssues.columns.duration].map((heading) => <th key={heading} className="px-5 py-4 text-xs font-bold uppercase tracking-[0.12em] text-slate-500 sm:px-6">{heading}</th>)}</tr></thead><tbody className="divide-y divide-slate-200/80">{issues.map((issue) => <tr key={`${issue.contactDate}-${issue.issueType}-${issue.declarationLinks.join("-")}`} className="align-top transition hover:bg-slate-50/70"><td className="px-5 py-5 text-sm font-bold text-ink sm:px-6">{issue.issueType}</td><td className="whitespace-nowrap px-5 py-5 text-sm text-slate-600 sm:px-6">{formatDate(issue.contactDate, language)}</td><td className="px-5 py-5 sm:px-6"><IssueLinks links={issue.declarationLinks} label={locale.qualityIssues.openLink} noLink={locale.qualityIssues.noLink} /></td><td className="px-5 py-5 sm:px-6"><StatusBadge solved={issue.solved} label={issue.solved ? locale.qualityIssues.solvedLabel : locale.qualityIssues.notSolved} /></td><td className="whitespace-nowrap px-5 py-5 text-sm font-semibold text-slate-600 sm:px-6">{duration(issue)}</td></tr>)}</tbody></table></div>
    </section>
  </div>;
}
