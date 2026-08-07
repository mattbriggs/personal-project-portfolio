import type { SidecarState } from "@/contracts";
import { invoke } from "./invoke";

/** `GET /health` via the `sidecar_health` command. */
export function health(): Promise<{ status: string }> {
  return invoke("sidecar_health");
}

/** Current supervisor lifecycle state (no network call). */
export function state(): Promise<SidecarState> {
  return invoke("sidecar_state");
}
