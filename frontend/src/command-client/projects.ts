import type {
  PlanResponse,
  Project,
  ProjectListResponse,
  ProjectStatus,
} from "@/contracts";
import { invoke } from "./invoke";

export interface ProjectCreate {
  name: string;
  status?: ProjectStatus;
  priority?: number;
  description?: string;
  started_date?: string | null;
  end_date?: string | null;
}

export interface ProjectUpdate {
  name: string;
  status: ProjectStatus;
  priority: number;
  description?: string;
  started_date?: string | null;
  end_date?: string | null;
}

export function list(status?: ProjectStatus): Promise<ProjectListResponse> {
  return invoke("projects_list", { status });
}

export function get(projectId: number): Promise<Project> {
  return invoke("project_get", { projectId });
}

export function create(payload: ProjectCreate): Promise<Project> {
  return invoke("project_create", { payload });
}

export function update(projectId: number, payload: ProjectUpdate): Promise<Project> {
  return invoke("project_update", { projectId, payload });
}

export function archive(projectId: number): Promise<Project> {
  return invoke("project_archive", { projectId });
}

export function remove(projectId: number): Promise<{ ok: boolean }> {
  return invoke("project_delete", { projectId });
}

export function getPlan(projectId: number): Promise<PlanResponse> {
  return invoke("project_plan_get", { projectId });
}

export function savePlan(projectId: number, content: string): Promise<PlanResponse> {
  return invoke("project_plan_save", { projectId, payload: { content } });
}
