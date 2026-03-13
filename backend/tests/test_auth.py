"""Unit + Integration + API tests for Auth."""
import pytest


# ── Unit: login success ────────────────────────────────────────────────────────
def test_login_success(client, seed_admin):
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@sapsecops.in", "password": "Admin123"},
    )
    assert res.status_code == 200
    body = res.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["expires_in"] > 0


# ── Unit: wrong password ───────────────────────────────────────────────────────
def test_login_wrong_password(client, seed_admin):
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@sapsecops.in", "password": "WrongPass"},
    )
    assert res.status_code == 401


# ── Unit: non-existent email ───────────────────────────────────────────────────
def test_login_unknown_email(client, seed_admin):
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@sapsecops.in", "password": "Admin123"},
    )
    assert res.status_code == 401


# ── Unit: invalid email format ─────────────────────────────────────────────────
def test_login_invalid_email_format(client):
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "not-an-email", "password": "Admin123"},
    )
    assert res.status_code == 422


# ── Integration: token is usable ──────────────────────────────────────────────
def test_token_grants_access_to_teams(client, seed_admin):
    token = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@sapsecops.in", "password": "Admin123"},
    ).json()["access_token"]
    res = client.get("/api/v1/teams/", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200


# ── Integration: invalid token is rejected ────────────────────────────────────
def test_invalid_token_rejected(client):
    res = client.get("/api/v1/teams/", headers={"Authorization": "Bearer bad.token.here"})
    assert res.status_code == 401


# ── API: missing body ─────────────────────────────────────────────────────────
def test_login_missing_body(client):
    res = client.post("/api/v1/auth/login", json={})
    assert res.status_code == 422
