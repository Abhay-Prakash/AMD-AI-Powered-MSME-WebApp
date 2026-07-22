"""Pydantic schemas for Firm Membership request/response contracts."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.firm_membership import MembershipRole


class FirmMembershipCreate(BaseModel):
    """
    Request schema for adding a CA to a firm.

    ca_profile_id is in the body; firm_id comes from the URL path parameter.
    """

    ca_profile_id: UUID
    role: MembershipRole | None = None
    is_primary: bool = False
    joined_at: date | None = None
    left_at: date | None = None


class FirmMembershipRead(BaseModel):
    """Response schema for a firm membership record."""

    id: UUID
    ca_profile_id: UUID
    firm_id: UUID
    role: str | None
    is_primary: bool
    joined_at: date | None
    left_at: date | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
