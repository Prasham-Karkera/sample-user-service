from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# --- Request Schemas ---

class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address", example="jane@example.com")
    password: str = Field(..., min_length=8, description="Minimum 8 characters", example="s3cur3P@ssw0rd")
    full_name: str = Field(..., min_length=2, max_length=255, example="Jane Doe")
    phone: str | None = Field(default=None, example="+919876543210")


class UpdateUserRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    phone: str | None = Field(default=None)


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="jane@example.com")
    password: str = Field(..., example="s3cur3P@ssw0rd")


# --- Response Schemas ---

class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    email: str
    full_name: str
    phone: str | None
    is_active: bool
    is_verified: bool
    role: str
    created_at: datetime
    updated_at: datetime


class UserSummary(BaseModel):
    """Lightweight user info — safe for inter-service responses."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    full_name: str
    email: str
    role: str
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token TTL in seconds")


class PaginatedUsersResponse(BaseModel):
    data: list[UserResponse]
    pagination: dict[str, int | str]
    meta: dict[str, str]
