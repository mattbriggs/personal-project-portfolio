//! Tauri-managed runtime state.
//!
//! Holds the sidecar port, the per-launch token (wrapped in [`SecretString`] so
//! it is not accidentally logged or serialized), the base URL, and the current
//! supervisor lifecycle state. The token and port are never exposed to the
//! renderer.

use crate::sidecar::supervisor::SidecarState;
use secrecy::{ExposeSecret, SecretString};
use std::sync::{Arc, Mutex};

/// Shared, thread-safe runtime state managed by Tauri.
pub struct AppState {
    port: u16,
    token: SecretString,
    /// Current lifecycle state, mutated by the supervisor.
    pub state: Arc<Mutex<SidecarState>>,
    /// HTTP client reused across forwarded requests.
    pub http: reqwest::Client,
}

impl AppState {
    /// Create runtime state for a launched sidecar.
    pub fn new(port: u16, token: String, http: reqwest::Client) -> Self {
        Self {
            port,
            token: SecretString::new(token),
            state: Arc::new(Mutex::new(SidecarState::Starting)),
            http,
        }
    }

    /// The loopback base URL of the sidecar.
    pub fn base_url(&self) -> String {
        format!("http://127.0.0.1:{}", self.port)
    }

    /// Expose the token for attaching to an outgoing request header.
    ///
    /// Intentionally crate-visible; callers must not log the returned value.
    pub(crate) fn token(&self) -> &str {
        self.token.expose_secret()
    }

    /// Snapshot the current lifecycle state.
    pub fn current_state(&self) -> SidecarState {
        *self.state.lock().expect("state lock poisoned")
    }

    /// Update the lifecycle state.
    pub fn set_state(&self, new: SidecarState) {
        *self.state.lock().expect("state lock poisoned") = new;
    }
}
