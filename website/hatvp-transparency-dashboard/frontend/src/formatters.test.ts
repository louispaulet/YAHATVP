import { describe, expect, it } from "vitest";
import { formatCurrency, formatNumber, formatPercentage } from "./formatters";

describe("dashboard value formatting", () => {
  it("uses compact currency units for readable large amounts", () => {
    expect(formatCurrency(65_563_528, "en")).toBe("€65.6M");
    expect(formatCurrency(506_108, "en")).toBe("€506.1K");
    expect(formatCurrency(999, "en")).toBe("€999");
  });

  it("keeps signs and locale conventions when compacting values", () => {
    expect(formatCurrency(-1_250_000, "en")).toBe("-€1.3M");
    expect(formatCurrency(65_563_528, "fr")).toBe("65,6\u00a0M\u00a0€");
    expect(formatNumber(1_250_000, "fr")).toBe("1,3\u00a0M");
  });

  it("keeps ordinary counts grouped until they are genuinely large", () => {
    expect(formatNumber(74_791, "en")).toBe("74,791");
    expect(formatNumber(1_250_000, "en")).toBe("1.3M");
  });

  it("formats women shares with one decimal and locale conventions", () => {
    expect(formatPercentage(37.5, "en")).toBe("37.5%");
    expect(formatPercentage(37.5, "fr")).toBe("37,5\u00a0%");
  });
});
