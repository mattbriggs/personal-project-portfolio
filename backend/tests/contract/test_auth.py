"""Contract tests for token authentication and health routes."""


def test_health_is_unauthenticated(client) -> None:
    assert client.get("/health").status_code == 200


def test_ready_is_unauthenticated(client) -> None:
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"


def test_business_route_requires_token(client) -> None:
    resp = client.get("/api/v1/projects")
    assert resp.status_code == 401
    body = resp.json()
    assert body["code"] == "AUTHENTICATION_FAILED"
    assert "correlation_id" in body


def test_business_route_rejects_wrong_token(client) -> None:
    resp = client.get("/api/v1/projects", headers={"X-API-Key": "wrong"})
    assert resp.status_code == 401


def test_business_route_accepts_valid_token(client, test_token: str) -> None:
    resp = client.get("/api/v1/projects", headers={"X-API-Key": test_token})
    assert resp.status_code == 200


def test_correlation_id_header_present(auth_client) -> None:
    resp = auth_client.get("/api/v1/projects")
    assert resp.headers.get("X-Correlation-ID")
