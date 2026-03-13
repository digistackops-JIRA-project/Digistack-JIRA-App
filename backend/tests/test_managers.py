"""Unit + Integration + API tests for Managers."""


def _manager_payload(team_id, email="mgr@sapsecops.in"):
    return {
        "name": "Alice Manager",
        "email": email,
        "password": "Manager1",
        "phone": "+91-9000000000",
        "team_id": team_id,
    }


# ── Unit: create manager ───────────────────────────────────────────────────────
def test_create_manager_success(client, auth_headers, seed_team):
    res = client.post("/api/v1/managers/", json=_manager_payload(seed_team["id"]), headers=auth_headers)
    assert res.status_code == 201
    body = res.json()
    assert body["name"] == "Alice Manager"
    assert body["team_name"] == "DevOps"
    assert "hashed_password" not in body


def test_create_manager_invalid_team(client, auth_headers):
    res = client.post("/api/v1/managers/", json=_manager_payload(99999), headers=auth_headers)
    assert res.status_code == 404


def test_create_manager_duplicate_email(client, auth_headers, seed_team):
    payload = _manager_payload(seed_team["id"])
    client.post("/api/v1/managers/", json=payload, headers=auth_headers)
    res = client.post("/api/v1/managers/", json=payload, headers=auth_headers)
    assert res.status_code == 409


def test_create_manager_weak_password(client, auth_headers, seed_team):
    payload = _manager_payload(seed_team["id"])
    payload["password"] = "weak"
    res = client.post("/api/v1/managers/", json=payload, headers=auth_headers)
    assert res.status_code == 422


def test_create_manager_invalid_email(client, auth_headers, seed_team):
    payload = _manager_payload(seed_team["id"], email="not-valid")
    res = client.post("/api/v1/managers/", json=payload, headers=auth_headers)
    assert res.status_code == 422


# ── Unit: list managers ────────────────────────────────────────────────────────
def test_list_managers_empty(client, auth_headers):
    res = client.get("/api/v1/managers/", headers=auth_headers)
    assert res.status_code == 200
    assert res.json() == []


def test_list_managers(client, auth_headers, seed_manager):
    res = client.get("/api/v1/managers/", headers=auth_headers)
    assert len(res.json()) == 1


# ── Unit: update manager ───────────────────────────────────────────────────────
def test_update_manager(client, auth_headers, seed_manager, seed_team):
    payload = _manager_payload(seed_team["id"], email="updated@sapsecops.in")
    payload["name"] = "Updated Name"
    res = client.put(f"/api/v1/managers/{seed_manager['id']}", json=payload, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Updated Name"


# ── Unit: delete manager ───────────────────────────────────────────────────────
def test_delete_manager(client, auth_headers, seed_team):
    mgr = client.post(
        "/api/v1/managers/",
        json=_manager_payload(seed_team["id"], email="del@sapsecops.in"),
        headers=auth_headers,
    ).json()
    res = client.delete(f"/api/v1/managers/{mgr['id']}", headers=auth_headers)
    assert res.status_code == 204


def test_delete_nonexistent_manager(client, auth_headers):
    res = client.delete("/api/v1/managers/99999", headers=auth_headers)
    assert res.status_code == 404


# ── API: no auth ──────────────────────────────────────────────────────────────
def test_managers_no_auth(client):
    assert client.get("/api/v1/managers/").status_code == 401
