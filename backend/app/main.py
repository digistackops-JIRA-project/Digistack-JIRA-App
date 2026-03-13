import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import health, auth, teams, managers, employees

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Admin Portal API — Phase 1 of SapSecOps Ticketing System",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router)                               # /health, /health/live, /health/ready
app.include_router(auth.router,      prefix="/api/v1/auth")
app.include_router(teams.router,     prefix="/api/v1/teams")
app.include_router(managers.router,  prefix="/api/v1/managers")
app.include_router(employees.router, prefix="/api/v1/employees")

# ── Init __init__.py placeholders ─────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 %s v%s starting in [%s] mode", settings.APP_NAME, settings.APP_VERSION, settings.APP_ENV)
