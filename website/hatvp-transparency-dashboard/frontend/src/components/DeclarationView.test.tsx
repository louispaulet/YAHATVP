import { MemoryRouter } from "react-router-dom";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { getLocale } from "../config/i18n";
import { declarationXmlFixtures } from "../declaration-fixtures";
import { DeclarationView } from "./DeclarationView";

describe("DeclarationView", () => {
  it("renders annual bars with concrete heights", () => {
    render(<MemoryRouter><DeclarationView rawXml={declarationXmlFixtures[1]} language="en" locale={getLocale("en")} /></MemoryRouter>);

    const bars = screen.getAllByTestId("annual-bar");
    expect(bars).toHaveLength(2);
    expect(bars[0]).toHaveStyle({ height: "78px" });
    expect(bars.every((bar) => !bar.getAttribute("style")?.includes("%"))).toBe(true);
  });
});
