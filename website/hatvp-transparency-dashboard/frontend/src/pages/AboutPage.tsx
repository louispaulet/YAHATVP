import { SourceLinkCard } from "../components/SourceLinkCard";
import { useI18n } from "../context/I18nContext";
import { ExternalLink } from "lucide-react";
import { Disclosure } from "../components/Disclosure";

export function AboutPage() {
  const { locale } = useI18n();
  return (
    <div className="mx-auto max-w-3xl px-5 py-16 lg:px-8 lg:py-24">
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.about.eyebrow}</p>
      <h1 className="mt-4 text-4xl font-black tracking-tight sm:text-5xl">{locale.about.title}</h1>
      <div className="mt-8 space-y-6 text-base leading-8 text-slate-600">{locale.about.paragraphs.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}<p>{locale.about.sourcePrefix}</p></div>
      <section className="mt-12" aria-labelledby="reader-questions-title">
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.about.eyebrow}</p>
        <h2 id="reader-questions-title" className="mt-2 text-2xl font-black tracking-tight text-ink">{locale.about.readerTitle}</h2>
        <div className="mt-4 space-y-3">{Object.entries(locale.about.readerQuestions).map(([key, item]) => <Disclosure key={key} summary={item.question} open={key === "what"}><p>{item.answer}</p></Disclosure>)}</div>
      </section>
      <section className="mt-12">
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.about.sources.eyebrow}</p>
        <h2 className="mt-2 text-2xl font-black tracking-tight text-ink">{locale.about.sources.title}</h2>
        <p className="mt-3 text-sm leading-6 text-slate-600">{locale.about.sources.description}</p>
        <div className="mt-5 grid gap-4 sm:grid-cols-3">{locale.about.sources.links.map((link) => <SourceLinkCard key={link.href} link={link} />)}</div>
      </section>
      <div className="mt-8 grid gap-6 md:grid-cols-2">
        <section className="dashboard-card border-lime/40 p-6">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.about.archive.eyebrow}</p>
          <h2 className="mt-2 text-2xl font-black tracking-tight text-ink">{locale.about.archive.title}</h2>
          <p className="mt-3 text-sm leading-6 text-slate-600">{locale.about.archive.description}</p>
          <a className="mt-4 inline-flex min-h-10 items-center gap-1 text-sm font-bold text-emerald hover:underline" href={locale.about.archive.href} target="_blank" rel="noreferrer">{locale.about.archive.link}<ExternalLink size={14} strokeWidth={2} aria-hidden="true" /></a>
        </section>
        <section className="dashboard-card border-lime/40 p-6">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.about.huggingFace.eyebrow}</p>
          <h2 className="mt-2 text-2xl font-black tracking-tight text-ink">{locale.about.huggingFace.title}</h2>
          <p className="mt-3 text-sm leading-6 text-slate-600">{locale.about.huggingFace.description}</p>
          <a className="mt-4 inline-flex min-h-10 items-center gap-1 text-sm font-bold text-emerald hover:underline" href={locale.about.huggingFace.href} target="_blank" rel="noreferrer">{locale.about.huggingFace.link}<ExternalLink size={14} strokeWidth={2} aria-hidden="true" /></a>
        </section>
      </div>
      <a className="dashboard-card group mt-6 block p-5 transition hover:-translate-y-0.5 hover:border-emerald/40 hover:shadow-soft" href={locale.about.project.href} target="_blank" rel="noreferrer">
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.about.project.eyebrow}</p>
        <span className="mt-2 flex items-start justify-between gap-3 text-sm font-bold text-ink"><span>{locale.about.project.title}</span><ExternalLink size={16} strokeWidth={2} aria-hidden="true" className="shrink-0 text-emerald transition group-hover:translate-x-0.5" /></span>
        <span className="mt-3 block text-sm leading-6 text-slate-500">{locale.about.project.description}</span>
      </a>
      <div className="mt-10 grid gap-4 sm:grid-cols-2">
        <div className="dashboard-card p-5"><p className="text-xs font-bold uppercase tracking-[0.14em] text-slate-400">{locale.about.curatedTables}</p><p className="mt-2 text-2xl font-black">4</p><p className="mt-1 text-sm text-slate-500">{locale.about.curatedTablesDetail}</p></div>
        <div className="dashboard-card p-5"><p className="text-xs font-bold uppercase tracking-[0.14em] text-slate-400">{locale.about.updateRhythm}</p><p className="mt-2 text-2xl font-black">{locale.about.updateRhythmValue}</p><p className="mt-1 text-sm text-slate-500">{locale.about.updateRhythmDetail}</p></div>
      </div>
    </div>
  );
}
