//! Project and plan commands.

use crate::app_state::AppState;
use crate::errors::CommandError;
use crate::http::forwarder;
use reqwest::Method;
use serde_json::Value;
use tauri::State;

/// `GET /api/v1/projects` — list projects (optional status filter).
#[tauri::command]
pub async fn projects_list(
    state: State<'_, AppState>,
    status: Option<String>,
) -> Result<Value, CommandError> {
    let path = match status {
        Some(s) => format!("/api/v1/projects?status={s}"),
        None => "/api/v1/projects".to_string(),
    };
    forwarder::get(&state, &path).await
}

/// `GET /api/v1/projects/{id}` — fetch a project.
#[tauri::command]
pub async fn project_get(
    state: State<'_, AppState>,
    project_id: i64,
) -> Result<Value, CommandError> {
    forwarder::get(&state, &format!("/api/v1/projects/{project_id}")).await
}

/// `POST /api/v1/projects` — create a project.
#[tauri::command]
pub async fn project_create(
    state: State<'_, AppState>,
    payload: Value,
) -> Result<Value, CommandError> {
    forwarder::forward(&state, Method::POST, "/api/v1/projects", Some(&payload)).await
}

/// `PUT /api/v1/projects/{id}` — update a project.
#[tauri::command]
pub async fn project_update(
    state: State<'_, AppState>,
    project_id: i64,
    payload: Value,
) -> Result<Value, CommandError> {
    forwarder::forward(
        &state,
        Method::PUT,
        &format!("/api/v1/projects/{project_id}"),
        Some(&payload),
    )
    .await
}

/// `POST /api/v1/projects/{id}/archive` — archive a project.
#[tauri::command]
pub async fn project_archive(
    state: State<'_, AppState>,
    project_id: i64,
) -> Result<Value, CommandError> {
    forwarder::forward::<(), Value>(
        &state,
        Method::POST,
        &format!("/api/v1/projects/{project_id}/archive"),
        None,
    )
    .await
}

/// `DELETE /api/v1/projects/{id}` — permanently delete a project.
#[tauri::command]
pub async fn project_delete(
    state: State<'_, AppState>,
    project_id: i64,
) -> Result<Value, CommandError> {
    forwarder::forward::<(), Value>(
        &state,
        Method::DELETE,
        &format!("/api/v1/projects/{project_id}"),
        None,
    )
    .await
}

/// `GET /api/v1/projects/{id}/plan` — fetch plan Markdown.
#[tauri::command]
pub async fn project_plan_get(
    state: State<'_, AppState>,
    project_id: i64,
) -> Result<Value, CommandError> {
    forwarder::get(&state, &format!("/api/v1/projects/{project_id}/plan")).await
}

/// `PUT /api/v1/projects/{id}/plan` — save plan Markdown.
#[tauri::command]
pub async fn project_plan_save(
    state: State<'_, AppState>,
    project_id: i64,
    payload: Value,
) -> Result<Value, CommandError> {
    forwarder::forward(
        &state,
        Method::PUT,
        &format!("/api/v1/projects/{project_id}/plan"),
        Some(&payload),
    )
    .await
}
