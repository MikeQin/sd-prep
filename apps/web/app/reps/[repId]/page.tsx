import React from "react";
import Link from "next/link";
import { fetchRep } from "../../../lib/api";
import { RepTrendChart } from "../../../components/RepTrendChart";
import { RepCallsList } from "../../../components/RepCallsList";

export default async function RepProfilePage({ params }: { params: { repId: string } }) {
  const rep = await fetchRep(params.repId);
  return (
    <main>
      <Link href="/">Back to leaderboard</Link>
      <h1>{rep.name}</h1>
      <p>Vertical: {rep.vertical}</p>
      <RepTrendChart calls={rep.calls} />
      <RepCallsList calls={rep.calls} />
    </main>
  );
}
