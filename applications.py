from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from app.db.session import get_db_session
from app.schemas.application import ApplicationListResponse, ApplicationResponse, DraftResponse, ExportManifestResponse
from app.services.application_service import ApplicationService

router = APIRouter()

@router.get("", response_model=ApplicationListResponse)
async def get_applications(
    session: AsyncSession = Depends(get_db_session),
) -> ApplicationListResponse:
    service = ApplicationService(session)
    return await service.get_applications()

@router.post("/{id}/ready", response_model=ApplicationResponse)
async def mark_application_ready(id: UUID, session: AsyncSession = Depends(get_db_session)):
    service = ApplicationService(session)
    return await service.mark_application_ready(id)

@router.get("/{id}/draft", response_model=DraftResponse)
async def get_application_draft(id: UUID, session: AsyncSession = Depends(get_db_session)):
    service = ApplicationService(session)
    return await service.get_application_draft(id)

@router.post("/{id}/generate-draft")
async def generate_draft(id: UUID, session: AsyncSession = Depends(get_db_session)) -> dict:
    service = ApplicationService(session)
    return await service.generate_draft(id)

@router.post("/{id}/regenerate-draft")
async def regenerate_draft(id: UUID, session: AsyncSession = Depends(get_db_session)) -> dict:
    service = ApplicationService(session)
    return await service.generate_draft(id, force_regenerate=True)

@router.get("/{id}/export", response_model=ExportManifestResponse)
async def export_application_package(id: UUID, session: AsyncSession = Depends(get_db_session)):
    service = ApplicationService(session)
    return await service.export_application_package(id)

