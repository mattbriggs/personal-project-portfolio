//! Explicit, allowlisted Tauri commands.
//!
//! Each command maps exactly one renderer operation to one fixed sidecar method
//! and path via the internal [`crate::http::forwarder`]. There is deliberately
//! **no** generic command that accepts an arbitrary method/path from the
//! renderer — that keeps the exposed surface auditable.
//!
//! Payloads and responses are passed as `serde_json::Value`; the renderer's
//! typed command client applies the generated TypeScript contracts. This avoids
//! duplicating every Pydantic model in Rust while keeping the command list
//! explicit.

pub mod dashboard;
pub mod health;
pub mod milestones;
pub mod plans;
pub mod projects;
pub mod reviews;
pub mod scores;
pub mod sessions;
pub mod settings;
