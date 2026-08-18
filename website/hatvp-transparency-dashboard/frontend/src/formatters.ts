import type { Language } from "./config/i18n";

const localeByLanguage: Record<Language, string> = {
  en: "en-GB",
  fr: "fr-FR",
};

const compactUnits = [
  { value: 1_000_000_000_000, en: "T", fr: "Bn" },
  { value: 1_000_000_000, en: "B", fr: "Md" },
  { value: 1_000_000, en: "M", fr: "M" },
  { value: 1_000, en: "K", fr: "k" },
] as const;

const COMPACT_NUMBER_THRESHOLD = 1_000_000;
const COMPACT_CURRENCY_THRESHOLD = 1_000;

function localeFor(language: Language): string {
  return localeByLanguage[language];
}

function compactValue(value: number, language: Language, currency: boolean): string {
  const unit = compactUnits.find(({ value: unitValue }) => Math.abs(value) >= unitValue);
  if (!unit) return "";

  const sign = value < 0 ? "-" : "";
  const scaled = new Intl.NumberFormat(localeFor(language), { maximumFractionDigits: 1 }).format(Math.abs(value) / unit.value);
  const suffix = language === "fr" ? unit.fr : unit.en;
  if (currency && language === "fr") return `${sign}${scaled}\u00a0${suffix}\u00a0€`;
  if (currency) return `${sign}€${scaled}${suffix}`;
  return `${sign}${scaled}${language === "fr" ? `\u00a0${suffix}` : suffix}`;
}

export function formatNumber(value: number, language: Language): string {
  if (Math.abs(value) >= COMPACT_NUMBER_THRESHOLD) return compactValue(value, language, false);
  return new Intl.NumberFormat(localeFor(language)).format(value);
}

export function formatCurrency(value: number, language: Language): string {
  if (Math.abs(value) >= COMPACT_CURRENCY_THRESHOLD) return compactValue(value, language, true);
  return new Intl.NumberFormat(localeFor(language), {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(value);
}
