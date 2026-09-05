import { useMemo, useState } from "react";
import { formatCurrency, formatNumber } from "../formatters";
import type { Locale, Language } from "../config/i18n";
import { declarationFieldLabel, declarationSectionLabel, sectionIcon } from "./declarationLabels";
import { fieldValue, parseDeclarationXml, type AnnualAmount, type DeclarationRecord, type DeclarationSection } from "./declarationData";

interface DeclarationViewProps {
  rawXml: string;
  language: Language;
  locale: Locale;
}

function sourceValue(value: string, fallback: string): string {
  return value || fallback;
}

function annualSummary(values: AnnualAmount[]): AnnualAmount[] {
  const totals = new Map<string, number>();
  for (const value of values) totals.set(value.year, (totals.get(value.year) || 0) + value.amount);
  return Array.from(totals, ([year, amount]) => ({ year, amount, field: "annual-total" })).sort((left, right) => left.year.localeCompare(right.year));
}

function firstSection(model: NonNullable<ReturnType<typeof parseDeclarationXml>["model"]>, key: string): DeclarationSection | null {
  return model.sections.find((section) => section.key === key) || null;
}

function displayTitle(record: DeclarationRecord, index: number, language: Language): string {
  return fieldValue(record, ["descriptionMandat", "description", "nomSociete", "typeCompte", "nature", "nom", "label"]) || `${language === "fr" ? "Élément" : "Entry"} ${index + 1}`;
}

function dateRange(record: DeclarationRecord, fallback: string): string | null {
  const start = fieldValue(record, ["dateDebut", "dateAcquisition", "dateSouscription", "datePassif"]);
  const end = fieldValue(record, ["dateFin"]);
  if (!start && !end) return null;
  return [start, end].filter(Boolean).join(" — ") || fallback;
}

function AnnualAmounts({ values, language, label, valuesLabel, amountLabel, yearLabel }: { values: AnnualAmount[]; language: Language; label: string; valuesLabel: string; amountLabel: string; yearLabel: string }) {
  if (values.length === 0) return null;
  const max = Math.max(...values.map((item) => Math.abs(item.amount)), 1);
  return (
    <div className="mt-5 rounded-2xl bg-ink/[0.035] p-4" data-testid="annual-amounts">
      <div className="flex items-center justify-between gap-3">
        <p className="text-xs font-bold uppercase tracking-[0.14em] text-emerald">{label}</p>
        <span className="text-xs font-semibold text-slate-400">{formatNumber(values.length, language)} {valuesLabel}</span>
      </div>
      <div className="mt-4 flex h-32 items-end gap-2 border-b border-slate-200 px-1" role="img" aria-label={`${label}: ${values.map((item) => `${item.year} ${formatCurrency(item.amount, language)}`).join(", ")}`}>
        {values.map((item, index) => (
          <div className="flex min-w-0 flex-1 flex-col items-center justify-end gap-2" key={`${item.year}-${item.field}-${index}`}>
            <div data-testid="annual-bar" className="w-full max-w-12 rounded-t-xl bg-emerald/80" style={{ height: `${Math.max(10, (Math.abs(item.amount) / max) * 78)}px` }} title={`${item.year}: ${formatCurrency(item.amount, language)}`} />
            <span className="text-[10px] font-bold text-slate-500">{item.year}</span>
          </div>
        ))}
      </div>
      <table className="mt-4 w-full border-collapse text-left text-xs" aria-label={label}>
        <thead><tr className="border-b border-slate-200 text-[10px] uppercase tracking-[0.12em] text-slate-400"><th className="pb-2 pr-3">{yearLabel}</th><th className="pb-2 text-right">{amountLabel}</th></tr></thead>
        <tbody className="divide-y divide-slate-100">{values.map((item, index) => <tr key={`annual-row-${item.year}-${item.field}-${index}`}><th scope="row" className="py-2 pr-3 font-semibold text-slate-600">{item.year}</th><td className="py-2 text-right font-bold text-ink">{formatCurrency(item.amount, language)}</td></tr>)}</tbody>
      </table>
    </div>
  );
}

function RecordFields({ record, language, fallback, labels, sectionKey }: { record: DeclarationRecord; language: Language; fallback: string; labels: Record<string, string>; sectionKey?: string }) {
  return (
    <dl className="mt-4 grid gap-x-4 gap-y-3 sm:grid-cols-2">
      {record.fields.map((field, index) => (
        <div className="min-w-0" key={`${field.key}-${index}`}>
          <dt className="text-[10px] font-bold uppercase tracking-[0.12em] text-slate-400">{declarationFieldLabel(field.key, language, labels, sectionKey)}</dt>
          <dd className="mt-1 break-words text-sm font-semibold leading-5 text-slate-700">{sourceValue(field.value, fallback)}</dd>
        </div>
      ))}
    </dl>
  );
}

