//! Health command and sidecar state query.

use crate::app_state::AppState;
use crate::errors::CommandError;
use crate::http::forwarder;
use crate::sidecar::supervisor::SidecarState;
use serde_json::Value;
use tauri::State;

/// `GET /health` — sidecar liveness probe.
#[tauri::command]
pub async fn sidecar_health(state: State<'_, AppState>) -> Result<Value, CommandError> {
    forwarder::get(&state, "/health").await
}

/// Return the current supervisor lifecycle state (no network call).
#[tauri::command]
pub async fn sidecar_state(state: State<'_, AppState>) -> Result<SidecarState, CommandError> {
    Ok(state.current_state())
}
