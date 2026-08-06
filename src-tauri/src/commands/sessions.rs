//! Session commands.

use crate::app_state::AppState;
use crate::errors::CommandError;
use crate::http::forwarder;
use reqwest::Method;
use serde_json::Value;
use tauri::State;

/// `GET /api/v1/sessions?week_key=...` — sessions for a week.
#[tauri::command]
pub async fn sessions_for_week(
    state: State<'_, AppState>,
    week_key: String,
) -> Result<Value, CommandError> {
    forwarder::get(&state, &format!("/api/v1/sessions?week_key={week_key}")).await
}

/// `POST /api/v1/sessions` — create a session.
#[tauri::command]
pub async fn session_create(
    state: State<'_, AppState>,
    payload: Value,
) -> Result<Value, CommandError> {
    forwarder::forward(&state, Method::POST, "/api/v1/sessions", Some(&payload)).await
}

/// `PUT /api/v1/sessions/{id}` — update a session.
#[tauri::command]
pub async fn session_update(
    state: State<'_, AppState>,
    session_id: i64,
    payload: Value,
) -> Result<Value, CommandError> {
    forwarder::forward(
        &state,
        Method::PUT,
        &format!("/api/v1/sessions/{session_id}"),
        Some(&payload),
    )
    .await
}

/// `POST /api/v1/sessions/{id}/status` — transition status.
#[tauri::command]
pub async fn session_set_status(
    state: State<'_, AppState>,
    session_id: i64,
    payload: Value,
) -> Result<Value, CommandError> {
    forwarder::forward(
        &state,
        Method::POST,
        &format!("/api/v1/sessions/{session_id}/status"),
        Some(&payload),
    )
    .await
}

/// `POST /api/v1/sessions/{id}/reschedule` — reschedule a session.
#[tauri::command]
pub async fn session_reschedule(
    state: State<'_, AppState>,
    session_id: i64,
    payload: Value,
) -> Result<Value, CommandError> {
    forwarder::forward(
        &state,
        Method::POST,
        &format!("/api/v1/sessions/{session_id}/reschedule"),
        Some(&payload),
    )
    .await
}

/// `DELETE /api/v1/sessions/{id}` — delete a session.
#[tauri::command]
pub async fn session_delete(
    state: State<'_, AppState>,
    session_id: i64,
) -> Result<Value, CommandError> {
    forwarder::forward::<(), Value>(
        &state,
        Method::DELETE,
        &format!("/api/v1/sessions/{session_id}"),
        None,
    )
    .await
}
