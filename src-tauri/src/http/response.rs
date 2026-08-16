//! Normalization of sidecar responses into command results.

use crate::errors::{codes, CommandError};
use serde::de::DeserializeOwned;

/// The JSON error body shape returned by the sidecar.
#[derive(serde::Deserialize)]
struct ApiError {
    code: Option<String>,
    message: Option<String>,
    #[serde(default)]
    field_errors: std::collections::HashMap<String, Vec<String>>,
    #[serde(default)]
    correlation_id: Option<String>,
    #[serde(default)]
    retryable: bool,
}

/// Convert a completed HTTP response into a typed result.
///
/// On a 2xx status the body is deserialized into `T`. Otherwise the structured
/// error body is mapped into a [`CommandError`], preserving the code,
/// field errors, correlation ID, and retryable flag.
pub async fn parse<T: DeserializeOwned>(resp: reqwest::Response) -> Result<T, CommandError> {
    let status = resp.status();
    let bytes = resp
        .bytes()
        .await
        .map_err(|e| CommandError::sidecar_unavailable(format!("read body failed: {e}")))?;

    if status.is_success() {
        if bytes.is_empty() {
            // Some endpoints (rare) may return empty; let serde try null.
            return serde_json::from_slice(b"null").map_err(|e| {
                CommandError::new(codes::INTERNAL_ERROR, format!("decode failed: {e}"))
            });
        }
        return serde_json::from_slice::<T>(&bytes)
            .map_err(|e| CommandError::new(codes::INTERNAL_ERROR, format!("decode failed: {e}")));
    }

    // Error path: try to parse the structured body.
    match serde_json::from_slice::<ApiError>(&bytes) {
        Ok(api) => Err(CommandError {
            code: api
                .code
                .unwrap_or_else(|| codes::INTERNAL_ERROR.to_string()),
            message: api.message.unwrap_or_else(|| "Request failed.".into()),
            field_errors: api.field_errors,
            correlation_id: api.correlation_id,
            retryable: api.retryable,
        }),
        Err(_) => Err(CommandError::new(
            codes::INTERNAL_ERROR,
            format!("Sidecar returned status {status}"),
        )),
    }
}
