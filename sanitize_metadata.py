import asyncio
import argparse
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models.knowledge import KnowledgeDocument, KnowledgeChunk
import os
import urllib.parse
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def sanitize_metadata(apply: bool = False, batch_size: int = 50):
    report = {
        "start_time": datetime.utcnow().isoformat(),
        "documents_processed": 0,
        "documents_modified": 0,
        "chunks_processed": 0,
        "chunks_modified": 0,
        "status": "dry-run" if not apply else "applied",
        "errors": []
    }
    
    logger.info(f"Starting sanitization sprint. Mode: {'APPLY' if apply else 'DRY-RUN'}")
    
    try:
        async with AsyncSessionLocal() as session:
            # Process Documents
            result = await session.execute(select(KnowledgeDocument))
            documents = result.scalars().all()
            
            for doc in documents:
                report["documents_processed"] += 1
                modified = False
                
                # Check source_url for local paths
                old_source_url = doc.source_url
                if old_source_url and ("D:\\" in old_source_url or "C:\\" in old_source_url or "/" in old_source_url):
                    filename = os.path.basename(old_source_url.replace("\\", "/"))
                    
                    if not doc.storage_uri:
                        doc.storage_uri = f"knowledge://internal/{urllib.parse.quote(filename)}"
                        modified = True
                    if not doc.display_name:
                        doc.display_name = doc.title or filename.replace("_", " ").replace(".pdf", "")
                        modified = True
                    if not doc.citation_label:
                        doc.citation_label = "Government Document"
                        modified = True
                    if not doc.source_agency:
                        doc.source_agency = doc.issuing_authority
                        modified = True
                    if not doc.source_origin:
                        doc.source_origin = "local_ingestion"
                        modified = True
                    
                    # Ensure display_url is null so the UI hides the link
                    doc.display_url = None
                    
                    # Redact the old source_url for security
                    doc.source_url = doc.storage_uri
                    modified = True
                
                if modified:
                    report["documents_modified"] += 1
                    logger.info(f"[DOC] Modifying {doc.id} - storage_uri: {doc.storage_uri}")
                    
            # Process Chunks in batches
            result_chunks = await session.execute(select(KnowledgeChunk))
            chunks = result_chunks.scalars().all()
            
            updates = []
            for chunk in chunks:
                report["chunks_processed"] += 1
                meta = chunk.metadata_.copy() if chunk.metadata_ else {}
                chunk_modified = False
                
                if "source_url" in meta and meta["source_url"] and ("D:\\" in meta["source_url"] or "C:\\" in meta["source_url"] or "/" in meta["source_url"]):
                    filename = os.path.basename(meta["source_url"].replace("\\", "/"))
                    storage_uri = f"knowledge://internal/{urllib.parse.quote(filename)}"
                    
                    # Update metadata but preserve existing keys
                    meta["source_url"] = storage_uri
                    meta["storage_uri"] = storage_uri
                    meta["display_name"] = meta.get("document_title", filename.replace(".pdf", ""))
                    meta["display_url"] = None
                    meta["citation_label"] = "Government Document"
                    
                    chunk.metadata_ = meta
                    chunk_modified = True
                
                if chunk_modified:
                    report["chunks_modified"] += 1
                    updates.append(chunk)
                    
            if apply:
                await session.commit()
                logger.info("Transaction committed successfully.")
            else:
                await session.rollback()
                logger.info("Dry-run complete. Transaction rolled back.")
                
    except Exception as e:
        report["errors"].append(str(e))
        logger.error(f"Error during sanitization: {e}")
        
    report["end_time"] = datetime.utcnow().isoformat()
    
    # Save report
    report_file = f"migration_report_{'apply' if apply else 'dry_run'}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    import json
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
        
    logger.info(f"Detailed migration report saved to {report_file}")
    logger.info(f"Summary: Docs Mod: {report['documents_modified']}/{report['documents_processed']} | Chunks Mod: {report['chunks_modified']}/{report['chunks_processed']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sanitize production metadata")
    parser.add_argument("--apply", action="store_true", help="Apply the changes transactionally")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size for processing")
    parser.add_argument("--yes", action="store_true", help="Bypass manual confirmation")
    args = parser.parse_args()
    
    # Confirm rollback/backup
    if args.apply and not args.yes:
        confirm = input("WARNING: Have you ensured the database is backed up? This will mutate records. Type 'yes' to proceed: ")
        if confirm.lower() != 'yes':
            print("Aborting.")
            exit(1)
            
    asyncio.run(sanitize_metadata(apply=args.apply, batch_size=args.batch_size))
