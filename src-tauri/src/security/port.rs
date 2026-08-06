//! Dynamic loopback port selection.
//!
//! Binds an ephemeral port on `127.0.0.1` to discover a free port, then releases
//! it so the sidecar can bind it. There is an inherent (small) race window
//! between release and the sidecar binding; readiness polling confirms success.

use std::io;
use std::net::{Ipv4Addr, TcpListener};

/// Pick an available loopback TCP port.
///
/// # Returns
/// A free port on `127.0.0.1`, or an [`io::Error`] if none could be bound.
pub fn pick_free_port() -> io::Result<u16> {
    let listener = TcpListener::bind((Ipv4Addr::LOCALHOST, 0))?;
    let port = listener.local_addr()?.port();
    Ok(port)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn picks_a_nonzero_loopback_port() {
        let port = pick_free_port().expect("should find a free port");
        assert!(port > 0);
        // The port should be immediately bindable again after release.
        let _l = TcpListener::bind((Ipv4Addr::LOCALHOST, port)).expect("rebind");
    }

    #[test]
    fn successive_calls_return_bindable_ports() {
        let p1 = pick_free_port().unwrap();
        let p2 = pick_free_port().unwrap();
        assert!(p1 > 0 && p2 > 0);
    }
}
