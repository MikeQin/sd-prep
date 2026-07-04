import React from "react";
import { fetchRep } from "../../../lib/api";
import { RepTrendChart } from "../../../components/RepTrendChart";

export default async function RepProfilePage({ params }: { params: { repId: string } }) {
  const rep = await fetchRep(params.repId);
  return (
    <main>
      <h1>{rep.name}</h1>
      <p>Vertical: {rep.vertical}</p>
      <RepTrendChart calls={rep.calls} />
    </main>
  );
}
