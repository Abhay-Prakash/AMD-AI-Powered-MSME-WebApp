import asyncio
import time
from app.db.session import AsyncSessionLocal
from app.services.retrieval_service import RetrievalService
from app.ai.gateway import AIGateway

QUERIES = [
    "PMEGP eligibility for new business",
    "CGTMSE guarantee coverage limits",
    "ZED certification requirements",
    "Technology Upgradation scheme details",
    "Interest Subvention rate for manufacturing"
]

async def validate_retrieval():
    async with AsyncSessionLocal() as session:
        retrieval_service = RetrievalService(session)
        gateway = AIGateway()
        print("Starting Retrieval Validation\n" + "-"*50)
        
        for q in QUERIES:
            print(f"\nQuery: '{q}'")
            start = time.time()
            
            emb_start = time.time()
            embeddings = await gateway.embed_texts([q])
            embedding_latency_ms = int((time.time() - emb_start) * 1000)
            
            if not embeddings:
                print("  [!] Failed to generate embedding.")
                continue
                
            query_embedding = embeddings[0]
            
            results_obj = await retrieval_service.search(
                query=q,
                query_embedding=query_embedding,
                embedding_model="nomic-ai/nomic-embed-text-v1.5",
                embedding_latency_ms=embedding_latency_ms,
                top_k=3
            )
            results = results_obj.results
            latency = (time.time() - start) * 1000
            
            print(f"Top K: {len(results)}")
            print(f"Latency: {latency:.2f}ms")
            for idx, r in enumerate(results):
                doc_name = getattr(r, 'document_title', 'Unknown Document')
                print(f"  [{idx+1}] Similarity: {r.similarity_score:.4f} | Document: {doc_name}")
                print(f"      Chunk Snippet: {r.content[:100].encode('ascii', 'replace').decode()}...")
            
            if not results:
                print("  [!] No results found. Ensure knowledge base is populated and embedded.")

if __name__ == "__main__":
    asyncio.run(validate_retrieval())
