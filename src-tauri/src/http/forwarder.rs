//! Generic authenticated forwarder.
//!
//! This is the single internal helper that attaches the `X-API-Key` token and
//! performs the request. It is **not** exposed to the renderer — only the
//! explicit, allowlisted commands in [`crate::commands`] call it, each mapping
//! one renderer operation to one fixed method and path.

use crate::app_state::AppState;
use crate::errors::CommandError;
use crate::http::response;
use reqwest::Method;
use serde::de::DeserializeOwned;
use serde::Serialize;

/// The header carrying the per-launch auth token.
pub const API_KEY_HEADER: &str = "X-API-Key";

/// Forward a request to the sidecar and parse the typed response.
///
/// # Arguments
/// * `state` - Runtime state providing the base URL, token, and HTTP client.
/// * `method` - HTTP method.
/// * `path` - Path beginning with `/` (e.g. `/api/v1/projects`).
/// * `body` - Optional JSON body.
///
/// # Errors
/// Returns `SIDECAR_UNAVAILABLE` on transport failure, or the normalized
/// structured error from the sidecar otherwise.
pub async fn forward<B: Serialize, T: DeserializeOwned>(
    state: &AppState,
    method: Method,
    path: &str,
    body: Option<&B>,
) -> Result<T, CommandError> {
    let url = format!("{}{}", state.base_url(), path);
    let mut req = state
        .http
        .request(method, &url)
        .header(API_KEY_HEADER, state.token());
    if let Some(b) = body {
        req = req.json(b);
    }
    let resp = req.send().await.map_err(|e| {
        CommandError::sidecar_unavailable(format!("request to sidecar failed: {e}"))
    })?;
    response::parse::<T>(resp).await
}

/// Forward a request that has no request body.
pub async fn get<T: DeserializeOwned>(state: &AppState, path: &str) -> Result<T, CommandError> {
    forward::<(), T>(state, Method::GET, path, None).await
}
