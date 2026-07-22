from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client import Client
from app.repositories.base_repository import BaseRepository
from app.schemas.client import ClientCreate, ClientUpdate


class ClientRepository(BaseRepository[Client]):
    """
    Data access for the Client model scoped to a specific CA.
    """

    model = Client

    def __init__(self, session: AsyncSession, ca_profile_id: UUID) -> None:
        super().__init__(session)
        self.ca_profile_id = ca_profile_id

    async def get(self, record_id: UUID) -> Client | None:
        from sqlalchemy import select
        stmt = select(Client).where(Client.id == record_id, Client.ca_profile_id == self.ca_profile_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> list[Client]:
        from sqlalchemy import select
        stmt = (
            select(Client)
            .where(Client.ca_profile_id == self.ca_profile_id)
            .offset(skip)
            .limit(limit)
            .order_by(Client.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        from sqlalchemy import select, func
        stmt = select(func.count(Client.id)).where(Client.ca_profile_id == self.ca_profile_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create(self, data: ClientCreate) -> Client:
        client_data = data.model_dump()
        client_data["ca_profile_id"] = self.ca_profile_id
        client = Client(**client_data)
        self.session.add(client)
        await self.session.commit()
        await self.session.refresh(client)
        return client

    async def update(self, client: Client, data: ClientUpdate) -> Client:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)
        await self.session.commit()
        await self.session.refresh(client)
        return client

    async def get_portfolio_aggregates(self, skip: int = 0, limit: int = 100) -> "list[dict]":
        from sqlalchemy import select, func, literal_column
        from app.models.match import Match
        from app.models.application import Application
        
        # We need to compute matches count and potential recovery per client.
        # matches.status = 'active' or 'suggested'
        stmt = (
            select(
                Client,
                func.count(Match.id).label("matches_count"),
                func.coalesce(func.sum(Match.benefit), 0).label("potential_recovery")
            )
            .outerjoin(Match, Match.client_id == Client.id)
            .where(Client.ca_profile_id == self.ca_profile_id)
            .group_by(Client.id)
            .offset(skip)
            .limit(limit)
            .order_by(Client.created_at.desc())
        )
        
        result = await self.session.execute(stmt)
        rows = result.all()
        
        portfolio = []
        for client, m_count, recovery in rows:
            portfolio.append({
                "client": client,
                "matches_count": m_count,
                "potential_recovery": recovery,
            })
            
        return portfolio

    async def get_financial_totals(self) -> dict:
        from sqlalchemy import select, func
        from app.models.match import Match
        from app.models.invoice import Invoice
        
        # Pending fees = sum(invoice.success_fee_amount) where status in pending, overdue
        # Disbursed to date = sum(match.benefit) where match.status == disbursed
        # Success fee earned = sum(invoice.success_fee_amount) where status == paid
        
        # Query 1: Disbursed to date
        stmt_disbursed = (
            select(func.coalesce(func.sum(Match.benefit), 0))
            .select_from(Client)
            .join(Match, Match.client_id == Client.id)
            .where(Client.ca_profile_id == self.ca_profile_id)
            .where(Match.status == "disbursed")
        )
        res_disbursed = await self.session.execute(stmt_disbursed)
        disbursed_to_date = res_disbursed.scalar_one()
        
        # Query 2: Fees
        stmt_fees = (
            select(
                Invoice.payment_status,
                func.coalesce(func.sum(Invoice.success_fee_amount), 0)
            )
            .select_from(Client)
            .join(Match, Match.client_id == Client.id)
            .join(Invoice, Invoice.application_id == Match.id)
            .where(Client.ca_profile_id == self.ca_profile_id)
            .group_by(Invoice.payment_status)
        )
        res_fees = await self.session.execute(stmt_fees)
        fees = res_fees.all()
        
        pending_fees = 0
        success_fee_earned = 0
        for status, amount in fees:
            if status in ("pending", "overdue"):
                pending_fees += amount
            elif status == "paid":
                success_fee_earned += amount
                
        return {
            "disbursed_to_date": disbursed_to_date,
            "pending_fees": pending_fees,
            "success_fee_earned": success_fee_earned,
        }

    async def get_highest_value_matches(self, limit: int = 10) -> list:
        from sqlalchemy import select
        from app.models.match import Match
        
        stmt = (
            select(Match, Client.company_name)
            .select_from(Client)
            .join(Match, Match.client_id == Client.id)
            .where(Client.ca_profile_id == self.ca_profile_id)
            .where(Match.status.in_(["suggested", "active", "under_review", "drafted", "submitted"]))
            .order_by(Match.benefit.desc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.all()
        
    async def get_recent_disbursements(self, limit: int = 5) -> list:
        from sqlalchemy import select
        from app.models.match import Match
        from app.models.invoice import Invoice
        
        stmt = (
            select(Invoice, Match, Client.company_name)
            .select_from(Client)
            .join(Match, Match.client_id == Client.id)
            .join(Invoice, Invoice.application_id == Match.id)
            .where(Client.ca_profile_id == self.ca_profile_id)
            .where(Invoice.payment_status == "paid")
            .order_by(Invoice.created_at.desc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.all()

    async def get_portfolio_totals(self) -> dict:
        from sqlalchemy import select, func
        from app.models.match import Match
        
        stmt = (
            select(
                func.count(Match.id).label("matches_count"),
                func.coalesce(func.sum(Match.benefit), 0).label("potential_recovery")
            )
            .select_from(Client)
            .outerjoin(Match, Match.client_id == Client.id)
            .where(Client.ca_profile_id == self.ca_profile_id)
        )
        
        result = await self.session.execute(stmt)
        row = result.first()
        
        return {
            "matches_count": row.matches_count if row else 0,
            "potential_recovery": row.potential_recovery if row else 0,
        }

