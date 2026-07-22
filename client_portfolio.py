from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ClientStatus(str, Enum):
    ONBOARDED = "ONBOARDED"
    MATCHED = "MATCHED"
    IN_PROGRESS = "IN_PROGRESS"
    DISBURSED = "DISBURSED"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class ClientPortfolioWidget(BaseModel):
    client_id: UUID
    company_name: str
    udyam_number: str | None
    sector: str | None
    enterprise_class: str
    matches_count: int
    potential_recovery: Decimal
    status: ClientStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClientPortfolioResponse(BaseModel):
    clients: list[ClientPortfolioWidget]
    total: int
    skip: int
    limit: int
