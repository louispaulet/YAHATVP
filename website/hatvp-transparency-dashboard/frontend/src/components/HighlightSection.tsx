import type { ReactNode } from "react";

export function HighlightSection({ eyebrow, title, description, children }: {
  eyebrow: string;
  title: string;
  description: string;
  children: ReactNode;
}) {
  return (
    <section className="border-t border-slate-200 pt-10 sm:pt-14">
      <div className="grid gap-4 lg:grid-cols-[0.78fr_1.22fr] lg:gap-12">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{eyebrow}</p>
          <h2 className="mt-3 text-3xl font-black tracking-[-0.035em] sm:text-4xl">{title}</h2>
        </div>
        <p className="max-w-2xl text-sm leading-7 text-slate-600 lg:pt-7">{description}</p>
      </div>
      <div className="mt-7 grid gap-4 md:grid-cols-2 xl:grid-cols-4">{children}</div>
    </section>
  );
}
