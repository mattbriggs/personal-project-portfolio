//! Cryptographically random per-launch authentication token.
//!
//! The token is generated once per application launch, kept only in in-memory
//! runtime state ([`crate::app_state::AppState`]), passed to the sidecar via an
//! environment variable, and attached to every protected request as `X-API-Key`.
//! It is never persisted to disk or logged.

use rand::RngCore;

/// Number of random bytes in a token (256 bits of entropy).
pub const TOKEN_BYTES: usize = 32;

/// Generate a new random token as a lowercase hex string.
///
/// # Returns
/// A 64-character hex string (32 random bytes).
pub fn generate_token() -> String {
    let mut bytes = [0u8; TOKEN_BYTES];
    rand::thread_rng().fill_bytes(&mut bytes);
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn token_has_expected_length_and_entropy() {
        let a = generate_token();
        let b = generate_token();
        assert_eq!(a.len(), TOKEN_BYTES * 2);
        assert!(a.chars().all(|c| c.is_ascii_hexdigit()));
        assert_ne!(a, b, "two tokens must differ");
    }
}
