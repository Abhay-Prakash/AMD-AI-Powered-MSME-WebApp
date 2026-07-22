"""Pydantic schemas for CA Profile request/response contracts."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.ca_profile import VerificationStatus


class CAProfileCreate(BaseModel):
    """Request schema for creating a CA profile. user_id is provided externally."""

    full_name: str = Field(..., min_length=1, max_length=255)
    membership_number: str | None = Field(default=None, max_length=50)
    phone: str | None = Field(default=None, max_length=20)
    designation: str | None = Field(default=None, max_length=100)
    years_of_experience: int | None = Field(default=None, ge=0, le=80)
    bio: str | None = None
    profile_photo_url: str | None = Field(default=None, max_length=500)


class CAProfileUpdate(BaseModel):
    """Partial update schema for a CA profile. All fields are optional."""

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    membership_number: str | None = Field(default=None, max_length=50)
    phone: str | None = Field(default=None, max_length=20)
    designation: str | None = Field(default=None, max_length=100)
    years_of_experience: int | None = Field(default=None, ge=0, le=80)
    bio: str | None = None
    profile_photo_url: str | None = Field(default=None, max_length=500)


class VerificationStatusUpdate(BaseModel):
    """
    Request schema for the verification status endpoint.

    verified_by_user_id should be the UUID of the admin performing the action.
    Once auth middleware is in place, this will be extracted from the JWT token.
    """

    status: VerificationStatus
    verified_by_user_id: UUID | None = None


class CAProfileRead(BaseModel):
    """Response schema for a CA profile record."""

    id: UUID
    user_id: UUID
    full_name: str
    membership_number: str | None
    phone: str | None
    designation: str | None
    years_of_experience: int | None
    bio: str | None
    profile_photo_url: str | None
    verification_status: str
    verified_at: datetime | None
    verified_by_user_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
