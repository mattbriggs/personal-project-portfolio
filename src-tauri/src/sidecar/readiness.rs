//! Readiness polling.
//!
//! Repeatedly probes the sidecar's unauthenticated `/health` endpoint until it
//! responds or a timeout elapses. `/health` is used (not `/ready`) so liveness
//! is confirmed even before the database is fully ready; the caller may probe
//! `/ready` separately.

use std::time::{Duration, Instant};

/// Outcome of waiting for the sidecar to become ready.
#[derive(Debug, PartialEq, Eq)]
pub enum ReadinessOutcome {
    /// The sidecar responded healthy.
    Ready,
    /// The deadline elapsed with no healthy response.
    TimedOut,
}

/// Poll `http://127.0.0.1:{port}/health` until healthy or `timeout` elapses.
///
/// # Arguments
/// * `client` - Shared HTTP client.
/// * `base_url` - Sidecar base URL.
/// * `timeout` - Overall deadline.
/// * `interval` - Delay between polls.
pub async fn wait_until_ready(
    client: &reqwest::Client,
    base_url: &str,
    timeout: Duration,
    interval: Duration,
) -> ReadinessOutcome {
    let deadline = Instant::now() + timeout;
    let url = format!("{base_url}/health");
    loop {
        if let Ok(resp) = client.get(&url).send().await {
            if resp.status().is_success() {
                return ReadinessOutcome::Ready;
            }
        }
        if Instant::now() >= deadline {
            return ReadinessOutcome::TimedOut;
        }
        tokio::time::sleep(interval).await;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn times_out_against_dead_port() {
        // Port 1 is privileged/closed; expect a prompt timeout.
        let client = reqwest::Client::builder()
            .connect_timeout(Duration::from_millis(50))
            .build()
            .unwrap();
        let outcome = wait_until_ready(
            &client,
            "http://127.0.0.1:1",
            Duration::from_millis(150),
            Duration::from_millis(50),
        )
        .await;
        assert_eq!(outcome, ReadinessOutcome::TimedOut);
    }
}
