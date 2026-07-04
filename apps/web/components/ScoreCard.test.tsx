import React from "react";
import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ScoreCard } from "./ScoreCard";

describe("ScoreCard", () => {
  it("renders coaching flags when present", () => {
    render(
      <ScoreCard
        score={{
          talk_listen_ratio: 3.1,
          objection_raised: true,
          objection_handled_well: false,
          pricing_discussed: true,
          next_step_committed: false,
          sentiment_score: -0.2,
          overall_score: 45.2,
          flags: ["objection_not_handled", "no_next_step_commitment"],
        }}
      />
    );

    expect(screen.getByLabelText("coaching-flags")).toHaveTextContent("objection_not_handled");
    expect(screen.getByText("Overall score: 45.2")).toBeInTheDocument();
  });
});
