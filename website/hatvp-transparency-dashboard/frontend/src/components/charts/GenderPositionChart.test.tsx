import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import GenderPositionChart from "./GenderPositionChart";

describe("gender position chart", () => {
  it("shows women share over total people and exposes a clear parity legend", () => {
    render(
      <GenderPositionChart
        positions={[
          { label: "Largest position", male: 6, female: 3, unknown: 1 },
          { label: "Second position", male: 1, female: 3, unknown: 1 },
        ]}
        emptyLabel="No positions"
        language="en"
        chartLabel="Share of women by job position"
        legendLabel="Chart legend"
        womenLabel="Women"
        parityLabel="Parity (50%)"
        peopleLabel="people total"
        noteLabel="Positions are sorted by total people."
      />,
    );

    expect(screen.getByText("Parity (50%)")).toBeInTheDocument();
    expect(screen.getByText("30.0%")).toBeInTheDocument();
    expect(screen.getByText("60.0%")).toBeInTheDocument();
    expect(screen.getByText("10 people total")).toBeInTheDocument();
    expect(screen.getByText("5 people total")).toBeInTheDocument();
    expect(screen.getByText(/Largest position/)).toHaveClass("break-words");
    expect(screen.getByRole("img", { name: /Largest position: 30\.0%, 10 people total/ })).toBeInTheDocument();
  });
});
