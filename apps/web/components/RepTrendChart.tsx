"use client";

import React from "react";
import { CartesianGrid, Line, LineChart, Tooltip, XAxis, YAxis } from "recharts";
import type { CallSummary } from "../lib/types";

// Assumes `calls` arrives pre-sorted by date, as GET /api/reps/{id} returns.
export function RepTrendChart({ calls }: { calls: CallSummary[] }) {
  const data = calls.map((call) => ({ date: call.date, score: call.overall_score }));

  return (
    <LineChart width={600} height={300} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="date" />
      <YAxis domain={[0, 100]} />
      <Tooltip />
      <Line type="monotone" dataKey="score" stroke="#2563eb" />
    </LineChart>
  );
}
