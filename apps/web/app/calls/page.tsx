import React from "react";
import Link from "next/link";
import { fetchCalls } from "../../lib/api";
import { CallsListTable } from "../../components/CallsListTable";

export default async function CallsListPage() {
  const calls = await fetchCalls();
  return (
    <main>
      <Link href="/">Back to leaderboard</Link>
      <h1>All Calls</h1>
      <CallsListTable calls={calls} />
    </main>
  );
}
