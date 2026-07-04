import React from "react";
import type { ScoreOut } from "../lib/types";

export function ScoreCard({ score }: { score: ScoreOut }) {
  return (
    <section aria-label="scorecard">
      <p>Overall score: {score.overall_score.toFixed(1)}</p>
      <p>Talk/listen ratio: {score.talk_listen_ratio.toFixed(2)}</p>
      <p>Pricing discussed: {score.pricing_discussed ? "Yes" : "No"}</p>
      <p>Objection handled well: {score.objection_handled_well ? "Yes" : "No"}</p>
      <p>Next step committed: {score.next_step_committed ? "Yes" : "No"}</p>
      {score.flags.length > 0 && (
        <ul aria-label="coaching-flags">
          {score.flags.map((flag) => (
            <li key={flag}>{flag}</li>
          ))}
        </ul>
      )}
    </section>
  );
}
