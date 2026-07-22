from typing import Any
from pydantic import BaseModel, Field
from uuid import UUID

class RetrievalRequest(BaseModel):
    query: str
    top_k: int | None = None
    filters: dict[str, Any] | None = None

class RetrievalResult(BaseModel):
    document_id: UUID
    chunk_id: UUID
    document_title: str | None = None
    content: str
    similarity_score: float
    metadata_: dict[str, Any] = Field(default_factory=dict, alias="metadata")
    page_number: int | None = None
    section: str | None = None
    issuing_authority: str | None = None
    document_type: str | None = None
    effective_date: str | None = None
    source_url: str | None = None
    display_name: str | None = None
    display_url: str | None = None
    source_agency: str | None = None
    citation_label: str | None = None

class RetrievalResponse(BaseModel):
    query: str
    query_embedding_model: str
    top_k: int
    processing_time_ms: int
    embedding_latency_ms: int
    database_latency_ms: int
    candidate_count: int
    returned_count: int
    average_similarity_score: float | None = None
    strategy: str
    distance_metric: str
    results: list[RetrievalResult]
