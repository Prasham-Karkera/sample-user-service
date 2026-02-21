from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import structlog
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import jwt
from app.config import settings
from app.exceptions import (
    DuplicateEmailError,
    InvalidCredentialsError,
    UserNotFoundError,
)
from app.models.user import User
from app.schemas.user import RegisterRequest, UpdateUserRequest, UserResponse, TokenResponse

logger = structlog.get_logger(__name__)

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def _hash_password(self, password: str) -> str:
        return _pwd_context.hash(password)

    def _verify_password(self, plain: str, hashed: str) -> bool:
        return _pwd_context.verify(plain, hashed)

    def _create_access_token(self, user: User) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "roles": [user.role],
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=settings.JWT_EXPIRY_SECONDS)).timestamp()),
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    async def authenticate(self, email: str, password: str) -> TokenResponse:
        result = await self._db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user or not self._verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password")
        logger.info("user_authenticated", user_id=str(user.id))
        token = self._create_access_token(user)
        return TokenResponse(access_token=token, expires_in=settings.JWT_EXPIRY_SECONDS)

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    async def register(self, request: RegisterRequest) -> UserResponse:
        # Check duplicate email
        result = await self._db.execute(select(User).where(User.email == request.email))
        if result.scalar_one_or_none():
            raise DuplicateEmailError(f"Email already registered: {request.email}")

        user = User(
            email=request.email,
            hashed_password=self._hash_password(request.password),
            full_name=request.full_name,
            phone=request.phone,
        )
        self._db.add(user)
        await self._db.commit()
        await self._db.refresh(user)
        logger.info("user_registered", user_id=str(user.id), email=user.email)
        return UserResponse.model_validate(user)

    async def get_by_id(self, user_id: uuid.UUID) -> UserResponse:
        result = await self._db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        return UserResponse.model_validate(user)

    async def list_users(self, page: int = 1, page_size: int = 20) -> list[UserResponse]:
        offset = (page - 1) * page_size
        result = await self._db.execute(
            select(User).order_by(User.created_at.desc()).offset(offset).limit(page_size)
        )
        return [UserResponse.model_validate(u) for u in result.scalars().all()]

    async def update(self, user_id: uuid.UUID, request: UpdateUserRequest) -> UserResponse:
        result = await self._db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        if request.full_name is not None:
            user.full_name = request.full_name
        if request.phone is not None:
            user.phone = request.phone
        await self._db.commit()
        await self._db.refresh(user)
        logger.info("user_updated", user_id=str(user_id))
        return UserResponse.model_validate(user)

    async def deactivate(self, user_id: uuid.UUID) -> None:
        result = await self._db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        user.is_active = False
        await self._db.commit()
        logger.info("user_deactivated", user_id=str(user_id))
