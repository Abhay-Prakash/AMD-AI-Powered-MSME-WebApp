"""Firm Membership repository — data access for the FirmMembership join table."""

from uuid import UUID

from sqlalchemy import select, update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.firm_membership import FirmMembership
from app.repositories.base_repository import BaseRepository
from app.schemas.firm_membership import FirmMembershipCreate


class FirmMembershipRepository(BaseRepository[FirmMembership]):
    """
    Data access for the FirmMembership join table.

    Provides specialised queries beyond standard CRUD:
    - list_by_ca_profile: eager-loads Firm data for the CA memberships view
    - list_by_firm: eager-loads CAProfile data for the firm members view
    - get_by_ca_and_firm: used for duplicate detection in the service layer
    - clear_primary_for_ca: bulk UPDATE used atomically before setting a new primary
    """

    model = FirmMembership

    async def create(
        self,
        *,
        ca_profile_id: UUID,
        firm_id: UUID,
        data: FirmMembershipCreate,
    ) -> FirmMembership:
        membership = FirmMembership(
            ca_profile_id=ca_profile_id,
            firm_id=firm_id,
            role=data.role,
            is_primary=data.is_primary,
            joined_at=data.joined_at,
            left_at=data.left_at,
        )
        self.session.add(membership)
        await self.session.commit()
        await self.session.refresh(membership)
        return membership

    async def get_by_ca_and_firm(
        self, ca_profile_id: UUID, firm_id: UUID
    ) -> FirmMembership | None:
        """Check if a CA already has a membership record in a given firm."""
        stmt = select(FirmMembership).where(
            FirmMembership.ca_profile_id == ca_profile_id,
            FirmMembership.firm_id == firm_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_ca_profile(self, ca_profile_id: UUID) -> list[FirmMembership]:
        """Fetch all memberships for a CA, with Firm eagerly loaded."""
        stmt = (
            select(FirmMembership)
            .where(FirmMembership.ca_profile_id == ca_profile_id)
            .options(selectinload(FirmMembership.firm))
            .order_by(FirmMembership.is_primary.desc(), FirmMembership.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_firm(self, firm_id: UUID) -> list[FirmMembership]:
        """Fetch all members of a firm, with CAProfile eagerly loaded."""
        stmt = (
            select(FirmMembership)
            .where(FirmMembership.firm_id == firm_id)
            .options(selectinload(FirmMembership.ca_profile))
            .order_by(FirmMembership.is_primary.desc(), FirmMembership.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def clear_primary_for_ca(self, ca_profile_id: UUID) -> None:
        """
        Set is_primary=False on all existing memberships for a CA.

        Called atomically before creating a new primary membership.
        Uses a bulk UPDATE to avoid loading all membership rows into memory.
        synchronize_session=False is correct here because the updated rows
        are not read back in the same transaction.
        """
        stmt = (
            sql_update(FirmMembership)
            .where(
                FirmMembership.ca_profile_id == ca_profile_id,
                FirmMembership.is_primary.is_(True),
            )
            .values(is_primary=False)
            .execution_options(synchronize_session=False)
        )
        await self.session.execute(stmt)
