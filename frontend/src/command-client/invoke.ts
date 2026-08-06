// Thin wrapper around Tauri's invoke that normalizes errors to CommandError.
//
// This is the ONLY module permitted to import the Tauri invoke API. All feature
// code calls the typed functions in the sibling modules, never invoke directly,
// and never performs HTTP — enforced by scripts/verify_no_renderer_http.py.

import { invoke as tauriInvoke } from "@tauri-apps/api/core";
import { toCommandError } from "./errors";

/** Invoke a Tauri command, converting failures to {@link CommandError}. */
export async function invoke<T>(
  command: string,
  args?: Record<string, unknown>,
): Promise<T> {
  try {
    return await tauriInvoke<T>(command, args);
  } catch (err) {
    throw toCommandError(err);
  }
}
