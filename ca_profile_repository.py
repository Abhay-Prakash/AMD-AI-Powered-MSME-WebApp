"""CA Profile repository — data access for Chartered Accountant profiles."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ca_profile import CAProfile
from app.repositories.base_repository import BaseRepository
from app.schemas.ca_profile import CAProfileCreate


class CAProfileRepository(BaseRepository[CAProfile]):
    """Data access for the CAProfile model."""

    model = CAProfile

    async def create(self, *, user_id: UUID, data: CAProfileCreate) -> CAProfile:
        """
        Create a CA profile linked to an existing user.

        user_id is passed explicitly (not via the schema) because it comes
        from the authenticated principal, not from the request body.
        """
        profile = CAProfile(
            **data.model_dump(),
            user_id=user_id,
        )
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def get_by_user_id(self, user_id: UUID) -> CAProfile | None:
        """Fetch the CA profile associated with a given user. Returns None if no profile exists."""
        stmt = select(CAProfile).where(CAProfile.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_membership_number(self, membership_number: str) -> CAProfile | None:
        """Lookup by ICAI membership number. Used for duplicate detection."""
        stmt = select(CAProfile).where(
            CAProfile.membership_number == membership_number
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
