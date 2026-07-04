import React from "react";
import "@testing-library/jest-dom";
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RepTrendChart } from "./RepTrendChart";

describe("RepTrendChart", () => {
  it("renders an svg chart without crashing", () => {
    const { container } = render(
      <RepTrendChart
        calls={[
          { id: "hs-0001", rep_id: "rep-01", customer_name: "Pat", vertical: "home_services", date: "2026-05-02", overall_score: 60 },
          { id: "hs-0002", rep_id: "rep-01", customer_name: "Sam", vertical: "home_services", date: "2026-05-05", overall_score: 80 },
        ]}
      />
    );

    expect(container.querySelector("svg")).not.toBeNull();
  });
});
