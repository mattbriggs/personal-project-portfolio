"""Contract tests covering the sessions -> scoring -> dashboard workflow."""


def _make_project(auth_client, name="Work") -> int:
    return auth_client.post("/api/v1/projects", json={"name": name}).json()["id"]


def test_session_default_duration_applied(auth_client) -> None:
    pid = _make_project(auth_client)
    resp = auth_client.post(
        "/api/v1/sessions",
        json={"project_id": pid, "scheduled_date": "2026-04-07", "status": "planned"},
    )
    assert resp.status_code == 201
    # Default from config is 90.
    assert resp.json()["duration_minutes"] == 90
    assert resp.json()["week_key"] == "2026.15"


def test_session_status_and_dashboard(auth_client) -> None:
    pid = _make_project(auth_client)
    s = auth_client.post(
        "/api/v1/sessions",
        json={
            "project_id": pid,
            "scheduled_date": "2026-04-07",
            "status": "planned",
            "duration_minutes": 60,
        },
    ).json()
    auth_client.post(f"/api/v1/sessions/{s['id']}/status", json={"status": "done"})

    dash = auth_client.get("/api/v1/dashboard?week_key=2026.15").json()
    assert dash["week_key"] == "2026.15"
    row = next(r for r in dash["rows"] if r["project"]["id"] == pid)
    assert row["planned"] == 1
    assert row["completed"] == 1
    assert dash["week_done_minutes"] == 60


def test_reschedule_moves_week(auth_client) -> None:
    pid = _make_project(auth_client)
    s = auth_client.post(
        "/api/v1/sessions",
        json={"project_id": pid, "scheduled_date": "2026-04-07", "status": "planned"},
    ).json()
    moved = auth_client.post(
        f"/api/v1/sessions/{s['id']}/reschedule", json={"scheduled_date": "2026-04-14"}
    ).json()
    assert moved["week_key"] == "2026.16"


def test_score_override_persists(auth_client) -> None:
    pid = _make_project(auth_client)
    resp = auth_client.post(
        "/api/v1/scores/override",
        json={
            "project_id": pid,
            "week_key": "2026.15",
            "score": 88,
            "status": "green",
            "reason": "ahead of plan",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["is_manual_override"] is True


def test_score_override_requires_reason(auth_client) -> None:
    pid = _make_project(auth_client)
    resp = auth_client.post(
        "/api/v1/scores/override",
        json={
            "project_id": pid,
            "week_key": "2026.15",
            "score": 88,
            "status": "green",
            "reason": "",
        },
    )
    assert resp.status_code == 422


def test_weekly_review_get_or_create_and_save(auth_client) -> None:
    got = auth_client.get("/api/v1/reviews/2026.15").json()
    assert got["id"] == 0
    assert got["date_from"] == "2026-04-06"

    saved = auth_client.put(
        "/api/v1/reviews/2026.15", json={"what_moved": "a lot", "hours_invested": 5.5}
    ).json()
    assert saved["id"] > 0
    assert saved["what_moved"] == "a lot"

    history = auth_client.get("/api/v1/reviews").json()["reviews"]
    assert any(r["week_key"] == "2026.15" for r in history)
