//! Shared reqwest client construction.

use std::time::Duration;

/// Build the HTTP client used for all sidecar requests.
///
/// A short connect timeout keeps the UI responsive when the sidecar is down.
pub fn build_client() -> reqwest::Client {
    reqwest::Client::builder()
        .connect_timeout(Duration::from_secs(2))
        .timeout(Duration::from_secs(30))
        .build()
        .expect("failed to build reqwest client")
}