function RecordCard({ record, index, section, language, locale }: { record: DeclarationRecord; index: number; section: DeclarationSection; language: Language; locale: Locale }) {
  const title = displayTitle(record, index, language);
  const range = dateRange(record, locale.declaration.notAvailable);
  return (
    <article className="rounded-2xl border border-slate-200/80 bg-white/80 p-4 sm:p-5">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <h3 className="text-base font-black tracking-tight text-ink">{title}</h3>
        {range && <span className="rounded-full bg-sky/20 px-3 py-1 text-xs font-bold text-ink">{range}</span>}
      </div>
      <RecordFields record={record} language={language} fallback={locale.declaration.notAvailable} labels={locale.declaration.fieldLabels} sectionKey={section.key} />
      {record.annualAmounts.length > 0 && section.records.length === 1 && <AnnualAmounts values={record.annualAmounts} language={language} label={locale.declaration.annualValues} valuesLabel={locale.declaration.valuesLabel} amountLabel={locale.declaration.fieldLabels.montant} yearLabel={locale.declaration.fieldLabels.annee} />}
    </article>
  );
}

function DeclarationSectionView({ section, language, locale }: { section: DeclarationSection; language: Language; locale: Locale }) {
  const annualAmounts = annualSummary(section.records.flatMap((record) => record.annualAmounts));
  const Icon = sectionIcon(section.key);
  return (
    <section id={`declaration-section-${section.key}`} className="dashboard-card scroll-mt-6 p-5 sm:p-7" aria-labelledby={`section-${section.key}`}>
      <div className="flex items-start gap-4">
        <span className="flex size-11 shrink-0 items-center justify-center rounded-2xl bg-emerald/10 text-emerald" aria-hidden="true"><Icon size={20} strokeWidth={1.8} /></span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-baseline sm:justify-between">
            <h2 id={`section-${section.key}`} className="text-xl font-black tracking-tight text-ink">{declarationSectionLabel(section.key, language, locale.declaration.sectionLabels)}</h2>
            <span className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{formatNumber(section.records.length, language)} {locale.declaration.records}</span>
          </div>
          {section.records.length === 0 && <details className="mt-3 rounded-xl bg-slate-50 px-4 py-3"><summary className="cursor-pointer text-sm font-semibold text-slate-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald">{section.declaredNone ? locale.declaration.noneDeclared : locale.declaration.emptySection}</summary>{!section.declaredNone && <p className="mt-2 text-xs leading-5 text-slate-500">{locale.declaration.emptySectionDetail}</p>}</details>}
        </div>
      </div>
      {annualAmounts.length > 0 && section.records.length > 1 && <AnnualAmounts values={annualAmounts} language={language} label={locale.declaration.annualValues} valuesLabel={locale.declaration.valuesLabel} amountLabel={locale.declaration.fieldLabels.montant} yearLabel={locale.declaration.fieldLabels.annee} />}
      {section.records.length > 0 && <div className="mt-5 grid min-w-0 gap-4 lg:grid-cols-2">{section.records.map((record, index) => <RecordCard key={`${section.key}-${index}`} record={record} index={index} section={section} language={language} locale={locale} />)}</div>}
    </section>
  );
}

