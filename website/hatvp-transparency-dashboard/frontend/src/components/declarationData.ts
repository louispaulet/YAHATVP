export type DeclarationSectionCategory = "profile" | "mandate" | "income" | "activity" | "asset" | "other";

export interface DeclarationField {
  key: string;
  value: string;
}

export interface AnnualAmount {
  year: string;
  amount: number;
  field: string;
}

export interface DeclarationRecord {
  fields: DeclarationField[];
  annualAmounts: AnnualAmount[];
}

export interface DeclarationSection {
  key: string;
  category: DeclarationSectionCategory;
  declaredNone: boolean;
  records: DeclarationRecord[];
  fieldCount: number;
}

export interface DeclarationViewModel {
  metadata: DeclarationRecord;
  sections: DeclarationSection[];
  summary: {
    sourceFieldCount: number;
    sectionCount: number;
    recordCount: number;
    annualAmountCount: number;
    annualAmountTotal: number;
    assetValueTotal: number;
  };
}

export interface DeclarationParseResult {
  model: DeclarationViewModel | null;
  error: string | null;
}

const META_FIELDS = new Set(["dateDepot", "uuid", "origine", "complete", "declarationVersion"]);
const INCOME_FIELDS = new Set(["montant", "revenuElu", "revenuConjoint", "remuneration"]);
const ASSET_VALUE_FIELDS = new Set(["evaluation", "valeur", "valeurAchat", "valeurRachat", "montant", "restantDu"]);
const INCOME_SECTIONS = new Set(["mandatElectifDto", "revenuMandatDto", "activProfCinqDerniereDto", "participationDirigeantDto"]);
const ASSET_SECTIONS = new Set([
  "immeubleDto", "sciDto", "valeursNonEnBourseDto", "valeursEnBourseDto", "assuranceVieDto",
  "comptesBancaireDto", "bienDiverDto", "vehiculeDto", "fondDto", "autreBienDto", "bienEtrangerDto", "passifDto",
]);
const ACTIVITY_SECTIONS = new Set([
  "activConsultantDto", "activProfConjointDto", "fonctionBenevoleDto", "participationFinanciereDto",
  "activCollaborateursDto", "observationInteretDto",
]);

function tagName(node: Element): string {
  return node.localName || node.tagName.split(":").pop() || node.tagName;
}

function children(node: Element): Element[] {
  return Array.from(node.children) as Element[];
}

function cleanText(value: string | null): string {
  return (value || "").replace(/\s+/g, " ").trim();
}

function leafFields(node: Element): DeclarationField[] {
  const nested = children(node);
  if (nested.length === 0) return tagName(node) === "neant" ? [] : [{ key: tagName(node), value: cleanText(node.textContent) }];
  return nested.flatMap(leafFields);
}

function hasData(node: Element): boolean {
  return leafFields(node).length > 0;
}

function sectionRecords(section: Element): DeclarationRecord[] {
  const direct = children(section);
  const wrappers = direct.filter((node) => tagName(node) === "items");
  const nestedRows = wrappers.flatMap((wrapper) => children(wrapper).filter((node) => tagName(node) === "items"));
  const rows = nestedRows.length > 0 ? nestedRows : wrappers.filter(hasData);
  const sourceNodes = rows.length > 0 ? rows : direct.filter((node) => tagName(node) !== "neant" && hasData(node));
  return sourceNodes.map((node) => {
    const fields = leafFields(node);
    return { fields, annualAmounts: annualAmounts(fields) };
  });
}

function parseNumber(value: string): number | null {
  const normalized = value.replace(/[\s\u00a0\u202f]/g, "").replace(/[€$]/g, "");
  if (!/^-?\d+(?:[,.]\d+)?$/.test(normalized)) return null;
  const decimal = normalized.includes(",") ? normalized.replace(/\./g, "").replace(",", ".") : normalized;
  const parsed = Number(decimal);
  return Number.isFinite(parsed) ? parsed : null;
}

