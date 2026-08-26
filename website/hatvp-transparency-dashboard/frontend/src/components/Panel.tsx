import type { ReactNode } from "react";

interface PanelProps {
  title: string;
  eyebrow: string;
  description?: string;
  children: ReactNode;
}

export function Panel({ title, eyebrow, description, children }: PanelProps) {
  return (
    <section className="dashboard-card min-w-0 p-6 sm:p-8">
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{eyebrow}</p>
      <h2 className="mt-2 text-xl font-bold tracking-tight text-ink">{title}</h2>
      {description && <p className="mt-3 text-sm leading-6 text-slate-500">{description}</p>}
      <div className={description ? "mt-5" : "mt-7"}>{children}</div>
    </section>
  );
}
