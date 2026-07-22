"""CA Profiles router — thin HTTP layer for CA profile and membership endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.ca_profile import (
    CAProfileCreate,
    CAProfileRead,
    CAProfileUpdate,
    VerificationStatusUpdate,
)
from app.schemas.firm_membership import FirmMembershipRead
from app.services.ca_profile_service import CAProfileService
from app.services.firm_membership_service import FirmMembershipService

router = APIRouter()


@router.post("", response_model=CAProfileRead, status_code=status.HTTP_201_CREATED)
async def create_ca_profile(
    data: CAProfileCreate,
    user_id: UUID = Query(..., description="UUID of the owning user"),
    session: AsyncSession = Depends(get_db_session),
) -> CAProfileRead:
    """
    Create a CA profile for an existing user.

    NOTE: user_id is currently a query parameter for pre-auth testing.
    Once JWT middleware is in place, it will be extracted from the token
    and this parameter will be removed.
    """
    service = CAProfileService(session)
    try:
        return await service.create_ca_profile(user_id, data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get("/by-user/{user_id}", response_model=CAProfileRead)
async def get_ca_profile_by_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> CAProfileRead:
    """
    Fetch the CA profile for a given user UUID.

    Defined before /{ca_profile_id} to prevent 'by-user' matching as UUID.
    """
    service = CAProfileService(session)
    profile = await service.get_ca_profile_by_user(user_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CA profile not found for this user",
        )
    return profile


@router.get("/{ca_profile_id}", response_model=CAProfileRead)
async def get_ca_profile(
    ca_profile_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> CAProfileRead:
    """Fetch a CA profile by its own UUID."""
    service = CAProfileService(session)
    profile = await service.get_ca_profile(ca_profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CA profile not found",
        )
    return profile


@router.patch("/{ca_profile_id}", response_model=CAProfileRead)
async def update_ca_profile(
    ca_profile_id: UUID,
    data: CAProfileUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> CAProfileRead:
    """Partially update a CA profile's professional information."""
    service = CAProfileService(session)
    try:
        profile = await service.update_ca_profile(ca_profile_id, data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CA profile not found",
        )
    return profile


@router.patch("/{ca_profile_id}/verification", response_model=CAProfileRead)
async def update_verification_status(
    ca_profile_id: UUID,
    data: VerificationStatusUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> CAProfileRead:
    """
    Update the verification status of a CA profile.

    This endpoint should be admin-gated once auth middleware is in place.
    """
    service = CAProfileService(session)
    profile = await service.update_verification_status(ca_profile_id, data)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CA profile not found",
        )
    return profile


@router.get("/{ca_profile_id}/memberships", response_model=list[FirmMembershipRead])
async def list_ca_memberships(
    ca_profile_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> list[FirmMembershipRead]:
    """List all firm memberships for a CA profile."""
    service = FirmMembershipService(session)
    return await service.list_ca_memberships(ca_profile_id)
