# ============================================================================
# SapSecOps Admin Portal — Makefile
# Usage: make <target>
# ============================================================================

.PHONY: help up down logs \
        backend-test backend-lint backend-run backend-build \
        frontend-test frontend-lint frontend-dev frontend-build \
        db-info db-migrate db-validate db-repair \
        clean

# ── Default ───────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "SapSecOps Admin Portal — Available Commands"
	@echo "─────────────────────────────────────────────"
	@echo "  Stack:"
	@echo "    make up               Start full local stack (docker-compose)"
	@echo "    make down             Stop all containers"
	@echo "    make logs             Tail all container logs"
	@echo ""
	@echo "  Backend Team:"
	@echo "    make backend-test     Run pytest (unit + integration)"
	@echo "    make backend-lint     Run flake8"
	@echo "    make backend-run      Run uvicorn dev server"
	@echo "    make backend-build    Build backend Docker image"
	@echo ""
	@echo "  Frontend Team:"
	@echo "    make frontend-test    Run Vitest unit tests"
	@echo "    make frontend-lint    Run ESLint"
	@echo "    make frontend-dev     Start Vite dev server"
	@echo "    make frontend-build   Production build"
	@echo ""
	@echo "  DB Team:"
	@echo "    make db-info          Preview pending Flyway migrations"
	@echo "    make db-migrate       Apply Flyway migrations"
	@echo "    make db-validate      Validate migration checksums"
	@echo "    make db-repair        Repair flyway_schema_history"
	@echo ""
	@echo "  Utilities:"
	@echo "    make clean            Remove build artifacts and caches"
	@echo "    make hash pass=MyPass Generate bcrypt hash for a password"
	@echo ""

# ── Full Stack ────────────────────────────────────────────────────────────────
up:
	docker-compose up -d
	@echo "Stack is up. Frontend: http://localhost | API docs: http://localhost:8000/api/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

# ── Backend ───────────────────────────────────────────────────────────────────
backend-test:
	cd backend && \
	  pip install -q -r requirements.txt && \
	  pytest tests/ -v --cov=app --cov-report=term-missing

backend-lint:
	cd backend && flake8 app/ --max-line-length=120

backend-run:
	cd backend && uvicorn app.main:app --reload --port 8000

backend-build:
	docker build -t sapsecops/admin-backend:local ./backend

# ── Frontend ──────────────────────────────────────────────────────────────────
frontend-test:
	cd frontend && npm run test:unit

frontend-lint:
	cd frontend && npm run lint

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

frontend-build-docker:
	docker build -t sapsecops/admin-frontend:local ./frontend

# ── Database / Flyway ─────────────────────────────────────────────────────────
FLYWAY_CMD = docker run --rm \
  --network host \
  -v $(PWD)/database/migrations:/flyway/sql \
  -e FLYWAY_URL="jdbc:mysql://localhost:3306/admindb?useSSL=false&allowPublicKeyRetrieval=true" \
  -e FLYWAY_USER=adminuser \
  -e FLYWAY_PASSWORD=adminpass \
  flyway/flyway:10

db-info:
	$(FLYWAY_CMD) info

db-migrate:
	$(FLYWAY_CMD) migrate

db-validate:
	$(FLYWAY_CMD) validate

db-repair:
	$(FLYWAY_CMD) repair

# ── Utilities ─────────────────────────────────────────────────────────────────
hash:
	@python3 -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('$(pass)'))"

clean:
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -name "*.pyc" -delete 2>/dev/null || true
	rm -f backend/test_admin.db backend/coverage.xml backend/test-results.xml
	rm -rf frontend/dist frontend/node_modules/.vite frontend/coverage
	@echo "Clean done."
