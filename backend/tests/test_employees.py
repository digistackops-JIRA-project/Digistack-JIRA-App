"""Unit + Integration + API tests for Employees."""


def _emp_payload(team_id, manager_id, email="emp@sapsecops.in"):
    return {
        "name": "Bob Employee",
        "email": email,
        "password": "Employee1",
        "phone": "+91-8000000000",
        "team_id": team_id,
        "manager_id": manager_id,
    }


# ── Unit: create employee ──────────────────────────────────────────────────────
def test_create_employee_success(client, auth_headers, seed_team, seed_manager):
    res = client.post(
        "/api/v1/employees/",
        json=_emp_payload(seed_team["id"], seed_manager["id"]),
        headers=auth_headers,
    )
    assert res.status_code == 201
    body = res.json()
    assert body["name"] == "Bob Employee"
    assert body["team_name"] == "DevOps"
    assert body["manager_name"] == "John Manager"
    assert "hashed_password" not in body


def test_create_employee_invalid_team(client, auth_headers, seed_manager):
    res = client.post(
        "/api/v1/employees/",
        json=_emp_payload(99999, seed_manager["id"]),
        headers=auth_headers,
    )
    assert res.status_code == 404


def test_create_employee_invalid_manager(client, auth_headers, seed_team):
    res = client.post(
        "/api/v1/employees/",
        json=_emp_payload(seed_team["id"], 99999),
        headers=auth_headers,
    )
    assert res.status_code == 404


def test_create_employee_duplicate_email(client, auth_headers, seed_team, seed_manager):
    payload = _emp_payload(seed_team["id"], seed_manager["id"])
    client.post("/api/v1/employees/", json=payload, headers=auth_headers)
    res = client.post("/api/v1/employees/", json=payload, headers=auth_headers)
    assert res.status_code == 409


def test_create_employee_weak_password(client, auth_headers, seed_team, seed_manager):
    payload = _emp_payload(seed_team["id"], seed_manager["id"])
    payload["password"] = "abc"
    res = client.post("/api/v1/employees/", json=payload, headers=auth_headers)
    assert res.status_code == 422


# ── Unit: list employees ───────────────────────────────────────────────────────
def test_list_employees_empty(client, auth_headers):
    res = client.get("/api/v1/employees/", headers=auth_headers)
    assert res.status_code == 200
    assert res.json() == []


def test_list_employees(client, auth_headers, seed_team, seed_manager):
    client.post(
        "/api/v1/employees/",
        json=_emp_payload(seed_team["id"], seed_manager["id"]),
        headers=auth_headers,
    )
    res = client.get("/api/v1/employees/", headers=auth_headers)
    assert len(res.json()) == 1


# ── Integration: employees by manager ─────────────────────────────────────────
def test_employees_by_manager(client, auth_headers, seed_team, seed_manager):
    client.post(
        "/api/v1/employees/",
        json=_emp_payload(seed_team["id"], seed_manager["id"]),
        headers=auth_headers,
    )
    res = client.get("/api/v1/employees/by-manager", headers=auth_headers)
    assert res.status_code == 200
    groups = res.json()
    assert len(groups) >= 1
    assert groups[0]["manager_name"] == "John Manager"
    assert len(groups[0]["employees"]) == 1


# ── Unit: delete employee ──────────────────────────────────────────────────────
def test_delete_employee(client, auth_headers, seed_team, seed_manager):
    emp = client.post(
        "/api/v1/employees/",
        json=_emp_payload(seed_team["id"], seed_manager["id"]),
        headers=auth_headers,
    ).json()
    res = client.delete(f"/api/v1/employees/{emp['id']}", headers=auth_headers)
    assert res.status_code == 204


def test_delete_nonexistent_employee(client, auth_headers):
    res = client.delete("/api/v1/employees/99999", headers=auth_headers)
    assert res.status_code == 404


# ── API: no auth ──────────────────────────────────────────────────────────────
def test_employees_no_auth(client):
    assert client.get("/api/v1/employees/").status_code == 401
