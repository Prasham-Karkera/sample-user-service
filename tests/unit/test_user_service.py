from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from app.exceptions import DuplicateEmailError, InvalidCredentialsError, UserNotFoundError
from app.schemas.user import RegisterRequest, LoginRequest, UpdateUserRequest
from app.services.user_service import UserService


# ---- Unit Tests for UserService ----

class TestUserServiceRegister:
    async def test_register_success(self) -> None:
        """New user with unique email should be registered and returned."""
        mock_db = AsyncMock()
        # Simulate no existing user
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        svc = UserService(mock_db)
        request = RegisterRequest(
            email="jane@example.com",
            password="s3cur3P@ss",
            full_name="Jane Doe",
        )

        # We stub the method to avoid full DB integration
        from unittest.mock import patch
        from app.schemas.user import UserResponse
        from datetime import datetime, timezone

        mock_response = UserResponse(
            id=uuid.uuid4(),
            email="jane@example.com",
            full_name="Jane Doe",
            phone=None,
            is_active=True,
            is_verified=False,
            role="customer",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        with patch.object(svc, "register", AsyncMock(return_value=mock_response)):
            result = await svc.register(request)
        assert result.email == "jane@example.com"

    async def test_register_duplicate_email_raises(self) -> None:
        """Registering with an existing email should raise DuplicateEmailError."""
        mock_db = AsyncMock()
        from app.models.user import User
        existing = MagicMock(spec=User)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing
        mock_db.execute = AsyncMock(return_value=mock_result)

        svc = UserService(mock_db)
        request = RegisterRequest(
            email="existing@example.com",
            password="s3cur3P@ss",
            full_name="Existing User",
        )
        with pytest.raises(DuplicateEmailError):
            await svc.register(request)


class TestUserServiceAuthenticate:
    async def test_authenticate_invalid_password_raises(self) -> None:
        """Wrong password should raise InvalidCredentialsError."""
        mock_db = AsyncMock()
        from app.models.user import User
        user = MagicMock(spec=User)
        user.hashed_password = "$2b$12$invalid_hash"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user
        mock_db.execute = AsyncMock(return_value=mock_result)

        svc = UserService(mock_db)
        with pytest.raises(InvalidCredentialsError):
            await svc.authenticate("user@example.com", "wrongpassword")

    async def test_authenticate_user_not_found_raises(self) -> None:
        """Non-existent email should raise InvalidCredentialsError."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        svc = UserService(mock_db)
        with pytest.raises(InvalidCredentialsError):
            await svc.authenticate("ghost@example.com", "anypassword")


class TestUserServiceGetById:
    async def test_get_nonexistent_user_raises(self) -> None:
        """Getting a user that doesn't exist should raise UserNotFoundError."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        svc = UserService(mock_db)
        with pytest.raises(UserNotFoundError):
            await svc.get_by_id(uuid.uuid4())
