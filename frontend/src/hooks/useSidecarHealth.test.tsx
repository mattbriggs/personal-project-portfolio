import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

const state = vi.fn();
vi.mock("@/command-client", () => ({ health: { state: () => state() } }));

import { useSidecarHealth } from "./useSidecarHealth";

function wrapper(client: QueryClient) {
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
}

function makeClient() {
  return new QueryClient({
    defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } },
  });
}

describe("useSidecarHealth", () => {
  beforeEach(() => state.mockReset());

  it("reports degraded states", async () => {
    state.mockResolvedValue("failed");
    const client = makeClient();
    const { result } = renderHook(() => useSidecarHealth(), {
      wrapper: wrapper(client),
    });

    await waitFor(() => expect(result.current.state).toBe("failed"));
    expect(result.current.isDegraded).toBe(true);
    expect(result.current.isReady).toBe(false);
  });

  // The window opens before the frozen sidecar finishes booting, so the first
  // render's queries fail with retry disabled. Becoming ready must refetch them
  // or the user is stuck looking at an error until they restart the app.
  it("refetches every query when the sidecar becomes ready", async () => {
    state.mockResolvedValue("starting");
    const client = makeClient();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result, rerender } = renderHook(() => useSidecarHealth(), {
      wrapper: wrapper(client),
    });
    await waitFor(() => expect(result.current.state).toBe("starting"));
    expect(invalidate).not.toHaveBeenCalled();

    state.mockResolvedValue("ready");
    await client.refetchQueries({ queryKey: ["sidecar", "state"] });
    rerender();

    await waitFor(() => expect(result.current.isReady).toBe(true));
    expect(invalidate).toHaveBeenCalled();
  });

  it("does not refetch again while it stays ready", async () => {
    state.mockResolvedValue("ready");
    const client = makeClient();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { rerender, result } = renderHook(() => useSidecarHealth(), {
      wrapper: wrapper(client),
    });
    await waitFor(() => expect(result.current.isReady).toBe(true));
    const callsAfterFirstReady = invalidate.mock.calls.length;

    rerender();
    rerender();
    expect(invalidate.mock.calls.length).toBe(callsAfterFirstReady);
  });
});
