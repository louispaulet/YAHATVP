import { useI18n } from "../context/I18nContext";

export function ExplorePage() {
  const { locale } = useI18n();
  return (
    <div className="mx-auto max-w-3xl px-5 py-16 lg:px-8 lg:py-24">
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.explore.eyebrow}</p>
      <h1 className="mt-4 text-4xl font-black tracking-tight sm:text-5xl">{locale.explore.title}</h1>
      <p className="mt-8 max-w-2xl text-base leading-8 text-slate-600">{locale.explore.description}</p>
      <div className="dashboard-card mt-10 border-dashed p-6 sm:p-8"><p className="text-sm font-bold uppercase tracking-[0.14em] text-slate-400">{locale.explore.status}</p><p className="mt-3 text-lg font-semibold text-ink">{locale.explore.next}</p></div>
    </div>
  );
}
