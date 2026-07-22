from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Numeric, String, DateTime
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Invoice(TimestampMixin, Base):
    __tablename__ = "invoices"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    application_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    invoice_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    invoice_status: Mapped[str] = mapped_column(String(50), nullable=False, default="generated")
    payment_status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    success_fee_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    success_fee_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    payment_due_date: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payment_received_date: Mapped[str | None] = mapped_column(String(255), nullable=True)
    generated_at: Mapped[str | None] = mapped_column(String(255), nullable=True)

    application = relationship("Match")
