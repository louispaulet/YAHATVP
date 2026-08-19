import type { ReactNode } from "react";

interface PanelProps {
  title: string;
  eyebrow: string;
  children: ReactNode;
}

export function Panel({ title, eyebrow, children }: PanelProps) {
  return (
    <section className="dashboard-card p-6 sm:p-8">
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{eyebrow}</p>
      <h2 className="mt-2 text-xl font-bold tracking-tight text-ink">{title}</h2>
      <div className="mt-7">{children}</div>
    </section>
  );
}
