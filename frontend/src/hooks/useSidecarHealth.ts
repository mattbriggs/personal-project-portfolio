import { useQuery } from "@tanstack/react-query";
import { health } from "@/command-client";
import type { SidecarState } from "@/contracts";

/**
 * Poll the supervisor lifecycle state so the shell can show a degraded banner
 * and disable write actions when the sidecar is not ready.
 */
export function useSidecarHealth() {
  const query = useQuery<SidecarState>({
    queryKey: ["sidecar", "state"],
    queryFn: () => health.state(),
    refetchInterval: 4000,
    retry: false,
  });
  const state = query.data ?? "starting";
  return {
    state,
    isReady: state === "ready",
    isDegraded: state === "failed" || state === "degraded" || state === "stopped",
  };
}
