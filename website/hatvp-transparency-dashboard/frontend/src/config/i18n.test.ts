import { describe, expect, it } from "vitest";
import { translateDataLabel } from "./i18n";

const declarationTypes = [
  ["Déclaration d'intérêts", "Declaration of interests"],
  ["Déclaration d'intérêts modificative", "Amended declaration of interests"],
  ["Déclaration d'intérêts et d'activités", "Declaration of interests and activities"],
  ["Déclaration d'intérêts et d'activités modificative", "Amended declaration of interests and activities"],
  ["Déclaration de situation patrimoniale", "Asset declaration"],
  ["Déclaration de situation patrimoniale modificative", "Amended asset declaration"],
  ["Déclaration de situation patrimoniale de fin de mandat", "End-of-mandate asset declaration"],
  ["Déclaration de situation patrimoniale de fin de mandat modificative", "Amended end-of-mandate asset declaration"],
  ["Déclaration initiale de situation patrimoniale", "Initial asset declaration"],
] as const;

describe("dashboard label configuration", () => {
  it("translates every declaration type into English", () => {
    for (const [source, expected] of declarationTypes) {
      expect(translateDataLabel("en", "declarationTypes", source)).toBe(expected);
    }
  });

  it("accepts the malformed title casing emitted by the old fallback", () => {
    expect(translateDataLabel("en", "declarationTypes", "DéClaration D'IntéRêTs")).toBe("Declaration of interests");
    expect(translateDataLabel("fr", "declarationTypes", "DéClaration D'IntéRêTs Modificative")).toBe("Déclaration d’intérêts modificative");
  });
});
