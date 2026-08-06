import { WeekNavigator } from "@/components/navigation/WeekNavigator";
import { useSidecarHealth } from "@/hooks/useSidecarHealth";
import { useWorkspace, type WorkspaceView } from "@/state/workspace";
import { DashboardView } from "@/features/dashboard/DashboardView";
import { SessionsView } from "@/features/sessions/SessionsView";
import { ProjectsView } from "@/features/projects/ProjectsView";
import { MilestonesView } from "@/features/milestones/MilestonesView";
import { ReviewsView } from "@/features/reviews/ReviewsView";
import { SettingsView } from "@/features/settings/SettingsView";

const TABS: { id: WorkspaceView; label: string }[] = [
  { id: "dashboard", label: "Dashboard" },
  { id: "sessions", label: "Sessions" },
  { id: "projects", label: "Projects" },
  { id: "milestones", label: "Milestones" },
  { id: "reviews", label: "Weekly Review" },
  { id: "settings", label: "Settings" },
];

function ViewSwitch({ view }: { view: WorkspaceView }) {
  switch (view) {
    case "dashboard":
      return <DashboardView />;
    case "sessions":
      return <SessionsView />;
    case "projects":
      return <ProjectsView />;
    case "milestones":
      return <MilestonesView />;
    case "reviews":
      return <ReviewsView />;
    case "settings":
      return <SettingsView />;
  }
}

export function AppShell() {
  const { view, setView } = useWorkspace();
  const { state, isDegraded } = useSidecarHealth();

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>Portfolio Manager</h1>
        <span aria-label={`Sidecar ${state}`} title={`Sidecar ${state}`}>
          <span
            className={`status-dot status-${state === "ready" ? "green" : state === "failed" ? "red" : "yellow"}`}
            aria-hidden="true"
          />{" "}
          {state}
        </span>
      </header>

      {isDegraded && (
        <div className="banner" role="alert">
          The backend is unavailable. Data may be stale and changes are disabled.
          Check the log file in <code>~/.portfolio_manager/logs</code>, then retry.
        </div>
      )}

      <div className="tabs" role="tablist">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            role="tab"
            className="tab-btn"
            aria-current={view === tab.id}
            onClick={() => setView(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="app-body">
        <WeekNavigator />
        <main className="main-view">
          <ViewSwitch view={view} />
        </main>
      </div>
    </div>
  );
}
