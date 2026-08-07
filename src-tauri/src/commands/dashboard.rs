//! Dashboard command.

use crate::app_state::AppState;
use crate::errors::CommandError;
use crate::http::forwarder;
use serde_json::Value;
use tauri::State;

/// `GET /api/v1/dashboard` — aggregate dashboard for a week.
#[tauri::command]
pub async fn dashboard_get(
    state: State<'_, AppState>,
    week_key: Option<String>,
) -> Result<Value, CommandError> {
    let path = match week_key {
        Some(wk) => format!("/api/v1/dashboard?week_key={wk}"),
        None => "/api/v1/dashboard".to_string(),
    };
    forwarder::get(&state, &path).await
}
