"""Firm repository — data access for the Firm model."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.firm import Firm
from app.repositories.base_repository import BaseRepository
from app.schemas.firm import FirmCreate, FirmUpdate


class FirmRepository(BaseRepository[Firm]):
    """Data access for the Firm model."""

    model = Firm

    async def create(self, data: FirmCreate) -> Firm:
        firm = Firm(**data.model_dump())
        self.session.add(firm)
        await self.session.commit()
        await self.session.refresh(firm)
        return firm
