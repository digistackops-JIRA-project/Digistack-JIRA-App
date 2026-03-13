# SapSecOps Ticketing System — Phase 1: Admin Portal

A Jira-style ticketing system built with **Vue 3**, **Python FastAPI**, and **MySQL**.

## Project Phases

| Phase | Portal | Status |
|-------|--------|--------|
| Phase 1 | Admin Portal | ✅ This repo |
| Phase 2 | Manager Portal | 🔜 Upcoming |
| Phase 3 | Employee Portal | 🔜 Upcoming |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3 + Vite + Pinia + Vue Router |
| Backend | Python 3.11 + FastAPI + SQLAlchemy |
| Database | MySQL 8.0 |
| Migrations | Flyway 10 |
| Container | Docker + Nginx |
| CI/CD | Jenkins |

---

## Quick Start (Local)

### Prerequisites
- Docker & Docker Compose installed

```bash
# Clone
git clone https://git.sapsecops.in/ticketing/admin-portal.git
cd admin-portal

# Start the full stack (DB + Flyway migrate + Backend + Frontend)
docker-compose up -d

# Verify all containers are healthy
docker-compose ps
```

**Access:**
- Frontend: http://localhost
- Backend API docs: http://localhost:8000/api/docs
- Login: `admin@sapsecops.in` / `Admin123`

---

## Project Structure

```
admin-portal/
├── backend/                    # FastAPI application (Backend Team)
│   ├── app/
│   │   ├── main.py             # App entry point, CORS, router registration
│   │   ├── config.py           # Settings from env vars
│   │   ├── database.py         # SQLAlchemy engine + session
│   │   ├── models.py           # ORM models: Admin, Team, Manager, Employee
│   │   ├── schemas.py          # Pydantic request/response schemas
│   │   ├── security.py         # JWT + bcrypt
│   │   └── routers/
│   │       ├── health.py       # /health, /health/live, /health/ready
│   │       ├── auth.py         # POST /api/v1/auth/login
│   │       ├── teams.py        # CRUD /api/v1/teams
│   │       ├── managers.py     # CRUD /api/v1/managers
│   │       └── employees.py    # CRUD /api/v1/employees + /by-manager
│   ├── tests/                  # pytest: unit + integration + API tests
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # Vue 3 application (Frontend Team)
│   ├── src/
│   │   ├── views/              # LoginView, DashboardView, Teams, Managers, Employees
│   │   ├── store/auth.js       # Pinia auth store
│   │   ├── services/api.js     # Axios API client
│   │   └── router/index.js     # Vue Router with auth guards
│   ├── tests/unit/             # Vitest unit tests
│   ├── Dockerfile              # Multi-stage: Node build + Nginx serve
│   └── nginx.conf              # SPA routing + API proxy
│
├── database/                   # Flyway migrations (DB Team)
│   ├── migrations/
│   │   ├── V1__create_schema.sql
│   │   ├── V2__seed_admin.sql
│   │   ├── U1__undo_create_schema.sql
│   │   └── U2__undo_seed_admin.sql
│   └── flyway.conf
│
├── k8s/                        # Kubernetes manifests (future)
│   ├── backend/
│   ├── frontend/
│   └── database/
│
├── pipelines/                  # Jenkins pipelines per team
│   ├── backend/Jenkinsfile
│   ├── frontend/Jenkinsfile
│   └── database/Jenkinsfile
│
├── scripts/                    # Utility scripts
│   ├── generate_admin_hash.py  # Generate bcrypt hash for seeding
│   └── healthcheck.sh          # Manual health check across environments
│
├── docs/
│   └── DEPLOYMENT_GUIDE.md     # Full Dev→Prod deployment documentation
│
├── Makefile                    # Convenience commands for all teams
└── docker-compose.yml          # Local development stack
```

---

## Team Commands

### Backend Team
```bash
make backend-test      # Run all pytest tests with coverage
make backend-lint      # Run flake8
make backend-run       # Run locally with uvicorn --reload
```

### Frontend Team
```bash
make frontend-test     # Run Vitest unit tests
make frontend-lint     # Run ESLint
make frontend-dev      # Start Vite dev server
make frontend-build    # Production build
```

### DB Team
```bash
make db-info           # Preview pending migrations
make db-migrate        # Apply migrations (local)
make db-validate       # Validate checksums
```

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | No | App health + version |
| GET | `/health/live` | No | Liveness probe |
| GET | `/health/ready` | No | Readiness probe (checks DB) |
| POST | `/api/v1/auth/login` | No | Admin login → JWT |
| GET | `/api/v1/teams/` | JWT | List all teams |
| POST | `/api/v1/teams/` | JWT | Create team |
| DELETE | `/api/v1/teams/{id}` | JWT | Delete team |
| GET | `/api/v1/managers/` | JWT | List all managers |
| POST | `/api/v1/managers/` | JWT | Add manager |
| PUT | `/api/v1/managers/{id}` | JWT | Update manager |
| DELETE | `/api/v1/managers/{id}` | JWT | Delete manager |
| GET | `/api/v1/employees/` | JWT | List all employees |
| GET | `/api/v1/employees/by-manager` | JWT | Employees grouped by manager |
| POST | `/api/v1/employees/` | JWT | Add employee |
| PUT | `/api/v1/employees/{id}` | JWT | Update employee |
| DELETE | `/api/v1/employees/{id}` | JWT | Delete employee |

---

## Deployment

See [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for the complete Dev → Staging → Prod guide.

**Deployment order (always follow this):**
1. 🗄️  DB Team — run Flyway migrations
2. ⚙️  Backend Team — deploy FastAPI
3. 🌐 Frontend Team — deploy Vue app

---

## Default Credentials

| Role | Email | Password | Use |
|------|-------|----------|-----|
| Admin | admin@sapsecops.in | Admin123 | Admin Portal login |

> ⚠️ Change the admin password hash in `V2__seed_admin.sql` before production deployment.
