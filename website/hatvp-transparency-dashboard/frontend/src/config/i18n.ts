import en from "./locales/en.json";
import fr from "./locales/fr.json";

export const languages = ["en", "fr"] as const;
export type Language = (typeof languages)[number];
export type Locale = typeof en;
export type DataLabelCategory = keyof Locale["labels"];

const localeByLanguage: Record<Language, Locale> = { en, fr };

export const defaultLanguage: Language = "en";

export function getLocale(language: Language): Locale {
  return localeByLanguage[language];
}

export function translateDataLabel(language: Language, category: DataLabelCategory, value: string): string {
  const labels = getLocale(language).labels[category] as Record<string, string>;
  return labels[value] ?? humanizeDataLabel(value);
}

function humanizeDataLabel(value: string): string {
  return value
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/^./, (character) => character.toUpperCase());
}
