from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.client_detail import MatchUpdate
from app.schemas.match import GlobalMatchResponse
from app.services.match_service import MatchService


router = APIRouter()

@router.get("", response_model=list[GlobalMatchResponse])
async def get_matches(session: AsyncSession = Depends(get_db_session)):
    service = MatchService(session)
    return await service.get_all_matches()

@router.patch("/{match_id}", response_model=GlobalMatchResponse)
async def update_match(
    match_id: UUID,
    data: MatchUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> GlobalMatchResponse:
    service = MatchService(session)
    return await service.update_match_status(match_id, data.status)

@router.post("/{match_id}/explain")
async def explain_match(
    match_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    service = MatchService(session)
    return await service.explain_match(match_id)

