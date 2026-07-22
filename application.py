from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

class ApplicationSummary(BaseModel):
    total: int = 0
    drafted: int = 0
    submitted: int = 0
    approved: int = 0
    disbursed: int = 0

class ApplicationResponse(BaseModel):
    application_id: UUID
    match_id: UUID
    client_id: UUID
    company_name: str
    scheme: str
    benefit: Decimal
    status: str
    draft_preview: str
    missing_documents: List[str]
    gstin: Optional[str] = None
    udyam_number: Optional[str] = None
    enterprise_class: str
    sector: Optional[str] = None
    turnover: Optional[Decimal] = None
    clause_reference: str

class ApplicationListResponse(BaseModel):
    summary: ApplicationSummary
    data: List[ApplicationResponse]

class DraftResponse(BaseModel):
    application_id: UUID
    client_name: str
    scheme: str
    status: str
    generated_at: str
    last_updated: str
    draft_text: str
    missing_documents: List[str]
    benefit: str
    clause_reference: str

class ExportManifestResponse(BaseModel):
    filename: str
    estimated_size: str
    documents: List[str]

