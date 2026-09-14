from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name, "environment": settings.app_env}


@router.get("/ready", tags=["health"])
def ready() -> dict[str, str]:
    return {"status": "ready", "service": settings.app_name, "environment": settings.app_env}
