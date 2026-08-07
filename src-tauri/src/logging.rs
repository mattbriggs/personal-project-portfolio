//! Structured Rust logging with credential redaction.
//!
//! Initializes `tracing` with an env-filter. A helper redacts token-like values
//! so runtime diagnostics never leak the sidecar credential.

/// Initialize tracing once at startup.
pub fn init() {
    let filter = tracing_subscriber::EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| tracing_subscriber::EnvFilter::new("info"));
    let _ = tracing_subscriber::fmt()
        .with_env_filter(filter)
        .without_time()
        .try_init();
}

/// Redact a token-like string for safe logging (keeps a short prefix only).
///
/// # Examples
/// ```
/// use portfolio_manager_lib::logging::redact;
/// assert_eq!(redact("abcdef0123456789"), "abcd…[redacted]");
/// assert_eq!(redact("short"), "[redacted]");
/// ```
pub fn redact(secret: &str) -> String {
    if secret.len() <= 8 {
        "[redacted]".to_string()
    } else {
        format!("{}…[redacted]", &secret[..4])
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn redacts_long_and_short_secrets() {
        assert_eq!(redact("short"), "[redacted]");
        assert!(redact("0123456789abcdef").ends_with("[redacted]"));
        assert!(!redact("0123456789abcdef").contains("89abcdef"));
    }
}
