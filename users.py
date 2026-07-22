"""Users router — thin HTTP layer for user identity endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    session: AsyncSession = Depends(get_db_session),
) -> UserRead:
    """Register a new user. Returns the created user without password data."""
    service = UserService(session)
    try:
        return await service.create_user(data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> UserRead:
    """Fetch a user by UUID."""
    service = UserService(session)
    user = await service.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> UserRead:
    """Partially update a user record (is_active only in this phase)."""
    service = UserService(session)
    user = await service.update_user(user_id, data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """
    Deactivate a user (soft delete — sets is_active=False).

    This endpoint never hard-deletes. The user record is preserved for
    audit trail and referential integrity with ca_profiles.
    """
    service = UserService(session)
    deactivated = await service.deactivate_user(user_id)
    if not deactivated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
