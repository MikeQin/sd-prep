import React from "react";
import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RepCallsList } from "./RepCallsList";

describe("RepCallsList", () => {
  it("links each call to its call detail page", () => {
    render(
      <RepCallsList
        calls={[
          { id: "hs-0001", rep_id: "rep-01", customer_name: "Pat Romero", vertical: "home_services", date: "2026-05-02", overall_score: 82 },
        ]}
      />
    );

    const link = screen.getByRole("link", { name: /hs-0001/ });
    expect(link).toHaveAttribute("href", "/calls/hs-0001");
  });
});
