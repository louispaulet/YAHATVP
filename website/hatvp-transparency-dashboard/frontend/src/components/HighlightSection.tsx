import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

export type HighlightTone = "income" | "asset" | "amended";

export function HighlightSection({ tone, icon: Icon, eyebrow, title, description, children }: {
  tone: HighlightTone;
  icon: LucideIcon;
  eyebrow: string;
  title: string;
  description: string;
  children: ReactNode;
}) {
  return (
    <section className={`explore-section explore-section--${tone} border-t border-slate-200 pt-10 sm:pt-14`}>
      <div className="grid gap-4 lg:grid-cols-[0.78fr_1.22fr] lg:gap-12">
        <div>
          <div className="flex items-start gap-3">
            <span className={`explore-section-mark explore-section-mark--${tone}`}><Icon size={18} strokeWidth={1.8} aria-hidden="true" /></span>
            <div>
              <p className="explore-section-eyebrow text-xs font-bold uppercase tracking-[0.16em]">{eyebrow}</p>
              <h2 className="mt-3 text-3xl font-black leading-[1.08] tracking-[-0.035em] sm:text-4xl">{title}</h2>
            </div>
          </div>
        </div>
        <p className="max-w-2xl text-[0.9375rem] leading-7 text-slate-600 lg:pt-7">{description}</p>
      </div>
      <div className="explore-section-rule" aria-hidden="true"><span className={`explore-section-rule__accent explore-section-rule__accent--${tone}`} /></div>
      <div className="explore-card-grid">{children}</div>
    </section>
  );
}
