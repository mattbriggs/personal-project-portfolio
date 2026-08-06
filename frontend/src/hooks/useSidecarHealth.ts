import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";
import { health } from "@/command-client";
import type { SidecarState } from "@/contracts";

/**
 * Poll the supervisor lifecycle state so the shell can show a degraded banner
 * and disable write actions when the sidecar is not ready.
 *
 * Also refetches every query when the sidecar becomes ready. The window opens
 * as soon as the shell starts, but the frozen Python sidecar needs several
 * seconds to boot, so the first render's queries can fire before anything is
 * listening. Those fail with `SIDECAR_UNAVAILABLE`, and because the query
 * client sets `retry: false` they would otherwise stay failed for the life of
 * the window, leaving the user staring at an error on every cold start.
 */
export function useSidecarHealth() {
  const queryClient = useQueryClient();
  const query = useQuery<SidecarState>({
    queryKey: ["sidecar", "state"],
    queryFn: () => health.state(),
    refetchInterval: 4000,
    retry: false,
  });
  const state = query.data ?? "starting";

  // Tracks the previous readiness so the refetch fires on the transition into
  // "ready" rather than on every poll, and re-arms if the sidecar drops out.
  const wasReady = useRef(false);
  useEffect(() => {
    const isReady = state === "ready";
    if (isReady && !wasReady.current) {
      void queryClient.invalidateQueries();
    }
    wasReady.current = isReady;
  }, [state, queryClient]);

  return {
    state,
    isReady: state === "ready",
    isDegraded: state === "failed" || state === "degraded" || state === "stopped",
  };
}
