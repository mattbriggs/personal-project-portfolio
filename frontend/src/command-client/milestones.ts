import type { Milestone, MilestoneListResponse, MilestoneStatus } from "@/contracts";
import { invoke } from "./invoke";

export interface MilestoneCreate {
  project_id: number;
  description: string;
  status?: MilestoneStatus;
  target_date?: string | null;
  sort_order?: number;
  notes?: string;
}

export interface MilestoneUpdate {
  description: string;
  status: MilestoneStatus;
  target_date?: string | null;
  sort_order?: number;
  notes?: string;
}

export function forProject(projectId: number): Promise<MilestoneListResponse> {
  return invoke("milestones_for_project", { projectId });
}

export function create(payload: MilestoneCreate): Promise<Milestone> {
  return invoke("milestone_create", { payload });
}

export function update(milestoneId: number, payload: MilestoneUpdate): Promise<Milestone> {
  return invoke("milestone_update", { milestoneId, payload });
}

export function setStatus(
  milestoneId: number,
  status: MilestoneStatus,
): Promise<Milestone> {
  return invoke("milestone_set_status", { milestoneId, payload: { status } });
}

export function remove(milestoneId: number): Promise<{ ok: boolean }> {
  return invoke("milestone_delete", { milestoneId });
}
