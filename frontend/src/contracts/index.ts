// Renderer-facing contract types.
//
// These mirror the backend Pydantic contracts. `scripts/generate_openapi.py`
// emits `./generated/types.ts` from the live OpenAPI schema; a CI drift check
// keeps these in sync. They are hand-authored here so the renderer type-checks
// without requiring the generated file to be present during development.

export type ProjectStatus = "active" | "backlog" | "archive";
export type SessionStatus =
  | "backlog"
  | "planned"
  | "doing"
  | "done"
  | "cancelled";
export type MilestoneStatus = SessionStatus;
export type ScoreStatus = "green" | "yellow" | "red";

export interface Project {
  id: number;
  name: string;
  slug: string;
  status: ProjectStatus;
  priority: number;
  started_date: string | null;
  end_date: string | null;
  owner: string;
  review_cadence: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectListResponse {
  projects: Project[];
}

export interface Session {
  id: number;
  project_id: number;
  milestone_id: number | null;
  scheduled_date: string;
  week_key: string;
  duration_minutes: number;
  status: SessionStatus;
  description: string;
  notes: string;
  created_at: string;
  completed_at: string | null;
}

export interface SessionListResponse {
  sessions: Session[];
}

export interface Milestone {
  id: number;
  project_id: number;
  description: string;
  status: MilestoneStatus;
  completed_date: string | null;
  target_date: string | null;
  sort_order: number;
  notes: string;
  total_session_minutes: number;
  created_at: string;
  updated_at: string;
}

export interface MilestoneListResponse {
  milestones: Milestone[];
}

export interface ProjectScore {
  id: number;
  project_id: number;
  week_key: string;
  score: number;
  status: ScoreStatus;
  status_note: string;
  is_manual_override: boolean;
  override_reason: string;
  created_at: string | null;
}

export interface WeeklyReview {
  id: number;
  week_key: string;
  date_from: string | null;
  date_to: string | null;
  hours_invested: number;
  sessions_completed: number;
  what_moved: string;
  what_stalled: string;
  signals: string;
  decision_next_week: string;
  primary_focus: string;
  project_to_deprioritize: string;
  risk_to_watch: string;
  first_session_target: string;
  written_to_repo: boolean;
  created_at: string | null;
  updated_at: string | null;
}

export interface ReviewListResponse {
  reviews: WeeklyReview[];
}

export interface DashboardRow {
  project: Project;
  score: ProjectScore;
  planned: number;
  completed: number;
  remaining: number;
}

export interface UpcomingMilestone {
  project_name: string;
  description: string;
  target_date: string;
}

export interface Dashboard {
  week_key: string;
  date_range: string;
  rows: DashboardRow[];
  portfolio_score: number;
  portfolio_status: ScoreStatus;
  week_total_minutes: number;
  week_done_minutes: number;
  week_remaining_minutes: number;
  budget_minutes: number;
  upcoming_milestones: UpcomingMilestone[];
}

export interface Settings {
  log_level: string;
  theme: string;
  default_duration_minutes: number;
  weekly_budget_hours: number;
  database_path: string;
  resolved_database_path: string;
  active_database_path: string;
}

export interface PlanResponse {
  project_id: number;
  content: string;
}

export type SidecarState =
  | "not_started"
  | "starting"
  | "ready"
  | "degraded"
  | "stopping"
  | "stopped"
  | "failed";
