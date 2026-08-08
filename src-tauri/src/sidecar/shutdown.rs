//! Sidecar termination.
//!
//! Ensures the child process is killed when the application exits so no orphaned
//! sidecar keeps the database open.

use std::process::Child;

/// Terminate the sidecar child process, ignoring "already exited" errors.
///
/// # Returns
/// `true` if a kill signal was sent (or the process had already exited).
pub fn terminate(child: &mut Child) -> bool {
    match child.try_wait() {
        Ok(Some(_)) => true, // already exited
        _ => child.kill().is_ok(),
    }
}

/// Detect whether the child has exited unexpectedly.
///
/// # Returns
/// `Some(success)` if the process has exited, `None` if still running.
pub fn exited(child: &mut Child) -> Option<bool> {
    match child.try_wait() {
        Ok(Some(status)) => Some(status.success()),
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::process::Command;

    #[test]
    fn terminate_kills_a_long_running_child() {
        // `sleep 30` is a cheap long-running child on Unix.
        let mut child = Command::new("sleep").arg("30").spawn().expect("spawn sleep");
        assert!(exited(&mut child).is_none());
        assert!(terminate(&mut child));
        let _ = child.wait();
    }

    #[test]
    fn exited_reports_completed_child() {
        let mut child = Command::new("true").spawn().expect("spawn true");
        let _ = child.wait();
        assert_eq!(exited(&mut child), Some(true));
    }
}
