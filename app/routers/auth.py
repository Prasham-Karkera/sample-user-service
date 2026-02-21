from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import InvalidCredentialsError
from app.schemas.user import LoginRequest, TokenResponse
from app.services.user_service import UserService

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/v1/auth")


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> UserService:
    return UserService(db)


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Obtain access token",
    description=(
        "Authenticate with email and password to receive a JWT access token. "
        "This endpoint is excluded from gateway auth verification."
    ),
    operation_id="login",
    tags=["Auth"],
)
async def login(
    body: LoginRequest,
    svc: Annotated[UserService, Depends(_get_service)],
) -> TokenResponse:
    try:
        return await svc.authenticate(body.email, body.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_CREDENTIALS", "message": str(exc)}},
        ) from exc
