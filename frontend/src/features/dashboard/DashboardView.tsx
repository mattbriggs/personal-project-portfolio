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
      <h2>Dashboard</h2>
      <p className="view-sub">
        {data.week_key} · {data.date_range}
      </p>

      <div className="stat-grid">
        <div className="card elev-sm">
          <span className="card-kicker">Portfolio score</span>
          <span className="card-title">{data.portfolio_score}</span>
          <span style={{ alignSelf: "flex-start" }}>
            <StatusIndicator status={data.portfolio_status} />
          </span>
        </div>
        <div className="card elev-sm">
          <span className="card-kicker">Weekly budget</span>
          <span className="card-title">
            {hours(data.week_done_minutes)} / {hours(data.budget_minutes)}
          </span>
          <span className="card-body">
            {hours(data.week_total_minutes)} planned · {hours(data.week_remaining_minutes)} remaining
          </span>
        </div>
        <div className="card elev-sm">
          <span className="card-kicker">Active projects</span>
          <span className="card-title">{data.rows.length}</span>
          <span className="card-body">tracked in {data.week_key}</span>
        </div>
      </div>

      <h3>Active projects</h3>
      <div className="table-scroll" style={{ marginBottom: "var(--space-8)" }}>
        <table className="table">
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
      </div>

      <h3>Upcoming milestones</h3>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {data.upcoming_milestones.map((m, i) => (
          <div
            key={i}
            style={{
              display: "flex",
              gap: 12,
              alignItems: "baseline",
              borderBottom: "1px solid var(--color-divider)",
              paddingBottom: 8,
            }}
          >
            <span className="tag tag-outline" style={{ flex: "none" }}>
              {m.target_date}
            </span>
            <span>
              <strong>{m.project_name}</strong> — {m.description}
            </span>
          </div>
        ))}
        {data.upcoming_milestones.length === 0 && (
          <p className="text-muted">No upcoming milestones.</p>
        )}
      </div>
    </section>
  );
}