function annualAmounts(fields: DeclarationField[]): AnnualAmount[] {
  const years = fields.filter((field) => field.key === "annee").map((field) => field.value);
  const amounts = fields.filter((field) => INCOME_FIELDS.has(field.key));
  return years.flatMap((year, index) => {
    const field = amounts[index];
    const amount = field ? parseNumber(field.value) : null;
    return field && amount !== null ? [{ year, amount, field: field.key }] : [];
  });
}

function categoryFor(sectionKey: string): DeclarationSectionCategory {
  if (sectionKey === "general") return "profile";
  if (sectionKey === "mandatElectifDto") return "mandate";
  if (INCOME_SECTIONS.has(sectionKey)) return "income";
  if (ASSET_SECTIONS.has(sectionKey)) return "asset";
  if (ACTIVITY_SECTIONS.has(sectionKey)) return "activity";
  return "other";
}

function assetValueTotal(section: DeclarationSection): number {
  if (section.category !== "asset") return 0;
  return section.records.reduce((total, record) => total + record.fields.reduce((recordTotal, field) => {
    if (!ASSET_VALUE_FIELDS.has(field.key)) return recordTotal;
    const value = parseNumber(field.value);
    return value === null ? recordTotal : recordTotal + value;
  }, 0), 0);
}

function findDeclaration(root: Document): Element | null {
  if (root.documentElement && tagName(root.documentElement) === "declaration") return root.documentElement;
  return Array.from(root.getElementsByTagName("declaration"))[0] || Array.from(root.getElementsByTagNameNS("*", "declaration"))[0] || null;
}

function emptyRecord(): DeclarationRecord {
  return { fields: [], annualAmounts: [] };
}

export function parseDeclarationXml(xml: string): DeclarationParseResult {
  if (!xml.trim()) return { model: null, error: "The declaration source is empty." };
  const document = new DOMParser().parseFromString(xml, "application/xml");
  if (document.getElementsByTagName("parsererror").length > 0) return { model: null, error: "The declaration source could not be read." };
  const declaration = findDeclaration(document);
  if (!declaration) return { model: null, error: "The declaration source has no declaration node." };

  const direct = children(declaration);
  const metadataFields = direct.filter((node) => META_FIELDS.has(tagName(node))).flatMap(leafFields);
  const metadata = metadataFields.length > 0 ? { fields: metadataFields, annualAmounts: [] } : emptyRecord();
  const sections = direct
    .filter((node) => !META_FIELDS.has(tagName(node)))
    .map((node) => {
      const records = sectionRecords(node);
      return {
        key: tagName(node),
        category: categoryFor(tagName(node)),
        declaredNone: children(node).some((child) => tagName(child) === "neant" && cleanText(child.textContent).toLowerCase() === "true"),
        records,
        fieldCount: records.reduce((total, record) => total + record.fields.length, 0),
      };
    });
  const recordCount = sections.reduce((total, section) => total + section.records.length, 0);
  const annualAmounts = sections.flatMap((section) => section.records.flatMap((record) => record.annualAmounts));
  const sourceFieldCount = metadata.fields.length + sections.reduce((total, section) => total + section.fieldCount, 0);
  return {
    model: {
      metadata,
      sections,
      summary: {
        sourceFieldCount,
        sectionCount: sections.length,
        recordCount,
        annualAmountCount: annualAmounts.length,
        annualAmountTotal: annualAmounts.reduce((total, item) => total + item.amount, 0),
        assetValueTotal: sections.reduce((total, section) => total + assetValueTotal(section), 0),
      },
    },
    error: null,
  };
}

export function fieldValue(record: DeclarationRecord, keys: string[]): string | null {
  return record.fields.find((field) => keys.includes(field.key) && field.value)?.value || null;
}

export function sectionFieldValue(section: DeclarationSection, keys: string[]): string | null {
  for (const key of keys) {
    for (const record of section.records) {
      const value = fieldValue(record, [key]);
      if (value) return value;
    }
  }
  return null;
}
