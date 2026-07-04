import React from "react";
import Link from "next/link";
import { fetchCall } from "../../../lib/api";
import { ScoreCard } from "../../../components/ScoreCard";

export default async function CallDetailPage({ params }: { params: { callId: string } }) {
  const call = await fetchCall(params.callId);
  return (
    <main>
      <Link href={`/reps/${call.rep_id}`}>Back to rep profile</Link>
      <h1>Call {call.id} - {call.customer_name}</h1>
      <ScoreCard score={call.score} />
      <ol aria-label="transcript">
        {call.turns.map((turn, index) => (
          <li key={index}>
            <strong>{turn.speaker}:</strong> {turn.text}
          </li>
        ))}
      </ol>
    </main>
  );
}
