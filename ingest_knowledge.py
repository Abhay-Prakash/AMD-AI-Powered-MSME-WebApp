import asyncio
import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal
from app.services.knowledge_library_service import KnowledgeLibraryService

async def main():
    async with AsyncSessionLocal() as session:
        service = KnowledgeLibraryService(session)
        import os
        # Using environment variable or default relative path
        target_dir = os.getenv("KNOWLEDGE_DIR", "data/knowledge")
        print(f"Starting ingestion from: {target_dir}")
        await service.ingest_directory(target_dir)

if __name__ == "__main__":
    asyncio.run(main())
