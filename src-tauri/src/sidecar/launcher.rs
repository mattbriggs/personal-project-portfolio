//! Sidecar process launch.
//!
//! Builds the command that starts the packaged FastAPI sidecar. The auth token
//! is passed via the `PORTFOLIO_SIDECAR_TOKEN` environment variable — never as a
//! command-line argument — so it does not appear in the process list. The port
//! is a non-secret argument.

use crate::errors::CommandError;
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};

/// Description of how to start the sidecar process.
#[derive(Debug, Clone)]
pub struct SidecarCommand {
    /// Program to execute (packaged binary, or `python` in development).
    pub program: PathBuf,
    /// Arguments (excluding the token).
    pub args: Vec<String>,
}

impl SidecarCommand {
    /// Build the launch command for a packaged binary.
    ///
    /// # Arguments
    /// * `binary` - Path to the frozen `portfolio-sidecar` binary.
    /// * `port` - Loopback port to bind.
    /// * `production` - Whether to pass `--production`.
    pub fn packaged(binary: PathBuf, port: u16, production: bool) -> Self {
        let mut args = vec!["--port".into(), port.to_string()];
        if production {
            args.push("--production".into());
        }
        Self {
            program: binary,
            args,
        }
    }

    /// Assemble the argument vector actually passed to the OS (token excluded).
    ///
    /// Exposed for tests that assert the token is not present in argv.
    pub fn argv(&self) -> Vec<String> {
        let mut v = vec![self.program.to_string_lossy().to_string()];
        v.extend(self.args.clone());
        v
    }
}

/// Spawn the sidecar, passing the token via environment only.
///
/// # Errors
/// Returns `SIDECAR_STARTUP_FAILED` if the process cannot be spawned (e.g. the
/// binary is missing).
#[allow(clippy::result_large_err)]
pub fn spawn(cmd: &SidecarCommand, token: &str) -> Result<Child, CommandError> {
    Command::new(&cmd.program)
        .args(&cmd.args)
        .env("PORTFOLIO_SIDECAR_TOKEN", token)
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| CommandError::sidecar_startup_failed(format!("failed to spawn sidecar: {e}")))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn argv_excludes_token_and_includes_port() {
        let cmd = SidecarCommand::packaged(PathBuf::from("/opt/sidecar"), 8765, true);
        let argv = cmd.argv();
        assert!(argv.contains(&"8765".to_string()));
        assert!(argv.contains(&"--production".to_string()));
        assert!(
            !argv.iter().any(|a| a.contains("TOKEN") || a.len() == 64),
            "token must never appear in argv"
        );
    }
}
