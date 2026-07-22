from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel

class BillingSummary(BaseModel):
    total_recovered_subsidy: Decimal
    total_success_fee: Decimal
    invoices_generated: int
    invoices_paid: int
    invoices_pending: int

class BillingResponse(BaseModel):
    invoice_id: UUID | None
    application_id: UUID
    client_id: UUID
    client_name: str
    scheme: str
    subsidy_amount: Decimal
    success_fee_percentage: Decimal
    success_fee_amount: Decimal
    invoice_number: str
    invoice_status: str
    payment_status: str
    payment_due_date: str | None
    payment_received_date: str | None
    generated_at: str | None
    updated_at: str | None

class BillingDashboardResponse(BaseModel):
    summary: BillingSummary
    invoices: list[BillingResponse]
