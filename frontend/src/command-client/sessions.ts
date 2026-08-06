import type { Session, SessionListResponse, SessionStatus } from "@/contracts";
import { invoke } from "./invoke";

export interface SessionCreate {
  project_id: number;
  milestone_id?: number | null;
  scheduled_date: string;
  duration_minutes?: number | null;
  status?: SessionStatus;
  description?: string;
  notes?: string;
}

export interface SessionUpdate {
  project_id: number;
  milestone_id?: number | null;
  scheduled_date: string;
  duration_minutes: number;
  status: SessionStatus;
  description?: string;
  notes?: string;
}

export function forWeek(weekKey: string): Promise<SessionListResponse> {
  return invoke("sessions_for_week", { weekKey });
}

export function create(payload: SessionCreate): Promise<Session> {
  return invoke("session_create", { payload });
}

export function update(sessionId: number, payload: SessionUpdate): Promise<Session> {
  return invoke("session_update", { sessionId, payload });
}

export function setStatus(sessionId: number, status: SessionStatus): Promise<Session> {
  return invoke("session_set_status", { sessionId, payload: { status } });
}

export function reschedule(sessionId: number, scheduledDate: string): Promise<Session> {
  return invoke("session_reschedule", {
    sessionId,
    payload: { scheduled_date: scheduledDate },
  });
}

export function remove(sessionId: number): Promise<{ ok: boolean }> {
  return invoke("session_delete", { sessionId });
}
