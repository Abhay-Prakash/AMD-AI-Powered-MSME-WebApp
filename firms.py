"""Firms router — thin HTTP layer for firm CRUD and membership management endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.firm import FirmCreate, FirmRead, FirmUpdate
from app.schemas.firm_membership import FirmMembershipCreate, FirmMembershipRead
from app.services.firm_membership_service import FirmMembershipService
from app.services.firm_service import FirmService

router = APIRouter()


# ---------------------------------------------------------------------------
# Firm CRUD
# ---------------------------------------------------------------------------


@router.post("", response_model=FirmRead, status_code=status.HTTP_201_CREATED)
async def create_firm(
    data: FirmCreate,
    session: AsyncSession = Depends(get_db_session),
) -> FirmRead:
    """Create a new CA firm."""
    service = FirmService(session)
    return await service.create_firm(data)


@router.get("", response_model=list[FirmRead])
async def list_firms(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
) -> list[FirmRead]:
    """List all firms with pagination."""
    service = FirmService(session)
    return await service.list_firms(skip=skip, limit=limit)


@router.get("/{firm_id}", response_model=FirmRead)
async def get_firm(
    firm_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> FirmRead:
    """Fetch a firm by UUID."""
    service = FirmService(session)
    firm = await service.get_firm(firm_id)
    if firm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Firm not found",
        )
    return firm


@router.patch("/{firm_id}", response_model=FirmRead)
async def update_firm(
    firm_id: UUID,
    data: FirmUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> FirmRead:
    """Partially update a firm record."""
    service = FirmService(session)
    firm = await service.update_firm(firm_id, data)
    if firm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Firm not found",
        )
    return firm


@router.delete("/{firm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_firm(
    firm_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """
    Delete a firm. Cascades to all associated firm_memberships rows.
    CA profiles themselves are not affected.
    """
    service = FirmService(session)
    deleted = await service.delete_firm(firm_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Firm not found",
        )


# ---------------------------------------------------------------------------
# Firm Membership sub-resource
# ---------------------------------------------------------------------------


@router.post(
    "/{firm_id}/members",
    response_model=FirmMembershipRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_firm_member(
    firm_id: UUID,
    data: FirmMembershipCreate,
    session: AsyncSession = Depends(get_db_session),
) -> FirmMembershipRead:
    """Add a CA to a firm. ca_profile_id is provided in the request body."""
    service = FirmMembershipService(session)
    try:
        return await service.add_member(firm_id, data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get("/{firm_id}/members", response_model=list[FirmMembershipRead])
async def list_firm_members(
    firm_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> list[FirmMembershipRead]:
    """List all CA members of a firm, ordered by primary first."""
    service = FirmMembershipService(session)
    return await service.list_firm_members(firm_id)


@router.delete(
    "/{firm_id}/members/{membership_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_firm_member(
    firm_id: UUID,
    membership_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """Remove a CA from a firm by membership record UUID."""
    service = FirmMembershipService(session)
    removed = await service.remove_member(membership_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership record not found",
        )
