import type { ProjectScore, ScoreStatus } from "@/contracts";
import { invoke } from "./invoke";

export interface ScoreOverride {
  project_id: number;
  week_key: string;
  score: number;
  status: ScoreStatus;
  reason: string;
  status_note?: string;
}

export function override(payload: ScoreOverride): Promise<ProjectScore> {
  return invoke("score_override", { payload });
}
