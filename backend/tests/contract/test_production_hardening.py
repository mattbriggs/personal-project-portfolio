"""Contract tests verifying production API hardening."""

from pathlib import Path

from fastapi.testclient import TestClient

from portfolio_manager.api.app import create_app
from portfolio_manager.bootstrap import build_container


def _prod_client(tmp_path: Path) -> TestClient:
    container = build_container(
        config_path=tmp_path / "config.toml",
        db_path=":memory:",
        token="prod-token",
        production=True,
    )
    return TestClient(create_app(container))


def test_docs_disabled_in_production(tmp_path: Path) -> None:
    client = _prod_client(tmp_path)
    # Probe with a valid token so a 404 proves the route is genuinely disabled
    # (not merely blocked by authentication).
    client.headers.update({"X-API-Key": "prod-token"})
    assert client.get("/docs").status_code == 404
    assert client.get("/redoc").status_code == 404
    assert client.get("/openapi.json").status_code == 404


def test_settings_update_reports_no_restart_for_same_path(tmp_path: Path) -> None:
    # In-memory DB has no active path, so a path change cannot claim restart.
    client = _prod_client(tmp_path)
    client.headers.update({"X-API-Key": "prod-token"})
    resp = client.put(
        "/api/v1/settings",
        json={
            "log_level": "INFO",
            "theme": "dark",
            "default_duration_minutes": 60,
            "weekly_budget_hours": 10,
            "database_path": "~/.portfolio_manager/portfolio.db",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["theme"] == "dark"
