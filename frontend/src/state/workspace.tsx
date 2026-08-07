// Workspace state: selected week and active view. Not persisted between
// launches (SRS leaves this unspecified; current behavior does not persist).

import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import { currentWeekKey } from "@/utils/week";

export type WorkspaceView =
  | "dashboard"
  | "sessions"
  | "projects"
  | "milestones"
  | "reviews"
  | "settings";

interface WorkspaceContextValue {
  view: WorkspaceView;
  setView: (v: WorkspaceView) => void;
  selectedWeek: string;
  setSelectedWeek: (wk: string) => void;
}

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const [view, setView] = useState<WorkspaceView>("dashboard");
  const [selectedWeek, setSelectedWeek] = useState<string>(currentWeekKey());
  const value = useMemo(
    () => ({ view, setView, selectedWeek, setSelectedWeek }),
    [view, selectedWeek],
  );
  return (
    <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>
  );
}

export function useWorkspace(): WorkspaceContextValue {
  const ctx = useContext(WorkspaceContext);
  if (!ctx) throw new Error("useWorkspace must be used within WorkspaceProvider");
  return ctx;
}
