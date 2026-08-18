import type { DeclarationSearchResult } from "../types";

export function searchValue(value: string | null, fallback: string): string {
  return value?.trim() || fallback;
}

export function declarationName(result: DeclarationSearchResult, fallback: string): string {
  return [result.civilite, result.firstName, result.lastName].filter(Boolean).join(" ") || fallback;
}

export function declarationDate(value: string | null, language: string, fallback: string): string {
  return value
    ? new Date(`${value}T00:00:00`).toLocaleDateString(language === "fr" ? "fr-FR" : "en-GB")
    : fallback;
}
