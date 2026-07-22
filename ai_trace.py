from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import String, Text, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class AITrace(Base):
    __tablename__ = "ai_traces"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    conversation_id: Mapped[str] = mapped_column(String(255), index=True)
    capability: Mapped[str] = mapped_column(String(100))
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=True)
    user_input: Mapped[str] = mapped_column(Text)
    raw_llm_response: Mapped[str] = mapped_column(Text)
    latency_ms: Mapped[int] = mapped_column(Integer)
    tokens_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
