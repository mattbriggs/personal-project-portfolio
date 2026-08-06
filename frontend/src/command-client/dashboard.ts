import type { Dashboard } from "@/contracts";
import { invoke } from "./invoke";

/** Aggregate dashboard for a week (defaults to current week when omitted). */
export function get(weekKey?: string): Promise<Dashboard> {
  return invoke("dashboard_get", { weekKey });
}
