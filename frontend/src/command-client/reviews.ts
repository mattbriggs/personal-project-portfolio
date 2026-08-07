import type { ReviewListResponse, WeeklyReview } from "@/contracts";
import { invoke } from "./invoke";

export interface ReviewSave {
  hours_invested?: number;
  sessions_completed?: number;
  what_moved?: string;
  what_stalled?: string;
  signals?: string;
  decision_next_week?: string;
  primary_focus?: string;
  project_to_deprioritize?: string;
  risk_to_watch?: string;
  first_session_target?: string;
  written_to_repo?: boolean;
}

export function list(): Promise<ReviewListResponse> {
  return invoke("reviews_list");
}

export function getOrCreate(weekKey: string): Promise<WeeklyReview> {
  return invoke("review_get_or_create", { weekKey });
}

export function save(weekKey: string, payload: ReviewSave): Promise<WeeklyReview> {
  return invoke("review_save", { weekKey, payload });
}
