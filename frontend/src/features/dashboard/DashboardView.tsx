import { useQuery } from "@tanstack/react-query";
import { dashboard } from "@/command-client";
import type { Dashboard } from "@/contracts";
import { StatusIndicator } from "@/components/status/StatusIndicator";
import { useWorkspace } from "@/state/workspace";

function hours(minutes: number): string {
  return `${(minutes / 60).toFixed(1)}h`;
}

export function DashboardView() {
  const { selectedWeek } = useWorkspace();
  const { data, isLoading, isError, error } = useQuery<Dashboard>({
    queryKey: ["dashboard", selectedWeek],
    queryFn: () => dashboard.get(selectedWeek),
  });

  if (isLoading) return <p>Loading dashboard…</p>;
  if (isError) return <p role="alert">Could not load dashboard: {String(error)}</p>;
  if (!data) return null;

  return (
    <section aria-label="Dashboard">
      <h2>
        Dashboard — {data.week_key} <small>({data.date_range})</small>
      </h2>

      <p>
        <strong>Portfolio score: {data.portfolio_score}</strong>{" "}
        <StatusIndicator status={data.portfolio_status} />
      </p>
      <p>
        Weekly budget: {hours(data.week_done_minutes)} done /{" "}
        {hours(data.week_total_minutes)} planned of {hours(data.budget_minutes)} budget
        ({hours(data.week_remaining_minutes)} remaining)
      </p>

      <h3>Active projects</h3>
      <table>
        <thead>
          <tr>
            <th>Project</th>
            <th>Score</th>
            <th>Status</th>
            <th>Planned</th>
            <th>Done</th>
            <th>Remaining</th>
          </tr>
        </thead>
        <tbody>
          {data.rows.map((row) => (
            <tr key={row.project.id}>
              <td>{row.project.name}</td>
              <td>{row.score.score}</td>
              <td>
                <StatusIndicator status={row.score.status} />
              </td>
              <td>{row.planned}</td>
              <td>{row.completed}</td>
              <td>{row.remaining}</td>
            </tr>
          ))}
          {data.rows.length === 0 && (
            <tr>
              <td colSpan={6}>No active projects.</td>
            </tr>
          )}
        </tbody>
      </table>

      <h3>Upcoming milestones</h3>
      <ul>
        {data.upcoming_milestones.map((m, i) => (
          <li key={i}>
            {m.target_date} — <strong>{m.project_name}</strong>: {m.description}
          </li>
        ))}
        {data.upcoming_milestones.length === 0 && <li>No upcoming milestones.</li>}
      </ul>
    </section>
  );
}
