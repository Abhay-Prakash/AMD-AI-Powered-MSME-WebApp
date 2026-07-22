import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService
from app.ai.orchestrator import AIOrchestrator
from app.models.ai_trace import AITrace
from sqlalchemy import select

async def main():
    question = "What is the PMEGP eligibility and subsidy rate for a new manufacturing business?"
    
    async with AsyncSessionLocal() as session:
        retrieval_service = RetrievalService(session)
        embedding_service = EmbeddingService(session)
        orchestrator = AIOrchestrator()
        
        print(f"User: {question}\n")
        
        ai_response, knowledge_results, metadata = await orchestrator.chat(
            question=question,
            retrieval_service=retrieval_service,
            embedding_service=embedding_service,
            conversation_history=[],
            context_data={"business_profile": {"industry": "Manufacturing", "investment": 1500000}}
        )
        
        print(f"Copilot [{metadata['model']} - {metadata['latency_ms']}ms]:\n{ai_response.content}\n")
        print(f"Intent Detected: {metadata['intent']}")
        print(f"Retrieved Chunks: {metadata['retrieved_chunks']}")
        
        print("\nChecking AITraces...")
        # Note: the router normally inserts AITrace, but here we used orchestrator directly.
        # We can just verify the query returned success.
        
        # Test trace manually
        trace = AITrace(
            conversation_id="test-session-123",
            capability="subsidydesk_copilot",
            prompt_version="v1",
            user_input=question,
            raw_llm_response=ai_response.content,
            latency_ms=ai_response.latency_ms,
            tokens_used=ai_response.estimated_tokens,
            metadata_=metadata
        )
        session.add(trace)
        await session.commit()
        
        saved_trace = (await session.execute(select(AITrace).where(AITrace.conversation_id == "test-session-123"))).scalars().first()
        print(f"Successfully saved trace: {saved_trace.id}")

if __name__ == "__main__":
    asyncio.run(main())
