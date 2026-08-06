//! Milestone commands.

use crate::app_state::AppState;
use crate::errors::CommandError;
use crate::http::forwarder;
use reqwest::Method;
use serde_json::Value;
use tauri::State;

/// `GET /api/v1/projects/{id}/milestones` — milestones for a project.
#[tauri::command]
pub async fn milestones_for_project(
    state: State<'_, AppState>,
    project_id: i64,
) -> Result<Value, CommandError> {
    forwarder::get(&state, &format!("/api/v1/projects/{project_id}/milestones")).await
}

/// `POST /api/v1/milestones` — create a milestone.
#[tauri::command]
pub async fn milestone_create(
    state: State<'_, AppState>,
    payload: Value,
) -> Result<Value, CommandError> {
    forwarder::forward(&state, Method::POST, "/api/v1/milestones", Some(&payload)).await
}

/// `PUT /api/v1/milestones/{id}` — update a milestone.
#[tauri::command]
pub async fn milestone_update(
    state: State<'_, AppState>,
    milestone_id: i64,
    payload: Value,
) -> Result<Value, CommandError> {
    forwarder::forward(
        &state,
        Method::PUT,
        &format!("/api/v1/milestones/{milestone_id}"),
        Some(&payload),
    )
    .await
}

/// `POST /api/v1/milestones/{id}/status` — transition status.
#[tauri::command]
pub async fn milestone_set_status(
    state: State<'_, AppState>,
    milestone_id: i64,
    payload: Value,
) -> Result<Value, CommandError> {
    forwarder::forward(
        &state,
        Method::POST,
        &format!("/api/v1/milestones/{milestone_id}/status"),
        Some(&payload),
    )
    .await
}

/// `DELETE /api/v1/milestones/{id}` — delete a milestone.
#[tauri::command]
pub async fn milestone_delete(
    state: State<'_, AppState>,
    milestone_id: i64,
) -> Result<Value, CommandError> {
    forwarder::forward::<(), Value>(
        &state,
        Method::DELETE,
        &format!("/api/v1/milestones/{milestone_id}"),
        None,
    )
    .await
}
