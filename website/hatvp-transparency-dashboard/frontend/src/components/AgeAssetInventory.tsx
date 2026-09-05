import { translateDataLabel, type Language, type Locale } from "../config/i18n";
import { ExternalLink } from "lucide-react";
import { formatCurrency } from "../formatters";
import type { AgeAnalysisResponse } from "../types";
import { Panel } from "./Panel";

type Labels = Locale["ageAnalysis"];
type Asset = AgeAnalysisResponse["assetInventory"][number];

function dateLabel(value: string | null, language: Language, fallback: string): string {
  if (!value) return fallback;
  return new Intl.DateTimeFormat(language === "fr" ? "fr-FR" : "en-GB", {
    dateStyle: "medium",
  }).format(new Date(`${value}T00:00:00`));
}

function eventText(asset: Asset, language: Language, labels: Labels): string {
  if (!asset.eventDateRaw) return labels.noEventDate;
  const verbs = labels.assetEvents as Record<string, string>;
  const verb = verbs[asset.eventKind || ""] || labels.assetEvents.unknown;
  const when = asset.eventDate
    ? dateLabel(asset.eventDate, language, asset.eventDateRaw)
    : asset.eventDateRaw;
  if (asset.ageYears !== null) return `${verb} ${when} · ${labels.age} ${asset.ageYears}`;
  if (asset.ageRangeMin !== null && asset.ageRangeMax !== null) {
    return `${verb} ${when} · ${labels.approximateAge} ${asset.ageRangeMin}–${asset.ageRangeMax}`;
  }
  return `${verb} ${when}`;
}

function AssetCard({ asset, language, labels }: {
  asset: Asset; language: Language; labels: Labels;
}) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-4 sm:p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <h3 className="min-w-0 font-bold text-ink">{asset.name || labels.unnamedAsset}</h3>
        {asset.value !== null && <span className="shrink-0 text-sm font-black text-emerald">{formatCurrency(asset.value, language)}</span>}
      </div>
      <p className="mt-3 text-sm font-semibold leading-6 text-slate-700">{eventText(asset, language, labels)}</p>
      <p className="mt-1 text-xs leading-5 text-slate-500">{labels.valueDeclaredIn} {dateLabel(asset.declaredAt, language, labels.unknown)}</p>
      <details className="mt-4 border-t border-slate-100 pt-3 text-xs text-slate-500">
        <summary className="cursor-pointer rounded font-bold text-slate-600 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald">{labels.provenance}</summary>
        <dl className="mt-3 grid gap-2 sm:grid-cols-3">
          <div><dt className="font-bold">{labels.rawType}</dt><dd className="break-all">{asset.kind}</dd></div>
          <div><dt className="font-bold">{labels.rawDate}</dt><dd>{asset.eventDateRaw || labels.unknown}</dd></div>
          <div><dt className="font-bold">{labels.rawField}</dt><dd>{asset.eventSourceField || labels.unknown}</dd></div>
        </dl>
      </details>
    </article>
  );
}

export function AgeAssetInventory({ assets, language, labels }: {
  assets: AgeAnalysisResponse["assetInventory"]; language: Language; labels: Labels;
}) {
  const groups = Array.from(assets.reduce((map, item) => {
    map.set(item.kind, [...(map.get(item.kind) || []), item]);
    return map;
  }, new Map<string, Asset[]>()).entries());
  const hasMinorSubscription = assets.some((asset) =>
    asset.eventKind === "subscription" && asset.ageYears !== null && asset.ageYears < 18);
  return (
    <div className="mt-6">
      <Panel title={labels.assetTitle} eyebrow={labels.assetEyebrow}>
        <p className="max-w-4xl text-sm leading-6 text-slate-500">{labels.assetDescription}</p>
        <p className="mt-3 max-w-4xl text-sm leading-6 text-slate-600">{labels.assetDateClarification}</p>
        {hasMinorSubscription && <aside className="mt-5 rounded-2xl border border-sky-200 bg-sky-50 p-4 text-sm leading-6 text-slate-700">{labels.minorPolicyNote} <a href="https://www.economie.gouv.fr/particuliers/gerer-mon-argent/gerer-mon-budget-et-mon-epargne/quels-produits-depargne-pouvez-vous-ouvrir-pour-votre-enfant" target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 font-bold text-emerald underline decoration-emerald/30 underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald">{labels.minorPolicyLink}<ExternalLink size={13} strokeWidth={2} aria-hidden="true" /></a></aside>}
        {assets.length === 0 && <p className="py-8 text-sm text-slate-500">{labels.noAssets}</p>}
        <div className="mt-6 space-y-6">{groups.map(([kind, items]) => <section key={kind}><div className="flex items-baseline justify-between gap-3"><h3 className="text-lg font-black text-ink">{translateDataLabel(language, "assetSections", kind)}</h3><span className="text-xs font-bold text-slate-400">{items.length} {items.length === 1 ? labels.item : labels.items}</span></div><div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-3">{items.map((item) => <AssetCard key={item.sourceId} asset={item} language={language} labels={labels} />)}</div></section>)}</div>
      </Panel>
    </div>
  );
}
