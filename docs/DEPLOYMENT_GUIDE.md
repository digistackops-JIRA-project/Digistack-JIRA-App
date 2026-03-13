# SapSecOps Ticketing System — Phase 1: Admin Portal
## Complete Deployment Guide: Dev → Staging → Production

---

## Table of Contents
1. [Architecture Overview](#1-architecture-overview)
2. [Team Responsibilities](#2-team-responsibilities)
3. [Prerequisites](#3-prerequisites)
4. [Environment Setup](#4-environment-setup)
5. [Local Development](#5-local-development)
6. [Database Pipeline](#6-database-pipeline-db-team)
7. [Backend Pipeline](#7-backend-pipeline-backend-team)
8. [Frontend Pipeline](#8-frontend-pipeline-frontend-team)
9. [Dev → Staging → Prod Flow](#9-dev--staging--prod-deployment-flow)
10. [Kubernetes Migration Guide](#10-kubernetes-migration-guide)
11. [Health Checks & Monitoring](#11-health-checks--monitoring)
12. [Test Cases Per Stage](#12-test-cases-per-deployment-stage)
13. [Rollback Procedures](#13-rollback-procedures)
14. [Real-World Organisation Deployment Process](#14-real-world-organisation-deployment-process)
15. [Secrets Management](#15-secrets-management)

---

## 1. Architecture Overview

```
                    ┌──────────────────────────────────────┐
                    │         Load Balancer / Nginx         │
                    │     (HTTPS termination, rate limit)   │
                    └────────────┬─────────────────────────┘
                                 │
              ┌──────────────────┴──────────────────┐
              │                                      │
     ┌────────▼─────────┐                ┌──────────▼───────────┐
     │  Frontend (Vue3) │                │  Backend (FastAPI)    │
     │  Nginx container │                │  Uvicorn container    │
     │  Port 80 / 443   │                │  Port 8000            │
     └──────────────────┘                └──────────┬───────────┘
                                                    │
                                         ┌──────────▼───────────┐
                                         │   MySQL 8.0           │
                                         │   Database: admindb   │
                                         │   Flyway migrations   │
                                         └──────────────────────┘
```

**Component summary:**

| Component | Tech | Port | Managed by |
|-----------|------|------|------------|
| Frontend  | Vue 3 + Vite + Nginx | 80/443 | Frontend Team |
| Backend   | Python 3.11 + FastAPI + Uvicorn | 8000 | Backend Team |
| Database  | MySQL 8.0 | 3306 | DB Team |
| Migrations | Flyway 10 | — | DB Team |

---

## 2. Team Responsibilities

### DB Team
- Write and review all Flyway migration scripts (`V*.sql`)
- Run DB pipeline before any backend deployment
- Manage DB credentials via Vault / Jenkins credentials
- Own database backups and recovery

### Backend Team
- Develop and test FastAPI application
- Write/maintain unit, integration, and API tests in `pytest`
- Build and push Docker images
- Run backend pipeline after DB migrations are confirmed

### Frontend Team
- Develop and test Vue 3 application
- Write/maintain unit tests in Vitest
- Build and push Docker images
- Run frontend pipeline independently (after backend API is stable)

---

## 3. Prerequisites

### Physical Servers (per environment)

| Server | Specs (minimum) | Purpose |
|--------|----------------|---------|
| Dev     | 2 vCPU, 4GB RAM | Development & initial testing |
| Staging | 4 vCPU, 8GB RAM | Pre-production validation |
| Prod    | 8 vCPU, 16GB RAM | Live production |

### Software on each server

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker deploy

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Java (for Flyway standalone)
sudo apt-get install -y openjdk-17-jre-headless

# Create deploy user
sudo useradd -m -s /bin/bash deploy
sudo mkdir -p /home/deploy/.ssh
# Add your CI server's SSH public key to /home/deploy/.ssh/authorized_keys
```

### Jenkins Server
- Jenkins LTS with plugins: Pipeline, Docker Pipeline, SSH Agent, Cobertura, JUnit, Credentials Binding
- Docker installed on Jenkins agents

---

## 4. Environment Setup

### Environment Variables Per Environment

Create `/etc/sapsecops/` on each server:

**`admin-backend.dev.env`**
```
DB_HOST=<dev-mysql-ip>
DB_PORT=3306
DB_USER=adminuser
DB_PASSWORD=<dev-db-password>
DB_NAME=admindb
SECRET_KEY=<dev-256bit-secret>
APP_ENV=development
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=http://<dev-frontend-ip>
```

**`admin-backend.staging.env`**
```
DB_HOST=<staging-mysql-ip>
DB_PORT=3306
DB_USER=adminuser
DB_PASSWORD=<staging-db-password>
DB_NAME=admindb
SECRET_KEY=<staging-256bit-secret>
APP_ENV=staging
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=https://admin-staging.sapsecops.in
```

**`admin-backend.prod.env`**
```
DB_HOST=<prod-mysql-ip>
DB_PORT=3306
DB_USER=adminuser
DB_PASSWORD=<prod-db-password>
DB_NAME=admindb
SECRET_KEY=<prod-256bit-secret>
APP_ENV=production
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://admin.sapsecops.in
```

> ⚠️ **NEVER commit .env files to Git. Use Jenkins Credentials or HashiCorp Vault.**

---

## 5. Local Development

### Quick Start (All Teams)

```bash
# Clone the repo
git clone https://git.sapsecops.in/ticketing/admin-portal.git
cd admin-portal

# Start entire stack
docker-compose up -d

# Check all containers are healthy
docker-compose ps

# Watch logs
docker-compose logs -f
```

### Backend Development (without Docker)

```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy env file
cp .env.example .env
# Edit .env with your local MySQL details

# Run locally
uvicorn app.main:app --reload --port 8000

# API docs available at:
# http://localhost:8000/api/docs
```

### Frontend Development (without Docker)

```bash
cd frontend

# Install dependencies
npm install

# Set API base URL
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local

# Start dev server
npm run dev

# App available at: http://localhost:5173
```

---

## 6. Database Pipeline (DB Team)

### Step-by-Step

**Step 1 — Write migration**
```bash
# New file must follow Flyway naming convention:
# V{version}__{description}.sql
# Example: V3__add_department_column.sql

vim database/migrations/V3__add_department_column.sql
```

**Step 2 — Test migration locally**
```bash
docker run --rm \
  -v $(pwd)/database/migrations:/flyway/sql \
  -e FLYWAY_URL="jdbc:mysql://localhost:3306/admindb?useSSL=false" \
  -e FLYWAY_USER=adminuser \
  -e FLYWAY_PASSWORD=adminpass \
  flyway/flyway:10 info   # preview

docker run --rm \
  -v $(pwd)/database/migrations:/flyway/sql \
  flyway/flyway:10 migrate  # apply
```

**Step 3 — Commit and push to feature branch**
```bash
git checkout -b db/add-department-column
git add database/migrations/V3__add_department_column.sql
git commit -m "DB: V3 add department column to employees"
git push origin db/add-department-column
```

**Step 4 — Raise PR, get DB Team Lead approval**

**Step 5 — Merge to `main`; DB pipeline triggers automatically**

**Step 6 — Jenkins DB pipeline runs:**
1. Checkout
2. Validate SQL files
3. Flyway `info` (dry-run preview)
4. ✅ Automatic deploy to **Dev**
5. ✅ Automatic deploy to **Staging**
6. ⏸️  Manual approval gate for **Prod**
7. Flyway `migrate` on Prod
8. Flyway `validate` confirms checksums

---

## 7. Backend Pipeline (Backend Team)

### Step-by-Step

**Step 1 — Develop feature on branch**
```bash
git checkout -b feature/add-team-api
```

**Step 2 — Run tests locally**
```bash
cd backend
pytest tests/ -v --cov=app
# All tests must pass before pushing
```

**Step 3 — Push and open PR**
- PR requires at least 1 peer review
- Automated PR checks run tests + lint

**Step 4 — Merge to `main`; Jenkins backend pipeline triggers:**

1. **Checkout**
2. **Unit + Integration Tests** (pytest with SQLite) → JUnit XML + Coverage report
3. **Lint** (flake8) → fail build if errors
4. **Docker build** → `sapsecops/admin-backend:{BUILD_NUMBER}-{GIT_SHA}`
5. **Push image** to private registry
6. **Deploy to Dev** via SSH → `docker stop` old → `docker run` new
7. **Health Check Dev** → curl `/health/ready` must return 200
8. **API Smoke Tests Dev** → test login endpoint works
9. ⏸️  **Manual approval** → Staging
10. **Deploy to Staging** → same docker run pattern
11. **Health Check Staging**
12. ⏸️  **Manual approval** → Prod (requires Release Manager sign-off)
13. **Deploy to Prod**
14. **Health Check Prod** → fails build and sends alert if not 200

---

## 8. Frontend Pipeline (Frontend Team)

### Step-by-Step

**Step 1 — Develop feature on branch**
```bash
git checkout -b feature/employee-table-pagination
```

**Step 2 — Run tests locally**
```bash
cd frontend
npm run test:unit
npm run lint
npm run build   # ensure build succeeds
```

**Step 3 — PR → merge → Jenkins frontend pipeline triggers:**

1. **Checkout**
2. **npm ci** (clean install)
3. **Unit Tests** (Vitest) → JUnit XML
4. **Lint** (ESLint)
5. **Production Build** (vite build)
6. **Docker build** (multi-stage: Node build + Nginx serve)
7. **Push image** to private registry
8. **Deploy Dev** → `docker run` Nginx container
9. **Smoke Test Dev** → curl frontend returns HTTP 200
10. ⏸️  **Manual approval** → Staging
11. **Deploy Staging**
12. ⏸️  **Manual approval** → Prod
13. **Deploy Prod**

---

## 9. Dev → Staging → Prod Deployment Flow

### Environment Progression Rules

```
Developer's Laptop
       │
       │ git push
       ▼
  Feature Branch
       │
       │ Pull Request
       ▼
   Code Review ──── FAILED ──→ Back to Developer
       │
       │ Approved & Merged
       ▼
    main branch
       │
       │ Pipeline Auto-triggers
       ▼
  ┌────────────┐
  │    DEV     │  ← Full automated: tests + lint + build + deploy + healthcheck
  │  Server    │  ← QA team runs exploratory testing here
  └─────┬──────┘
        │
        │ Manual Approval (Dev Lead)
        ▼
  ┌────────────┐
  │  STAGING   │  ← Mirrors production environment exactly
  │  Server    │  ← Business/UAT testing happens here
  └─────┬──────┘
        │
        │ Manual Approval (Release Manager + CTO sign-off for prod)
        │ Must be done in release window (e.g., Tuesday 2-4 PM IST)
        ▼
  ┌────────────┐
  │    PROD    │  ← Blue/Green swap OR Docker container swap
  │  Server    │  ← Monitoring alerts enabled
  └────────────┘
```

### Deployment Order (Always follow this sequence!)

**For every release:**
1. 🗄️  **DB Team** runs DB migration pipeline first
2. ⚙️  **Backend Team** runs backend pipeline second
3. 🌐 **Frontend Team** runs frontend pipeline third

> Never deploy backend before DB migrations are confirmed.
> Never deploy frontend to prod before backend is verified healthy.

### Branch Strategy (GitFlow)

```
main           ← Production-ready code only
  └─ develop   ← Integration branch (all features merged here first)
       └─ feature/xyz   ← Individual feature branches
       └─ bugfix/abc    ← Bug fix branches
       └─ hotfix/xyz    ← Urgent production fixes (branch from main)
```

---

## 10. Kubernetes Migration Guide

When ready to migrate from physical servers to Kubernetes, the code works
without change because containers are already environment-agnostic.

### Backend Kubernetes Manifest (example)

```yaml
# k8s/backend/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: admin-backend
  namespace: sapsecops
spec:
  replicas: 2
  selector:
    matchLabels:
      app: admin-backend
  template:
    metadata:
      labels:
        app: admin-backend
    spec:
      containers:
      - name: admin-backend
        image: registry.sapsecops.in/sapsecops/admin-backend:IMAGE_TAG
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: admin-backend-secrets
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 15
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: admin-backend
  namespace: sapsecops
spec:
  selector:
    app: admin-backend
  ports:
  - port: 8000
    targetPort: 8000
```

### Flyway on Kubernetes (Job)

```yaml
# k8s/db/flyway-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: flyway-migrate
  namespace: sapsecops
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: flyway
        image: flyway/flyway:10
        args:
          - -url=jdbc:mysql://$(DB_HOST):3306/admindb
          - -user=$(DB_USER)
          - -password=$(DB_PASSWORD)
          - migrate
        envFrom:
        - secretRef:
            name: db-secrets
        volumeMounts:
        - name: migrations
          mountPath: /flyway/sql
      volumes:
      - name: migrations
        configMap:
          name: flyway-migrations
```

---

## 11. Health Checks & Monitoring

### Endpoints

| Endpoint | Purpose | Expected Response |
|----------|---------|-------------------|
| `GET /health` | App version + env info | `{"status":"UP","version":"1.0.0","environment":"production"}` |
| `GET /health/live` | Is the process alive? | `{"status":"ALIVE"}` |
| `GET /health/ready` | Is DB connected? Ready to serve? | `{"status":"READY","database":"UP"}` |

### Monitoring Setup (Recommended)

```bash
# Install Prometheus node-exporter on each server
docker run -d --name node-exporter \
  -p 9100:9100 \
  --pid=host \
  -v /:/host:ro,rslave \
  prom/node-exporter --path.rootfs=/host

# Add to Prometheus scrape config:
# - targets: ['dev-host:9100', 'staging-host:9100', 'prod-host:9100']
```

**Alert rules to configure:**
- Backend `/health/ready` returns non-200 for > 1 minute → PagerDuty
- MySQL replication lag > 30s → Slack alert
- Container restart > 3 times in 5 minutes → Slack alert

---

## 12. Test Cases Per Deployment Stage

### DEV Stage Tests (Automated in Pipeline)

| Test Type | Tool | What it tests |
|-----------|------|---------------|
| Unit tests | pytest | Individual functions, password hashing, schema validation |
| Integration tests | pytest + TestClient | API endpoints with SQLite in-memory DB |
| Frontend unit tests | Vitest | Vue components render correctly |
| Lint | flake8 / ESLint | Code style |
| Health check | curl | `/health/ready` returns 200 |
| API smoke test | curl | Admin login returns JWT token |

### STAGING Stage Tests (Manual + Automated)

| Test Type | Who | What |
|-----------|-----|------|
| End-to-end flow | QA Team | Login → Create Team → Add Manager → Add Employee |
| API collection | Backend Team | Full Postman/curl collection against staging |
| UI acceptance | Frontend Team | All CRUD operations work in browser |
| Security scan | Security Team | OWASP ZAP scan against staging URL |
| Load test | QA Team | 50 concurrent users for 5 minutes (k6 or JMeter) |
| DB migration verification | DB Team | `flyway validate` confirms checksums match |

### PROD Stage Tests (Post-deployment)

| Test Type | Who | What |
|-----------|-----|------|
| Health check | Pipeline | `/health/ready` must return 200 within 10s |
| Smoke test | Release Manager | Login with admin credentials, verify 3 buttons visible |
| Synthetic monitoring | DevOps | Scheduled health pings every 60s |

---

## 13. Rollback Procedures

### Backend / Frontend Rollback

```bash
# List available images
docker images registry.sapsecops.in/sapsecops/admin-backend

# Roll back to previous tag (e.g., 45-abc1234)
docker stop admin-backend
docker rm admin-backend
docker run -d --name admin-backend \
  --restart always \
  -p 8000:8000 \
  --env-file /etc/sapsecops/admin-backend.prod.env \
  registry.sapsecops.in/sapsecops/admin-backend:45-abc1234

# Verify health
curl http://localhost:8000/health/ready
```

### Database Rollback

> ⚠️ Flyway does NOT support automatic rollback (it's SQL, not reversible by default).
> Always create a `U` (undo) migration script paired with each `V` script.

```bash
# Emergency: restore from backup taken BEFORE the migration
mysqldump -h prod-db-host -u adminuser -p admindb > backup_before_v3.sql

# To restore:
mysql -h prod-db-host -u adminuser -p admindb < backup_before_v3.sql
```

**Rule: DB Team MUST take a manual backup before every Prod migration.**

---

## 14. Real-World Organisation Deployment Process

This describes how the deployment works end-to-end in practice, following
the same process used at mature software organisations.

### Sprint Cycle (2-week sprints)

```
Week 1:
  Mon–Fri  → Development on feature branches
  Friday   → Feature freeze: all PRs merged to develop by EOD

Week 2:
  Mon      → Regression testing on develop branch
  Tue      → DB Team runs Flyway migrate on Staging
             Backend Team deploys to Staging
             Frontend Team deploys to Staging
  Wed–Thu  → QA / UAT on Staging
             Bug fixes merged directly to develop
  Thu EOD  → Release candidate tagged: git tag v1.0.2-rc1
  Fri 2PM  → Release window opens
             Change Management ticket raised (change request form)
             All three teams on a call:
               1. DB migration to Prod → DB Lead confirms ✅
               2. Backend deploy to Prod → Backend Lead confirms ✅
               3. Frontend deploy to Prod → Frontend Lead confirms ✅
               4. QA smoke test on Prod → QA confirms ✅
             Release window closes at 4PM
```

### Change Management Checklist (Before Every Prod Deploy)

- [ ] Change request ticket approved by Release Manager
- [ ] DB backup taken and verified restorable
- [ ] All Staging tests passed
- [ ] Rollback plan documented
- [ ] On-call engineer is available during deployment
- [ ] Monitoring dashboards open on second screen
- [ ] Deployment window communicated to stakeholders

### Git Tagging Convention

```bash
# Release candidate
git tag -a v1.0.0-rc1 -m "Release candidate 1 for v1.0.0"
git push origin v1.0.0-rc1

# Final release after Prod deploy
git tag -a v1.0.0 -m "Production release v1.0.0 — 2024-01-15"
git push origin v1.0.0
```

### Communication Protocol

| Event | Channel | Who |
|-------|---------|-----|
| Feature branch merged | Slack #dev | Auto via Jenkins |
| Dev deployment done | Slack #deployments | Auto via Jenkins |
| Staging ready for UAT | Slack #qa-team | Jenkins + manual message |
| Prod deployment starting | Slack #incidents | Release Manager |
| Prod deployment done | Slack #deployments | Auto via Jenkins |
| Prod health check failed | PagerDuty + Slack #incidents | Auto |

---

## 15. Secrets Management

### Development
- Use `.env` files locally (never committed to Git)
- `.gitignore` includes `*.env` and `.env*`

### Jenkins Credentials
- Store all secrets in Jenkins Credentials Store (Credentials → System → Global)
- Reference as `withCredentials([usernamePassword(credentialsId: 'db-prod', ...)])`
- Credential IDs:
  - `db-dev` / `db-staging` / `db-prod` — DB username/password
  - `docker-registry` — Registry login
  - `ssh-dev-server` / `ssh-staging-server` / `ssh-prod-server` — SSH keys

### Production (HashiCorp Vault — Recommended)
```bash
# Write secrets
vault kv put secret/sapsecops/admin-backend/prod \
  db_password=<value> \
  secret_key=<value>

# Read in deployment script
vault kv get -field=db_password secret/sapsecops/admin-backend/prod
```

---

*Document version: 1.0.0 | Last updated: Phase-1 Admin Portal*
*Next: Phase-2 Manager Portal | Phase-3 Employee Portal*
