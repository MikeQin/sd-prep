import { fetchReps } from "../lib/api";
import { RepLeaderboardTable } from "../components/RepLeaderboardTable";

export default async function DashboardPage() {
  const reps = await fetchReps();
  return (
    <main>
      <h1>Rep Leaderboard</h1>
      <RepLeaderboardTable reps={reps} />
    </main>
  );
}
