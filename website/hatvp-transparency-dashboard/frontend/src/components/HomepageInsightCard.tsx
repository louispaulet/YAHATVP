import type { ReactNode } from "react";

type InsightTone = "emerald" | "coral" | "sky";

const toneClasses: Record<InsightTone, { marker: string; border: string; label: string }> = {
  emerald: { marker: "bg-emerald", border: "border-emerald/20", label: "text-emerald" },
  coral: { marker: "bg-[#d96c86]", border: "border-[#d96c86]/25", label: "text-[#b24b67]" },
  sky: { marker: "bg-sky", border: "border-sky/35", label: "text-[#3e8191]" },
};

interface HomepageInsightCardProps {
  number: string;
  eyebrow: string;
  title: string;
  description: string;
  tone: InsightTone;
  children: ReactNode;
}

export function HomepageInsightCard({ number, eyebrow, title, description, tone, children }: HomepageInsightCardProps) {
  const classes = toneClasses[tone];
  return (
    <article className={`flex h-full min-w-0 flex-col rounded-[1.5rem] border bg-white p-5 shadow-card sm:p-6 ${classes.border}`}>
      <div className="flex items-start justify-between gap-4">
        <span className={`flex size-9 shrink-0 items-center justify-center rounded-xl text-sm font-black text-ink ${classes.marker}`}>{number}</span>
        <p className={`pt-1 text-right text-[10px] font-bold uppercase tracking-[0.16em] ${classes.label}`}>{eyebrow}</p>
      </div>
      <h3 className="mt-5 text-xl font-bold leading-tight tracking-tight text-ink">{title}</h3>
      <p className="mt-3 text-sm leading-6 text-slate-500">{description}</p>
      <div className="mt-6 flex-1">{children}</div>
    </article>
  );
}
