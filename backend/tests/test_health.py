"""Unit + Integration tests for health endpoints."""


# ── /health ───────────────────────────────────────────────────────────────────
def test_health_returns_200(client):
    res = client.get("/health")
    assert res.status_code == 200


def test_health_body(client):
    body = client.get("/health").json()
    assert body["status"] == "UP"
    assert "version" in body
    assert "environment" in body


# ── /health/live ──────────────────────────────────────────────────────────────
def test_liveness_returns_200(client):
    res = client.get("/health/live")
    assert res.status_code == 200


def test_liveness_body(client):
    body = client.get("/health/live").json()
    assert body["status"] == "ALIVE"


# ── /health/ready ─────────────────────────────────────────────────────────────
def test_readiness_returns_200(client):
    res = client.get("/health/ready")
    assert res.status_code == 200


def test_readiness_body(client):
    body = client.get("/health/ready").json()
    # In test environment DB check is SQLite → should be READY
    assert "status" in body
    assert "database" in body
