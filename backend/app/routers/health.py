from fastapi import APIRouter
from app.schemas import HealthResponse, LivenessResponse, ReadinessResponse
from app.database import check_db_connection
from app.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health():
    """Basic health check — always returns 200 if app is running."""
    return HealthResponse(
        status="UP",
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
    )


@router.get("/health/live", response_model=LivenessResponse, tags=["Health"])
def liveness():
    """Kubernetes liveness probe — is the process alive?"""
    return LivenessResponse(status="ALIVE")


@router.get("/health/ready", response_model=ReadinessResponse, tags=["Health"])
def readiness():
    """Kubernetes readiness probe — can the app serve traffic (DB reachable)?"""
    db_ok = check_db_connection()
    return ReadinessResponse(
        status="READY" if db_ok else "NOT_READY",
        database="UP" if db_ok else "DOWN",
    )
