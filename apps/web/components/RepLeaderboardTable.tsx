import React from "react";
import type { RepSummary } from "../lib/types";

export function RepLeaderboardTable({ reps }: { reps: RepSummary[] }) {
  const sorted = [...reps].sort((a, b) => b.average_score - a.average_score);
  return (
    <table>
      <thead>
        <tr>
          <th>Rep</th>
          <th>Vertical</th>
          <th>Calls</th>
          <th>Avg Score</th>
        </tr>
      </thead>
      <tbody>
        {sorted.map((rep) => (
          <tr key={rep.id}>
            <td>{rep.name}</td>
            <td>{rep.vertical}</td>
            <td>{rep.call_count}</td>
            <td>{rep.average_score.toFixed(1)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
