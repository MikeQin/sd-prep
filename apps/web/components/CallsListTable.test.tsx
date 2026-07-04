import React from "react";
import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CallsListTable } from "./CallsListTable";

describe("CallsListTable", () => {
  it("links each row to its call detail page", () => {
    render(
      <CallsListTable
        calls={[
          { id: "hs-0001", rep_id: "rep-01", customer_name: "Pat Romero", vertical: "home_services", date: "2026-05-02", overall_score: 82 },
          { id: "al-0001", rep_id: "rep-04", customer_name: "Sam Osei", vertical: "apartment_leasing", date: "2026-05-03", overall_score: 65 },
        ]}
      />
    );

    expect(screen.getByRole("link", { name: /hs-0001/ })).toHaveAttribute("href", "/calls/hs-0001");
    expect(screen.getByRole("link", { name: /al-0001/ })).toHaveAttribute("href", "/calls/al-0001");
  });
});
