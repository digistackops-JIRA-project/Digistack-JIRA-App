"""Unit + Integration + API tests for Teams."""


# ── Unit: create team ──────────────────────────────────────────────────────────
def test_create_team_success(client, auth_headers):
    res = client.post("/api/v1/teams/", json={"team_name": "Backend"}, headers=auth_headers)
    assert res.status_code == 201
    body = res.json()
    assert body["team_name"] == "Backend"
    assert "id" in body
    assert "created_at" in body


def test_create_team_trims_whitespace(client, auth_headers):
    res = client.post("/api/v1/teams/", json={"team_name": "  Frontend  "}, headers=auth_headers)
    assert res.status_code == 201
    assert res.json()["team_name"] == "Frontend"


def test_create_team_empty_name(client, auth_headers):
    res = client.post("/api/v1/teams/", json={"team_name": "   "}, headers=auth_headers)
    assert res.status_code == 422


def test_create_team_duplicate(client, auth_headers):
    client.post("/api/v1/teams/", json={"team_name": "QA"}, headers=auth_headers)
    res = client.post("/api/v1/teams/", json={"team_name": "QA"}, headers=auth_headers)
    assert res.status_code == 409


# ── Unit: list teams ──────────────────────────────────────────────────────────
def test_list_teams_empty(client, auth_headers):
    res = client.get("/api/v1/teams/", headers=auth_headers)
    assert res.status_code == 200
    assert res.json() == []


def test_list_teams(client, auth_headers, seed_team):
    res = client.get("/api/v1/teams/", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1


# ── Unit: delete team ─────────────────────────────────────────────────────────
def test_delete_team_success(client, auth_headers):
    team = client.post("/api/v1/teams/", json={"team_name": "Temp"}, headers=auth_headers).json()
    res = client.delete(f"/api/v1/teams/{team['id']}", headers=auth_headers)
    assert res.status_code == 204


def test_delete_nonexistent_team(client, auth_headers):
    res = client.delete("/api/v1/teams/99999", headers=auth_headers)
    assert res.status_code == 404


# ── Integration: team used in manager dropdown ────────────────────────────────
def test_team_appears_in_list_after_create(client, auth_headers):
    client.post("/api/v1/teams/", json={"team_name": "SRE"}, headers=auth_headers)
    teams = client.get("/api/v1/teams/", headers=auth_headers).json()
    names = [t["team_name"] for t in teams]
    assert "SRE" in names


# ── API: unauthenticated requests rejected ────────────────────────────────────
def test_list_teams_no_auth(client):
    res = client.get("/api/v1/teams/")
    assert res.status_code == 401


def test_create_team_no_auth(client):
    res = client.post("/api/v1/teams/", json={"team_name": "X"})
    assert res.status_code == 401
