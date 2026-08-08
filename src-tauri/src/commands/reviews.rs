//! Weekly review commands.

use crate::app_state::AppState;
use crate::errors::CommandError;
use crate::http::forwarder;
use reqwest::Method;
use serde_json::Value;
use tauri::State;

/// `GET /api/v1/reviews` — review history (most recent first).
#[tauri::command]
pub async fn reviews_list(state: State<'_, AppState>) -> Result<Value, CommandError> {
    forwarder::get(&state, "/api/v1/reviews").await
}

/// `GET /api/v1/reviews/{week_key}` — get-or-create a review.
#[tauri::command]
pub async fn review_get_or_create(
    state: State<'_, AppState>,
    week_key: String,
) -> Result<Value, CommandError> {
    forwarder::get(&state, &format!("/api/v1/reviews/{week_key}")).await
}

/// `PUT /api/v1/reviews/{week_key}` — save a review.
#[tauri::command]
pub async fn review_save(
    state: State<'_, AppState>,
    week_key: String,
    payload: Value,
) -> Result<Value, CommandError> {
    forwarder::forward(
        &state,
        Method::PUT,
        &format!("/api/v1/reviews/{week_key}"),
        Some(&payload),
    )
    .await
}
