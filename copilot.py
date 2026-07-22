from typing import Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.ai.orchestrator import AIOrchestrator
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService
from app.db.session import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ai_trace import AITrace
router = APIRouter()


class CopilotRequest(BaseModel):
    message: str
    conversation_id: str
    client_id: str | None = None
    application_id: str | None = None
    match_id: str | None = None
    attachments: list[Any] = Field(default_factory=list)
    conversation_history: list[dict[str, str]] = Field(default_factory=list)


class Citation(BaseModel):
    document_title: str
    section: str
    page: int | None = None
    chunk_id: str
    source_url: str | None = None
    similarity: float
    display_name: str | None = None
    display_url: str | None = None
    source_agency: str | None = None
    citation_label: str | None = None


class CopilotResponse(BaseModel):
    response: str
    citations: list[Citation]
    metadata: dict[str, Any]


@router.post("/chat", response_model=CopilotResponse)
async def copilot_chat(
    request: CopilotRequest,
    # Ideally inject DB or services if needed for client data
    session: AsyncSession = Depends(get_db_session)
) -> CopilotResponse:
    # Initialize services
    retrieval_service = RetrievalService(session)
    embedding_service = EmbeddingService(session)
    orchestrator = AIOrchestrator()
    
    # In a full implementation we would fetch client_id data using services here
    # For now we simulate context_data
    context_data: dict[str, Any] = {}
    if request.client_id:
        context_data["business_profile"] = {"client_id": request.client_id}
        
    ai_response, knowledge_results, metadata = await orchestrator.chat(
        question=request.message,
        retrieval_service=retrieval_service,
        embedding_service=embedding_service,
        conversation_history=request.conversation_history,
        context_data=context_data,
    )
    
    # Map knowledge_results to Citations
    citations = []
    for k in knowledge_results:
        meta = k.get("metadata", {})
        citations.append(Citation(
            document_title=k.get("document_title") or meta.get("document_title") or meta.get("scheme_name") or "Unknown Document",
            section=k.get("section") or meta.get("section") or "",
            page=k.get("page_number") or meta.get("page") or meta.get("page_number"),
            chunk_id=str(k.get("chunk_id") or meta.get("chunk_id") or ""),
            source_url=k.get("source_url") or meta.get("source_url"),
            similarity=float(k.get("similarity_score") or k.get("distance") or 0.0),
            display_name=k.get("display_name"),
            display_url=k.get("display_url"),
            source_agency=k.get("source_agency"),
            citation_label=k.get("citation_label"),
        ))
        
    response_content = ai_response.content if ai_response.success else "I couldn't retrieve enough verified evidence to answer confidently."
    
    # Trace the interaction
    trace = AITrace(
        conversation_id=request.conversation_id,
        capability="subsidydesk_copilot",
        prompt_version="v1",
        user_input=request.message,
        raw_llm_response=response_content,
        latency_ms=ai_response.latency_ms if ai_response else 0,
        tokens_used=ai_response.estimated_tokens if ai_response else 0,
        metadata_=metadata
    )
    session.add(trace)
    await session.commit()
    
    return CopilotResponse(
        response=response_content,
        citations=citations,
        metadata=metadata,
    )
