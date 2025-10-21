from __future__ import annotations

from fastapi.testclient import TestClient

from src.app.main import create_app


def make_client() -> TestClient:
    app = create_app(use_memory=True)
    return TestClient(app)


def test_tasks_crud_flow():
    client = make_client()

    # Create
    res = client.post("/tasks/", json={"title": "test"})
    assert res.status_code == 201, res.text
    created = res.json()
    tid = created["id"]
    assert created["title"] == "test"

    # List
    res = client.get("/tasks/")
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list) and len(items) == 1

    # Get by id
    res = client.get(f"/tasks/{tid}")
    assert res.status_code == 200
    got = res.json()
    assert got["id"] == tid

    # Patch update
    res = client.patch(f"/tasks/{tid}", json={"done": True})
    assert res.status_code == 200
    updated = res.json()
    assert updated["done"] is True

    # Delete
    res = client.delete(f"/tasks/{tid}")
    assert res.status_code == 204

    # Get after delete -> 404
    res = client.get(f"/tasks/{tid}")
    assert res.status_code == 404

