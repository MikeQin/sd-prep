import React from "react";
import Link from "next/link";
import type { CallSummary } from "../lib/types";

export function RepCallsList({ calls }: { calls: CallSummary[] }) {
  return (
    <ul aria-label="rep-calls">
      {calls.map((call) => (
        <li key={call.id}>
          <Link href={`/calls/${call.id}`}>
            {call.date} - {call.id} - {call.overall_score.toFixed(1)}
          </Link>
        </li>
      ))}
    </ul>
  );
}
