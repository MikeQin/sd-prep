import React from "react";
import Link from "next/link";
import type { CallSummary } from "../lib/types";

export function CallsListTable({ calls }: { calls: CallSummary[] }) {
  return (
    <table>
      <thead>
        <tr>
          <th>Call</th>
          <th>Customer</th>
          <th>Vertical</th>
          <th>Date</th>
          <th>Score</th>
        </tr>
      </thead>
      <tbody>
        {calls.map((call) => (
          <tr key={call.id}>
            <td>
              <Link href={`/calls/${call.id}`}>{call.id}</Link>
            </td>
            <td>{call.customer_name}</td>
            <td>{call.vertical}</td>
            <td>{call.date}</td>
            <td>{call.overall_score.toFixed(1)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
