"""Pydantic schemas for Firm request/response contracts."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.firm import FirmType


class FirmCreate(BaseModel):
    """Request schema for creating a firm."""

    firm_name: str = Field(..., min_length=1, max_length=255)
    registration_number: str | None = Field(default=None, max_length=100)
    firm_type: FirmType | None = None
    gstin: str | None = Field(default=None, max_length=15)
    pan: str | None = Field(default=None, max_length=10)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=255)
    website: str | None = Field(default=None, max_length=255)
    established_year: int | None = Field(default=None, ge=1800, le=2100)


class FirmUpdate(BaseModel):
    """Partial update schema for a firm. All fields are optional."""

    firm_name: str | None = Field(default=None, min_length=1, max_length=255)
    registration_number: str | None = Field(default=None, max_length=100)
    firm_type: FirmType | None = None
    gstin: str | None = Field(default=None, max_length=15)
    pan: str | None = Field(default=None, max_length=10)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=255)
    website: str | None = Field(default=None, max_length=500)
    established_year: int | None = Field(default=None, ge=1800, le=2100)


class FirmRead(BaseModel):
    """Response schema for a firm record."""

    id: UUID
    firm_name: str
    registration_number: str | None
    firm_type: str | None
    gstin: str | None
    pan: str | None
    city: str | None
    state: str | None
    phone: str | None
    email: str | None
    website: str | None
    established_year: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
