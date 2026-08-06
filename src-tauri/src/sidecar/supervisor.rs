//! Sidecar supervisor.
//!
//! Encapsulates the sidecar lifecycle: port selection, token generation, launch,
//! readiness polling, monitoring, and shutdown. Exposes an explicit state
//! machine so the UI can distinguish "starting", "ready", and "failed".

use crate::security::{port, token};
use serde::Serialize;
use std::process::Child;
use std::sync::{Arc, Mutex};

/// Supervisor lifecycle states.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum SidecarState {
    /// Not yet started.
    NotStarted,
    /// Launch initiated; awaiting readiness.
    Starting,
    /// Healthy and serving requests.
    Ready,
    /// Running but unhealthy (e.g. lost readiness).
    Degraded,
    /// Shutdown initiated.
    Stopping,
    /// Cleanly stopped.
    Stopped,
    /// Startup or runtime failure.
    Failed,
}

/// Prepared launch parameters (port + token) before spawning.
pub struct LaunchPlan {
    /// Selected loopback port.
    pub port: u16,
    /// Generated per-launch token.
    pub token: String,
}

impl LaunchPlan {
    /// Allocate a free loopback port and generate a fresh token.
    ///
    /// # Errors
    /// Returns an error string if no free port can be allocated.
    pub fn prepare() -> Result<Self, String> {
        let port = port::pick_free_port().map_err(|e| format!("port allocation failed: {e}"))?;
        Ok(Self {
            port,
            token: token::generate_token(),
        })
    }
}

/// Owns the spawned child process and tracks shutdown.
pub struct SidecarHandle {
    child: Arc<Mutex<Option<Child>>>,
}

impl SidecarHandle {
    /// Wrap a spawned child process.
    pub fn new(child: Child) -> Self {
        Self {
            child: Arc::new(Mutex::new(Some(child))),
        }
    }

    /// Terminate the child if still running.
    pub fn shutdown(&self) {
        if let Ok(mut guard) = self.child.lock() {
            if let Some(mut child) = guard.take() {
                let _ = crate::sidecar::shutdown::terminate(&mut child);
                let _ = child.wait();
            }
        }
    }

    /// Return `Some(success)` if the child has exited, else `None`.
    pub fn check_exited(&self) -> Option<bool> {
        if let Ok(mut guard) = self.child.lock() {
            if let Some(child) = guard.as_mut() {
                return crate::sidecar::shutdown::exited(child);
            }
        }
        Some(false)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn launch_plan_has_port_and_token() {
        let plan = LaunchPlan::prepare().expect("prepare");
        assert!(plan.port > 0);
        assert_eq!(plan.token.len(), 64);
    }

    #[test]
    fn state_serializes_to_snake_case() {
        let json = serde_json::to_string(&SidecarState::NotStarted).unwrap();
        assert_eq!(json, "\"not_started\"");
    }
}
