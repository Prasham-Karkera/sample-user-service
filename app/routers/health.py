from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/health")


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


@router.get("/live", response_model=HealthResponse, operation_id="user_health_live", tags=["Health"])
async def liveness() -> HealthResponse:
    from app.config import settings
    return HealthResponse(status="ok", service="user-service", version=settings.APP_VERSION)


@router.get("/ready", response_model=HealthResponse, operation_id="user_health_ready", tags=["Health"])
async def readiness() -> HealthResponse:
    from app.config import settings
    return HealthResponse(status="ok", service="user-service", version=settings.APP_VERSION)
