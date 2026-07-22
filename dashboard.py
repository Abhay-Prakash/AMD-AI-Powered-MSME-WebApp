from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GreetingWidget(BaseModel):
    first_name: str
    active_clients: int
    active_matches: int
    pending_fees: Decimal
    
    model_config = ConfigDict(from_attributes=True)


class ProfileWidget(BaseModel):
    ca_name: str
    verification_status: str
    firm_name: str | None
    role: str | None
    clients_managed: int
    subscription_tier: str
    last_login: datetime | None
    
    model_config = ConfigDict(from_attributes=True)


class KPIWidget(BaseModel):
    clients_under_management: int
    potential_recovery: Decimal
    disbursed_to_date: Decimal
    success_fee_earned: Decimal
    
    model_config = ConfigDict(from_attributes=True)


class AIMatchWidget(BaseModel):
    match_id: UUID
    client_id: UUID
    client_name: str
    scheme_name: str
    estimated_benefit: Decimal
    confidence_score: float
    priority: str
    review_status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DisbursementWidget(BaseModel):
    disbursement_id: UUID
    client_name: str
    scheme_name: str
    disbursed_amount: Decimal
    fee_percentage: float
    fee_amount: Decimal
    invoice_status: str
    date: date
    
    model_config = ConfigDict(from_attributes=True)


class NotificationItem(BaseModel):
    notification_id: UUID
    type: str
    message: str
    created_at: datetime
    is_read: bool
    
    model_config = ConfigDict(from_attributes=True)


class NotificationSummary(BaseModel):
    unread_count: int
    recent: list[NotificationItem]
    
    model_config = ConfigDict(from_attributes=True)


class WorkspaceShortcut(BaseModel):
    id: str
    label: str
    action_type: str
    target: str
    icon: str
    
    model_config = ConfigDict(from_attributes=True)


class DashboardOverviewResponse(BaseModel):
    greeting: GreetingWidget
    profile: ProfileWidget
    kpis: KPIWidget
    highest_value_matches: list[AIMatchWidget]
    recent_disbursements: list[DisbursementWidget]
    notifications_summary: NotificationSummary
    workspace_shortcuts: list[WorkspaceShortcut]
    
    model_config = ConfigDict(from_attributes=True)
