import React from "react";
import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RepLeaderboardTable } from "./RepLeaderboardTable";

describe("RepLeaderboardTable", () => {
  it("sorts reps by average score descending", () => {
    render(
      <RepLeaderboardTable
        reps={[
          { id: "rep-01", name: "Jordan Blake", vertical: "home_services", call_count: 4, average_score: 70 },
          { id: "rep-02", name: "Casey Nguyen", vertical: "home_services", call_count: 5, average_score: 90 },
        ]}
      />
    );

    const rows = screen.getAllByRole("row");
    expect(rows[1]).toHaveTextContent("Casey Nguyen");
    expect(rows[2]).toHaveTextContent("Jordan Blake");
  });
});
