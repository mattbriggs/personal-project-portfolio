"""Contract tests for project routes."""


def test_create_and_get_project(auth_client) -> None:
    resp = auth_client.post("/api/v1/projects", json={"name": "My Novel"})
    assert resp.status_code == 201
    project = resp.json()
    assert project["slug"] == "my-novel"

    got = auth_client.get(f"/api/v1/projects/{project['id']}")
    assert got.status_code == 200
    assert got.json()["name"] == "My Novel"


def test_duplicate_name_conflicts(auth_client) -> None:
    auth_client.post("/api/v1/projects", json={"name": "Dup"})
    resp = auth_client.post("/api/v1/projects", json={"name": "Dup"})
    assert resp.status_code == 409
    assert resp.json()["code"] == "CONFLICT"


def test_invalid_priority_is_validation_error(auth_client) -> None:
    resp = auth_client.post("/api/v1/projects", json={"name": "X", "priority": 9})
    assert resp.status_code == 422
    assert resp.json()["code"] == "VALIDATION_ERROR"


def test_missing_project_returns_not_found(auth_client) -> None:
    resp = auth_client.get("/api/v1/projects/9999")
    assert resp.status_code == 404
    assert resp.json()["code"] == "NOT_FOUND"


def test_archived_project_cannot_be_updated(auth_client) -> None:
    created = auth_client.post("/api/v1/projects", json={"name": "Arch"}).json()
    auth_client.post(f"/api/v1/projects/{created['id']}/archive")
    resp = auth_client.put(
        f"/api/v1/projects/{created['id']}",
        json={"name": "Renamed", "status": "active", "priority": 3},
    )
    assert resp.status_code == 409
    assert resp.json()["code"] == "ARCHIVED_READ_ONLY"


def test_plan_round_trip(auth_client) -> None:
    created = auth_client.post("/api/v1/projects", json={"name": "Plan Proj"}).json()
    pid = created["id"]
    md = "# Heading\n\n```mermaid\ngraph TD; A-->B;\n```\n"
    save = auth_client.put(f"/api/v1/projects/{pid}/plan", json={"content": md})
    assert save.status_code == 200
    got = auth_client.get(f"/api/v1/projects/{pid}/plan")
    assert got.json()["content"] == md
