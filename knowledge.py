from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class KnowledgeDocumentCreate(BaseModel):
    title: str
    version: str | None = None
    source: str
    source_url: str | None = None
    issuing_authority: str
    category: str
    document_type: str
    effective_date: date | None = None
    published_on: date | None = None


class KnowledgeDocumentResponse(BaseModel):
    id: UUID
    title: str
    version: str | None
    source: str
    source_url: str | None
    issuing_authority: str
    category: str
    document_type: str
    effective_date: date | None
    published_on: date | None
    uploaded_at: datetime
    last_verified: datetime | None
    checksum: str | None
    processing_status: str
    processing_log: list[dict[str, Any]] | None
    
    class Config:
        from_attributes = True


class KnowledgeChunkResponse(BaseModel):
    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    metadata_: dict = Field(..., alias="metadata")
    embedding_status: str
    
    # Embedding Metadata
    embedding_model: str | None = None
    embedding_dimension: int | None = None
    embedding_provider: str | None = None
    embedding_latency_ms: int | None = None
    embedding_generated_at: datetime | None = None
    embedding_version: str | None = None

    class Config:
        from_attributes = True
