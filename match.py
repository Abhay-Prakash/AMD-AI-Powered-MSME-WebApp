from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class GlobalMatchResponse(BaseModel):
    id: UUID
    client_id: UUID
    company_name: str
    scheme: str
    confidence: str
    confidence_score: float
    status: str
    benefit: Decimal
    recommendation: str
    review_required: bool
    reason: str
    citation: str
    clause_ref: str
    issuing_body: str
    last_verified: str
    sector: str | None = None
    enterprise_class: str = "Micro"

