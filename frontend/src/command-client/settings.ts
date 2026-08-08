import type { Settings } from "@/contracts";
import { invoke } from "./invoke";

export interface SettingsUpdate {
  log_level: string;
  theme: string;
  default_duration_minutes: number;
  weekly_budget_hours: number;
  database_path: string;
}

export function get(): Promise<Settings> {
  return invoke("settings_get");
}

export function update(payload: SettingsUpdate): Promise<Settings> {
  return invoke("settings_update", { payload });
}
