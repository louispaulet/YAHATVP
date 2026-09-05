import type { ReactNode } from "react";

interface PanelProps {
  title: string;
  eyebrow: string;
  description?: string;
  children: ReactNode;
  className?: string;
  id?: string;
  labelledBy?: string;
  metadata?: ReactNode;
  disclosureAction?: ReactNode;
}

export function Panel({ title, eyebrow, description, children, className, id, labelledBy, metadata, disclosureAction }: PanelProps) {
  return (
    <section id={id} aria-labelledby={labelledBy} className={`dashboard-card min-w-0 p-6 sm:p-8${className ? ` ${className}` : ""}`}>
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{eyebrow}</p>
      <div className="mt-2 flex flex-wrap items-start justify-between gap-3">
        <h2 id={labelledBy} className="text-xl font-bold tracking-tight text-ink">{title}</h2>
        {disclosureAction}
      </div>
      {description && <p className="mt-3 text-sm leading-6 text-slate-500">{description}</p>}
      {metadata && <div className="mt-4 border-y border-slate-100 py-3 text-xs font-semibold text-slate-500">{metadata}</div>}
      <div className={description ? "mt-5" : "mt-7"}>{children}</div>
    </section>
  );
}
