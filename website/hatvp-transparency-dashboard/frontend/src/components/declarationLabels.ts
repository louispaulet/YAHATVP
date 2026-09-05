import { ArrowUpRight, BriefcaseBusiness, Circle, Euro, House, Minus, UserRound, type LucideIcon } from "lucide-react";
import type { Language } from "../config/i18n";

export type DeclarationLabelDictionary = Record<string, string>;

function humanize(value: string): string {
  return value
    .replace(/Dto$/, "")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/^./, (character) => character.toUpperCase());
}

/** Resolve a source section through the active locale, with a readable fallback for new XML nodes. */
export function declarationSectionLabel(key: string, _language: Language, labels: DeclarationLabelDictionary = {}): string {
  return labels[key] || humanize(key);
}

/** Resolve a source field through the active locale, with optional section context for repeated labels. */
export function declarationFieldLabel(key: string, _language: Language, labels: DeclarationLabelDictionary = {}, sectionKey?: string): string {
  return (sectionKey && labels[`${sectionKey}.${key}`]) || labels[key] || humanize(key);
}

/** Use the shared Lucide vocabulary so section meaning does not depend on a glyph or a colour. */
export function sectionIcon(key: string): LucideIcon {
  if (key === "general") return UserRound;
  if (key === "mandatElectifDto") return ArrowUpRight;
  if (key.includes("activ") || key.includes("fonction") || key.includes("participation")) return BriefcaseBusiness;
  if (key.includes("passif")) return Minus;
  if (key.includes("immeuble") || key.includes("sci") || key.includes("bien")) return House;
  if (key.includes("compte") || key.includes("valeur") || key.includes("assurance") || key.includes("fond")) return Euro;
  return Circle;
}
