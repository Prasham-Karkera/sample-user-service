from __future__ import annotations

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import DuplicateEmailError, UserNotFoundError
from app.schemas.user import (
    PaginatedUsersResponse,
    RegisterRequest,
    UpdateUserRequest,
    UserResponse,
)
from app.services.user_service import UserService

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/v1/users")


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> UserService:
    return UserService(db)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user account. Email must be unique.",
    operation_id="register_user",
    tags=["Users"],
)
async def register(
    body: RegisterRequest,
    svc: Annotated[UserService, Depends(_get_service)],
) -> UserResponse:
    try:
        return await svc.register(body)
    except DuplicateEmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": "DUPLICATE_EMAIL", "message": str(exc)}},
        ) from exc


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Returns a single user's profile by UUID.",
    operation_id="get_user",
    tags=["Users"],
)
async def get_user(
    user_id: uuid.UUID,
    svc: Annotated[UserService, Depends(_get_service)],
) -> UserResponse:
    try:
        return await svc.get_by_id(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "USER_NOT_FOUND", "message": str(exc)}},
        ) from exc


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user profile",
    description="Partially updates a user's profile fields.",
    operation_id="update_user",
    tags=["Users"],
)
async def update_user(
    user_id: uuid.UUID,
    body: UpdateUserRequest,
    svc: Annotated[UserService, Depends(_get_service)],
) -> UserResponse:
    try:
        return await svc.update(user_id, body)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"error": {"code": "USER_NOT_FOUND", "message": str(exc)}}) from exc


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate user",
    description="Soft-deletes a user by marking them as inactive.",
    operation_id="deactivate_user",
    tags=["Users"],
)
async def deactivate_user(
    user_id: uuid.UUID,
    svc: Annotated[UserService, Depends(_get_service)],
) -> None:
    try:
        await svc.deactivate(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"error": {"code": "USER_NOT_FOUND", "message": str(exc)}}) from exc
