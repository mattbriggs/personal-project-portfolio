//! Typed command errors shared with the renderer.
//!
//! Every Tauri command returns [`CommandError`] on failure. Transport failures
//! and structured API error bodies are both normalized into this shape so the
//! renderer maps a single, stable error taxonomy (mirrors the Python
//! `ErrorResponse` and the TypeScript `CommandError`).

use serde::Serialize;
use std::collections::HashMap;

/// Stable error codes matching the Python and TypeScript taxonomy.
pub mod codes {
    pub const VALIDATION_ERROR: &str = "VALIDATION_ERROR";
    pub const NOT_FOUND: &str = "NOT_FOUND";
    pub const CONFLICT: &str = "CONFLICT";
    pub const ARCHIVED_READ_ONLY: &str = "ARCHIVED_READ_ONLY";
    pub const AUTHENTICATION_FAILED: &str = "AUTHENTICATION_FAILED";
    pub const DATABASE_ERROR: &str = "DATABASE_ERROR";
    pub const SIDECAR_UNAVAILABLE: &str = "SIDECAR_UNAVAILABLE";
    pub const SIDECAR_STARTUP_FAILED: &str = "SIDECAR_STARTUP_FAILED";
    pub const INTERNAL_ERROR: &str = "INTERNAL_ERROR";
}

/// Error payload returned to the renderer for a failed command.
#[derive(Debug, Clone, Serialize)]
pub struct CommandError {
    /// Stable machine-readable error code.
    pub code: String,
    /// User-safe message (never a stack trace or token).
    pub message: String,
    /// Field-level validation errors, when present.
    #[serde(default)]
    pub field_errors: HashMap<String, Vec<String>>,
    /// Correlation ID echoed from the sidecar, when present.
    #[serde(default)]
    pub correlation_id: Option<String>,
    /// Whether the client may safely retry.
    pub retryable: bool,
}

impl CommandError {
    /// Build an error with a code and message.
    pub fn new(code: &str, message: impl Into<String>) -> Self {
        Self {
            code: code.to_string(),
            message: message.into(),
            field_errors: HashMap::new(),
            correlation_id: None,
            retryable: false,
        }
    }

    /// The sidecar could not be reached (transport failure). Retryable.
    pub fn sidecar_unavailable(message: impl Into<String>) -> Self {
        let mut e = Self::new(codes::SIDECAR_UNAVAILABLE, message);
        e.retryable = true;
        e
    }

    /// The sidecar never became ready during startup.
    pub fn sidecar_startup_failed(message: impl Into<String>) -> Self {
        Self::new(codes::SIDECAR_STARTUP_FAILED, message)
    }
}

impl std::fmt::Display for CommandError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}: {}", self.code, self.message)
    }
}

impl std::error::Error for CommandError {}
