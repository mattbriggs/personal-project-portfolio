//! Score commands.

use crate::app_state::AppState;
use crate::errors::CommandError;
use crate::http::forwarder;
use reqwest::Method;
use serde_json::Value;
use tauri::State;

/// `POST /api/v1/scores/override` — manual score override.
#[tauri::command]
pub async fn score_override(
    state: State<'_, AppState>,
    payload: Value,
) -> Result<Value, CommandError> {
    forwarder::forward(
        &state,
        Method::POST,
        "/api/v1/scores/override",
        Some(&payload),
    )
    .await
}
