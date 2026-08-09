import type { ReactNode } from "react";
import { WeekNavigator } from "@/components/navigation/WeekNavigator";
import { useSidecarHealth } from "@/hooks/useSidecarHealth";
import { useWorkspace, type WorkspaceView } from "@/state/workspace";
import { DashboardView } from "@/features/dashboard/DashboardView";
import { SessionsView } from "@/features/sessions/SessionsView";
import { ProjectsView } from "@/features/projects/ProjectsView";
import { MilestonesView } from "@/features/milestones/MilestonesView";
import { ReviewsView } from "@/features/reviews/ReviewsView";
import { SettingsView } from "@/features/settings/SettingsView";

// Line icons for each tab (Lucide-style, per the Modernist prototype).
const ICONS: Record<WorkspaceView, ReactNode> = {
  dashboard: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="3" width="7" height="9" /><rect x="14" y="3" width="7" height="5" />
      <rect x="14" y="12" width="7" height="9" /><rect x="3" y="16" width="7" height="5" />
    </svg>
  ),
  sessions: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="9" /><path d="M12 7v5l4 2" />
    </svg>
  ),
  projects: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 6a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z" />
    </svg>
  ),
  milestones: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M5 3v18" /><path d="M5 4h11l-2 4 2 4H5" />
    </svg>
  ),
  reviews: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="6" y="4" width="12" height="17" rx="1" />
      <path d="M9 4V3a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1" /><path d="m9 13 2 2 4-4" />
    </svg>
  ),
  settings: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="3" />
      <path d="M12 2v3M12 19v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2 12h3M19 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1" />
    </svg>
  ),
};

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

  const sidecarCls =
    state === "ready" ? "tag tag-neutral" : state === "failed" ? "tag tag-accent" : "tag tag-outline";

  return (
    <div className="app-shell">
      <header className="app-header">
        <span className="brand-mark" aria-hidden="true" />
        <span className="brand">Portfolio Manager</span>
        <span className="spacer" />
        <span className={sidecarCls} aria-label={`Sidecar ${state}`} title={`Sidecar ${state}`}>
          Sidecar {state}
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
            {ICONS[tab.id]}
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
