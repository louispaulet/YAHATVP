import { describe, expect, it } from "vitest";
import { declarationXmlFixtures } from "../declaration-fixtures";
import { parseDeclarationXml } from "./declarationData";

describe("declaration XML display model", () => {
  it("keeps every source field addressable while grouping repeated records", () => {
    for (const xml of declarationXmlFixtures) {
      const result = parseDeclarationXml(xml);
      expect(result.error).toBeNull();
      expect(result.model).not.toBeNull();
      const model = result.model!;
      const renderedFieldCount = model.metadata.fields.length + model.sections.reduce((total, section) => total + section.fieldCount, 0);
      expect(model.summary.sourceFieldCount).toBe(renderedFieldCount);
      expect(model.summary.sectionCount).toBeGreaterThan(0);
      expect(model.summary.recordCount).toBeGreaterThan(0);
    }
  });

  it("extracts annual income values from nested HATVP item rows", () => {
    const model = parseDeclarationXml(declarationXmlFixtures[0]).model!;
    const mandate = model.sections.find((section) => section.key === "mandatElectifDto");
    const income = model.sections.find((section) => section.key === "revenuMandatDto");
    expect(mandate?.records[0].annualAmounts).toEqual([{ year: "2025", amount: 50000, field: "montant" }]);
    expect(income?.records[0].annualAmounts).toEqual([{ year: "2025", amount: 12000, field: "revenuElu" }]);
  });

  it("recognizes none-declared sections without inventing empty records", () => {
    const model = parseDeclarationXml(declarationXmlFixtures[1]).model!;
    const volunteer = model.sections.find((section) => section.key === "fonctionBenevoleDto");
    expect(volunteer?.declaredNone).toBe(true);
    expect(volunteer?.records).toHaveLength(0);
  });

  it("supports asset, attachment, amended, and company-interest variants", () => {
    const models = declarationXmlFixtures.slice(2).map((xml) => parseDeclarationXml(xml).model!);
    expect(models[0].sections.map((section) => section.key)).toEqual(expect.arrayContaining(["immeubleDto", "assuranceVieDto", "vehiculeDto", "passifDto"]));
    expect(models[0].summary.assetValueTotal).toBeGreaterThan(0);
    expect(models[1].sections.find((section) => section.key === "attachedFiles")?.records).toHaveLength(2);
    expect(models[1].sections.find((section) => section.key === "participationDirigeantDto")?.records[0].annualAmounts).toHaveLength(2);
    expect(models[2].sections.find((section) => section.key === "mandatElectifDto")?.records[0].annualAmounts).toHaveLength(2);
    expect(models[2].metadata.fields.find((field) => field.key === "complete")?.value).toBe("false");
  });

  it("returns a clear error for malformed or empty source", () => {
    expect(parseDeclarationXml("").model).toBeNull();
    expect(parseDeclarationXml("<declaration>").error).toBeTruthy();
  });
});