export function DeclarationView({ rawXml, language, locale }: DeclarationViewProps) {
  const [copied, setCopied] = useState(false);
  const parsed = useMemo(() => parseDeclarationXml(rawXml), [rawXml]);
  const model = parsed.model;
  if (!model) {
    return <section className="dashboard-card mt-8 border-amber-200 bg-amber-50 p-6 text-sm text-amber-950"><p className="font-bold">{locale.declaration.parseError}</p><p className="mt-2">{parsed.error}</p></section>;
  }

  const profile = firstSection(model, "general");
  const meta = model.metadata;
  const nonProfileSections = model.sections.filter((section) => section.key !== "general");
  return (
    <div className="mt-8 space-y-6">
      <section className="grid gap-4 lg:grid-cols-[1.3fr_0.7fr]">
        <article className="dashboard-card p-5 sm:p-7">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.declaration.overviewEyebrow}</p>
          <h2 className="mt-2 text-2xl font-black tracking-tight text-ink">{locale.declaration.overviewTitle}</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">{locale.declaration.overviewDescription}</p>
          <dl className="mt-6 grid gap-4 sm:grid-cols-2">
            <div><dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.declaration.sections}</dt><dd className="mt-1 text-sm font-bold text-slate-700">{formatNumber(model.summary.sectionCount, language)}</dd></div>
            <div><dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.declaration.records}</dt><dd className="mt-1 text-sm font-bold text-slate-700">{formatNumber(model.summary.recordCount, language)}</dd></div>
            <div><dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.declaration.annualValues}</dt><dd className="mt-1 text-sm font-bold text-slate-700">{formatNumber(model.summary.annualAmountCount, language)}</dd></div>
          </dl>
        </article>
        <aside className="rounded-[1.5rem] bg-ink p-5 text-white shadow-soft sm:p-7">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-lime">{locale.declaration.dataEyebrow}</p>
          <p className="mt-3 text-4xl font-black tracking-tight">{formatNumber(model.summary.sourceFieldCount, language)}</p>
          <p className="mt-1 text-sm font-semibold text-slate-300">{locale.declaration.sourceFields}</p>
          <div className="mt-6 grid grid-cols-2 gap-3 border-t border-white/15 pt-5">
            <div><p className="text-2xl font-black">{formatNumber(model.summary.sectionCount, language)}</p><p className="text-xs text-slate-300">{locale.declaration.sections}</p></div>
            <div><p className="text-2xl font-black">{formatNumber(model.summary.recordCount, language)}</p><p className="text-xs text-slate-300">{locale.declaration.records}</p></div>
          </div>
        </aside>
      </section>

      {profile && <section className="dashboard-card min-w-0 p-5 sm:p-7"><div className="flex items-baseline justify-between gap-4"><div><p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.declaration.profileEyebrow}</p><h2 className="mt-2 text-xl font-black tracking-tight text-ink">{locale.declaration.profileTitle}</h2></div><span className="text-xs font-semibold text-slate-400">{formatNumber(profile.fieldCount, language)} {locale.declaration.fieldsLabel}</span></div><RecordFields record={{ fields: profile.records.flatMap((record) => record.fields).filter((field) => !["email", "adresse", "telephoneDec", "voie", "complement", "codePostal", "ville", "pays"].includes(field.key)), annualAmounts: [] }} language={language} fallback={locale.declaration.notAvailable} labels={locale.declaration.fieldLabels} sectionKey="general" /></section>}

      {nonProfileSections.length > 0 && <nav className="dashboard-card p-5 sm:p-6" aria-label={locale.declaration.sectionIndex}><p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.declaration.sectionIndex}</p><div className="mt-3 flex flex-wrap gap-2">{nonProfileSections.map((section) => <a key={section.key} href={`#declaration-section-${section.key}`} className="rounded-full bg-surface-subtle px-3 py-2 text-sm font-bold text-ink transition hover:bg-lime focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald">{declarationSectionLabel(section.key, language, locale.declaration.sectionLabels)}</a>)}</div></nav>}

      <div className="space-y-6">{nonProfileSections.map((section) => <DeclarationSectionView key={section.key} section={section} language={language} locale={locale} />)}</div>

      <details className="dashboard-card min-w-0 p-5 sm:p-7"><summary className="cursor-pointer text-sm font-bold text-ink focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-emerald">{locale.declaration.technicalFields} ({formatNumber(meta.fields.length, language)} {locale.declaration.fieldsLabel})</summary><p className="mt-3 text-sm leading-6 text-slate-500">{locale.declaration.technicalDescription}</p><div className="mt-4"><RecordFields record={meta} language={language} fallback={locale.declaration.notAvailable} labels={locale.declaration.fieldLabels} /></div></details>

      <details className="dashboard-card min-w-0 overflow-hidden">
        <summary className="cursor-pointer list-none px-5 py-5 text-sm font-bold text-ink transition hover:text-emerald sm:px-7">{locale.declaration.sourceDisclosure}</summary>
        <div className="border-t border-slate-200 px-5 pb-5 pt-4 sm:px-7"><div className="flex flex-wrap items-start justify-between gap-3"><p className="max-w-3xl text-sm leading-6 text-slate-500">{locale.declaration.sourceDescription}</p><button type="button" className="min-h-10 rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-bold text-ink transition hover:border-emerald hover:text-emerald focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald" onClick={() => { if (!navigator.clipboard) return; void navigator.clipboard.writeText(rawXml).then(() => setCopied(true)).catch(() => setCopied(false)); }}>{copied ? locale.declaration.copiedXml : locale.declaration.copyXml}</button></div><p className="sr-only" aria-live="polite">{copied ? locale.declaration.copiedXml : ""}</p><pre aria-label={locale.declaration.rawXmlLabel} className="mt-4 max-h-[70vh] overflow-auto rounded-2xl bg-[#101815] p-5 text-xs leading-6 text-slate-200"><code>{rawXml}</code></pre></div>
      </details>
    </div>
  );
}
