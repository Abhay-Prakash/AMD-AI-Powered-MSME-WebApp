from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.registration import RegistrationCreate, RegistrationResponse
from app.services.registration_service import RegistrationService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: RegistrationCreate,
    session: AsyncSession = Depends(get_db_session)
):
    service = RegistrationService(session)
    try:
        registration = await service.register(payload)
        return registration
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
