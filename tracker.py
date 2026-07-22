from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class TrackerSummary(BaseModel):
    matched: int
    ready_to_file: int
    submitted: int
    disbursed: int
    pipeline_completion_percentage: float
    estimated_total_benefit: Decimal


class TrackerResponse(BaseModel):
    id: UUID
    application_id: UUID
    client_id: UUID
    client_name: str
    scheme: str
    current_stage: str
    completed_steps: int
    total_steps: int
    workflow_percentage: float
    estimated_benefit: Decimal
    next_step: str
    estimated_completion: str
    assigned_ca: str
    priority: str
    updated_at: str
    clause_ref: str


class TrackerDashboardResponse(BaseModel):
    summary: TrackerSummary
    items: list[TrackerResponse]


class TrackerAdvanceRequest(BaseModel):
    next_stage: str
