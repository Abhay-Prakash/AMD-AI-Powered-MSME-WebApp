from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.document import DocumentResponse
from app.services.document_service import DocumentService

router = APIRouter()

@router.post("", response_model=DocumentResponse)
async def upload_document(
    client_id: UUID = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session)
):
    service = DocumentService(session)
    return await service.upload_document(client_id, file)

@router.get("/{client_id}", response_model=list[DocumentResponse])
async def list_documents(
    client_id: UUID,
    session: AsyncSession = Depends(get_db_session)
):
    service = DocumentService(session)
    return await service.list_documents(client_id)
