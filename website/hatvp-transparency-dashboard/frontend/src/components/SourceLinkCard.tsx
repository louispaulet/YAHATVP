import type { Locale } from "../config/i18n";
import { Download, ExternalLink } from "lucide-react";

type SourceLink = Locale["about"]["sources"]["links"][number];

export function SourceLinkCard({ link }: { link: SourceLink }) {
  const isDownload = link.kind === "download";
  const ActionIcon = isDownload ? Download : ExternalLink;
  const cardClass = isDownload ? "hover:border-emerald/40 hover:shadow-soft" : "hover:border-slate-300 hover:shadow-soft";
  const badgeClass = isDownload ? "bg-lime/60 text-ink" : "bg-slate-100 text-slate-500";
  const iconClass = isDownload ? "bg-emerald text-white" : "bg-slate-100 text-slate-600";

  return (
    <a
      className={`dashboard-card source-link-card group flex h-full flex-col p-5 transition hover:-translate-y-0.5 ${cardClass}`}
      href={link.href}
      target={isDownload ? undefined : "_blank"}
      rel={isDownload ? undefined : "noreferrer"}
      download={isDownload ? "" : undefined}
    >
      <span className="source-link-header">
        <span className="min-w-0 break-words text-sm font-bold text-ink">{link.label}</span>
        <span className={`max-w-full shrink-0 rounded-full px-2.5 py-1 text-center text-[0.65rem] font-bold uppercase leading-5 tracking-[0.12em] ${badgeClass}`}>{link.type}</span>
      </span>
      <span className="mt-3 block text-sm leading-6 text-slate-500">{link.description}</span>
      <span className="mt-auto flex items-center gap-2 border-t border-slate-100 pt-5 text-xs font-bold uppercase tracking-[0.12em] text-slate-700">
        <span aria-hidden="true" className={`inline-flex size-7 items-center justify-center rounded-full ${iconClass}`}><ActionIcon size={14} strokeWidth={2} /></span>
        {link.action}
      </span>
    </a>
  );
}
