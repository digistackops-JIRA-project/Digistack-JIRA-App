"""
Shared pytest fixtures.
Uses an in-memory SQLite DB so tests have NO dependency on a running MySQL server.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import Admin, Team, Manager, Employee
from app.security import hash_password

# ── In-memory SQLite for tests ─────────────────────────────────────────────────
TEST_DB_URL = "sqlite:///./test_admin.db"

engine_test = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(autouse=True)
def reset_db():
    """Truncate tables before each test for isolation."""
    db = TestingSessionLocal()
    db.query(Employee).delete()
    db.query(Manager).delete()
    db.query(Team).delete()
    db.query(Admin).delete()
    db.commit()
    db.close()


@pytest.fixture(scope="session")
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def seed_admin():
    db = TestingSessionLocal()
    admin = Admin(email="admin@sapsecops.in", hashed_password=hash_password("Admin123"))
    db.add(admin)
    db.commit()
    db.close()


@pytest.fixture
def auth_headers(client, seed_admin):
    res = client.post("/api/v1/auth/login", json={"email": "admin@sapsecops.in", "password": "Admin123"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def seed_team(auth_headers, client):
    res = client.post("/api/v1/teams/", json={"team_name": "DevOps"}, headers=auth_headers)
    return res.json()


@pytest.fixture
def seed_manager(auth_headers, client, seed_team):
    res = client.post(
        "/api/v1/managers/",
        json={
            "name": "John Manager",
            "email": "john@sapsecops.in",
            "password": "Manager1",
            "phone": "+91-9999999999",
            "team_id": seed_team["id"],
        },
        headers=auth_headers,
    )
    return res.json()
