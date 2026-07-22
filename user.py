"""Pydantic schemas for User request/response contracts."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """
    Request schema for creating a new user.

    password is accepted as plain text here and hashed in UserService.
    It must never be logged, stored, or returned in any response.
    """

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """
    Partial update schema for a user.

    is_active is the only field exposed for direct update.
    Password changes require a dedicated endpoint (future auth phase).
    """

    is_active: bool | None = None


class UserRead(BaseModel):
    """
    Response schema for a user record.

    hashed_password is never included. This schema is the only safe
    representation of a user that may leave the service boundary.
    """

    id: UUID
    email: str
    is_active: bool
    is_superuser: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
