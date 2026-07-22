from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class ClientDetailResponse(BaseModel):
    client_id: UUID
    company_name: str
    udyam_number: str | None = None
    gstin: str | None = None
    sector: str | None = None
    enterprise_class: str
    district: str | None = None
    state: str | None = None
    turnover: Decimal | None = None
    investment: Decimal | None = None
    employees: int | None = None
    status: str
    potential_recovery: Decimal
    matches_count: int


class ClientMatchResponse(BaseModel):
    id: UUID
    scheme: str
    confidence: str
    status: str
    reason: str
    benefit: Decimal
    citation: str
    clause_ref: str
    issuing_body: str
    last_verified: str


class ClientDocumentResponse(BaseModel):
    id: UUID
    name: str
    type: str
    ocr_status: str
    uploaded_at: datetime


class ClientAuditResponse(BaseModel):
    id: UUID
    timestamp: datetime
    event: str
    user: str


class MatchUpdate(BaseModel):
    status: str = Field(..., description="The new status to apply to the match (e.g. approved, rejected)")
