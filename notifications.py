from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.notification import NotificationListResponse, NotificationResponse
from app.services.notification_service import NotificationService

router = APIRouter()

@router.get("", response_model=NotificationListResponse)
async def get_notifications(session: AsyncSession = Depends(get_db_session)):
    service = NotificationService(session)
    return await service.get_notifications()

@router.patch("/read-all")
async def mark_all_read(session: AsyncSession = Depends(get_db_session)):
    service = NotificationService(session)
    await service.mark_all_read()
    return {"status": "success"}

@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(notification_id: UUID, session: AsyncSession = Depends(get_db_session)):
    service = NotificationService(session)
    try:
        return await service.mark_as_read(notification_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
