//! Settings commands.

use crate::app_state::AppState;
use crate::errors::CommandError;
use crate::http::forwarder;
use reqwest::Method;
use serde_json::Value;
use tauri::State;

/// `GET /api/v1/settings` — current settings.
#[tauri::command]
pub async fn settings_get(state: State<'_, AppState>) -> Result<Value, CommandError> {
    forwarder::get(&state, "/api/v1/settings").await
}

/// `PUT /api/v1/settings` — update settings.
#[tauri::command]
pub async fn settings_update(
    state: State<'_, AppState>,
    payload: Value,
) -> Result<Value, CommandError> {
    forwarder::forward(&state, Method::PUT, "/api/v1/settings", Some(&payload)).await
}
