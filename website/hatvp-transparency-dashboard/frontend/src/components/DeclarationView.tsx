import { useMemo } from "react";
import { formatCurrency, formatNumber } from "../formatters";
import type { Locale, Language } from "../config/i18n";
import { declarationFieldLabel, declarationSectionLabel, sectionIcon } from "./declarationLabels";
import { fieldValue, parseDeclarationXml, sectionFieldValue, type AnnualAmount, type DeclarationRecord, type DeclarationSection } from "./declarationData";

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

function AnnualAmounts({ values, language, label }: { values: AnnualAmount[]; language: Language; label: string }) {
  if (values.length === 0) return null;
  const max = Math.max(...values.map((item) => Math.abs(item.amount)), 1);
  return (
    <div className="mt-5 rounded-2xl bg-ink/[0.035] p-4" data-testid="annual-amounts">
      <div className="flex items-center justify-between gap-3">
        <p className="text-xs font-bold uppercase tracking-[0.14em] text-emerald">{label}</p>
        <span className="text-xs font-semibold text-slate-400">{formatNumber(values.length, language)} {language === "fr" ? "valeurs" : "values"}</span>
      </div>
      <div className="mt-4 flex h-32 items-end gap-2 border-b border-slate-200 px-1" role="img" aria-label={`${label}: ${values.map((item) => `${item.year} ${formatCurrency(item.amount, language)}`).join(", ")}`}>
        {values.map((item, index) => (
          <div className="flex min-w-0 flex-1 flex-col items-center justify-end gap-2" key={`${item.year}-${item.field}-${index}`}>
            <span className="max-w-full truncate text-[10px] font-bold text-slate-500">{formatCurrency(item.amount, language)}</span>
            <div className="w-full max-w-12 rounded-t-xl bg-emerald/80" style={{ height: `${Math.max(10, (Math.abs(item.amount) / max) * 78)}%` }} title={`${item.year}: ${formatCurrency(item.amount, language)}`} />
            <span className="text-[10px] font-bold text-slate-500">{item.year}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function RecordFields({ record, language, fallback }: { record: DeclarationRecord; language: Language; fallback: string }) {
  return (
    <dl className="mt-4 grid gap-x-4 gap-y-3 sm:grid-cols-2">
      {record.fields.map((field, index) => (
        <div className="min-w-0" key={`${field.key}-${index}`}>
          <dt className="text-[10px] font-bold uppercase tracking-[0.12em] text-slate-400">{declarationFieldLabel(field.key, language)}</dt>
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
      <RecordFields record={record} language={language} fallback={locale.declaration.notAvailable} />
      {record.annualAmounts.length > 0 && section.records.length === 1 && <AnnualAmounts values={record.annualAmounts} language={language} label={locale.declaration.annualValues} />}
    </article>
  );
}

function DeclarationSectionView({ section, language, locale }: { section: DeclarationSection; language: Language; locale: Locale }) {
  const annualAmounts = annualSummary(section.records.flatMap((record) => record.annualAmounts));
  return (
    <section className="dashboard-card p-5 sm:p-7" aria-labelledby={`section-${section.key}`}>
      <div className="flex items-start gap-4">
        <span className="flex size-11 shrink-0 items-center justify-center rounded-2xl bg-emerald/10 text-xl font-black text-emerald" aria-hidden="true">{sectionIcon(section.key)}</span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-baseline sm:justify-between">
            <h2 id={`section-${section.key}`} className="text-xl font-black tracking-tight text-ink">{declarationSectionLabel(section.key, language)}</h2>
            <span className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{formatNumber(section.records.length, language)} {locale.declaration.records}</span>
          </div>
          {section.declaredNone && section.records.length === 0 && <p className="mt-3 rounded-xl bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-500">{locale.declaration.noneDeclared}</p>}
        </div>
      </div>
      {annualAmounts.length > 0 && section.records.length > 1 && <AnnualAmounts values={annualAmounts} language={language} label={locale.declaration.annualValues} />}
      {section.records.length > 0 && <div className="mt-5 grid min-w-0 gap-4 lg:grid-cols-2">{section.records.map((record, index) => <RecordCard key={`${section.key}-${index}`} record={record} index={index} section={section} language={language} locale={locale} />)}</div>}
    </section>
  );
}

export function DeclarationView({ rawXml, language, locale }: DeclarationViewProps) {
  const parsed = useMemo(() => parseDeclarationXml(rawXml), [rawXml]);
  const model = parsed.model;
  if (!model) {
    return <section className="dashboard-card mt-8 border-amber-200 bg-amber-50 p-6 text-sm text-amber-950"><p className="font-bold">{locale.declaration.parseError}</p><p className="mt-2">{parsed.error}</p></section>;
  }

  const profile = firstSection(model, "general");
  const meta = model.metadata;
  const type = profile ? sectionFieldValue(profile, ["label"]) : null;
  const mandate = profile ? sectionFieldValue(profile, ["labelTypeMandat", "typeMandat", "label"]) : null;
  const organization = profile ? sectionFieldValue(profile, ["labelOrgane", "labelOrgan", "nomOrgane"]) : null;
  const status = fieldValue(meta, ["complete"])?.toLowerCase() === "true" ? locale.declaration.complete : locale.declaration.incomplete;
  const nonProfileSections = model.sections.filter((section) => section.key !== "general");
  return (
    <div className="mt-8 space-y-6">
      <section className="grid gap-4 lg:grid-cols-[1.3fr_0.7fr]">
        <article className="dashboard-card p-5 sm:p-7">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.declaration.overviewEyebrow}</p>
          <h2 className="mt-2 text-2xl font-black tracking-tight text-ink">{locale.declaration.overviewTitle}</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">{locale.declaration.overviewDescription}</p>
          <dl className="mt-6 grid gap-4 sm:grid-cols-2">
            <div><dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.declaration.fields.type}</dt><dd className="mt-1 text-sm font-bold text-slate-700">{sourceValue(type || "", locale.declaration.notAvailable)}</dd></div>
            <div><dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.search.fields.mandate}</dt><dd className="mt-1 text-sm font-bold text-slate-700">{sourceValue(mandate || "", locale.declaration.notAvailable)}</dd></div>
            <div><dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.search.fields.organ}</dt><dd className="mt-1 text-sm font-bold text-slate-700">{sourceValue(organization || "", locale.declaration.notAvailable)}</dd></div>
            <div><dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{locale.declaration.fields.status}</dt><dd className="mt-1 text-sm font-bold text-slate-700">{status}</dd></div>
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

      {profile && <section className="dashboard-card min-w-0 p-5 sm:p-7"><div className="flex items-baseline justify-between gap-4"><div><p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.declaration.profileEyebrow}</p><h2 className="mt-2 text-xl font-black tracking-tight text-ink">{locale.declaration.profileTitle}</h2></div><span className="text-xs font-semibold text-slate-400">{formatNumber(profile.fieldCount, language)} {locale.declaration.fieldsLabel}</span></div><RecordFields record={{ fields: profile.records.flatMap((record) => record.fields), annualAmounts: [] }} language={language} fallback={locale.declaration.notAvailable} /></section>}

      <section className="dashboard-card p-5 sm:p-7"><div className="flex items-baseline justify-between gap-4"><div><p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald">{locale.declaration.metadataEyebrow}</p><h2 className="mt-2 text-xl font-black tracking-tight text-ink">{locale.declaration.metadataTitle}</h2></div><span className="text-xs font-semibold text-slate-400">{formatNumber(meta.fields.length, language)} {locale.declaration.fieldsLabel}</span></div><RecordFields record={meta} language={language} fallback={locale.declaration.notAvailable} /></section>

      <div className="space-y-6">{nonProfileSections.map((section) => <DeclarationSectionView key={section.key} section={section} language={language} locale={locale} />)}</div>

      <details className="dashboard-card min-w-0 overflow-hidden">
        <summary className="cursor-pointer list-none px-5 py-5 text-sm font-bold text-ink transition hover:text-emerald sm:px-7">{locale.declaration.sourceTitle}<span className="ml-2 text-slate-400">↘</span></summary>
        <div className="border-t border-slate-200 px-5 pb-5 pt-4 sm:px-7"><p className="mb-4 text-sm leading-6 text-slate-500">{locale.declaration.sourceDescription}</p><pre aria-label={locale.declaration.rawXmlLabel} className="max-h-[70vh] overflow-auto rounded-2xl bg-[#101815] p-5 text-xs leading-6 text-slate-200"><code>{rawXml}</code></pre></div>
      </details>
    </div>
  );
}
