from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate
from app.schemas.client_detail import ClientDetailResponse, ClientMatchResponse, ClientDocumentResponse, ClientAuditResponse
from app.services.client_service import ClientService
from app.services.client_detail_service import ClientDetailService


router = APIRouter()


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
async def create_client(
    data: ClientCreate,
    user_id: UUID | None = Query(None, description="UUID of the current user"),
    session: AsyncSession = Depends(get_db_session),
) -> ClientRead:
    from app.services.ca_profile_service import CAProfileService
    ca_service = CAProfileService(session)
    if not user_id:
        from sqlalchemy import select
        from app.models.user import User
        res = await session.execute(select(User).where(User.email == "demo_ca@subsidydesk.com"))
        demo_user = res.scalar_one_or_none()
        if demo_user: user_id = demo_user.id
        
    ca_profile = await ca_service.get_ca_profile_by_user(user_id) if user_id else None
    if not ca_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CA Profile not found")
        
    service = ClientService(session, ca_profile.id)
    return await service.create_client(data)

from fastapi import UploadFile, File

@router.post("/bulk-import")
async def bulk_import(
    file: UploadFile = File(...),
    user_id: UUID = Query(..., description="UUID of the current user"),
    session: AsyncSession = Depends(get_db_session),
):
    from app.services.ca_profile_service import CAProfileService
    ca_service = CAProfileService(session)
    ca_profile = await ca_service.get_ca_profile_by_user(user_id)
    if not ca_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CA Profile not found")
        
    content = await file.read()
    service = ClientService(session, ca_profile.id)
    return await service.bulk_import(content.decode("utf-8"))



from app.schemas.client_portfolio import ClientPortfolioResponse
from app.services.client_portfolio_service import ClientPortfolioService

@router.get("", response_model=ClientPortfolioResponse)
async def list_clients(
    user_id: UUID | None = Query(None, description="UUID of the current user"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
) -> ClientPortfolioResponse:
    from app.services.ca_profile_service import CAProfileService
    ca_service = CAProfileService(session)
    
    if not user_id:
        from sqlalchemy import select
        from app.models.user import User
        stmt = select(User).where(User.email == "demo_ca@subsidydesk.com")
        res = await session.execute(stmt)
        demo_user = res.scalar_one_or_none()
        if demo_user:
            user_id = demo_user.id
            
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user_id")
        
    ca_profile = await ca_service.get_ca_profile_by_user(user_id)
    if not ca_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CA Profile not found")
        
    portfolio_service = ClientPortfolioService(session, ca_profile.id)
    return await portfolio_service.get_client_portfolio(skip=skip, limit=limit)


@router.get("/{client_id}", response_model=ClientDetailResponse)
async def get_client(
    client_id: UUID,
    user_id: UUID | None = Query(None, description="UUID of the current user"),
    session: AsyncSession = Depends(get_db_session),
) -> ClientDetailResponse:
    from app.services.ca_profile_service import CAProfileService
    ca_service = CAProfileService(session)
    if not user_id:
        from sqlalchemy import select
        from app.models.user import User
        res = await session.execute(select(User).where(User.email == "demo_ca@subsidydesk.com"))
        demo_user = res.scalar_one_or_none()
        if demo_user: user_id = demo_user.id
    ca_profile = await ca_service.get_ca_profile_by_user(user_id) if user_id else None
    if not ca_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CA Profile not found")
        
    service = ClientDetailService(session, ca_profile.id)
    client = await service.get_client_detail(client_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client

@router.get("/{client_id}/matches", response_model=list[ClientMatchResponse])
async def get_client_matches(
    client_id: UUID,
    user_id: UUID | None = Query(None, description="UUID of the current user"),
    session: AsyncSession = Depends(get_db_session),
) -> list[ClientMatchResponse]:
    from app.services.ca_profile_service import CAProfileService
    ca_service = CAProfileService(session)
    if not user_id:
        from sqlalchemy import select
        from app.models.user import User
        res = await session.execute(select(User).where(User.email == "demo_ca@subsidydesk.com"))
        demo_user = res.scalar_one_or_none()
        if demo_user: user_id = demo_user.id
    ca_profile = await ca_service.get_ca_profile_by_user(user_id) if user_id else None
    if not ca_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CA Profile not found")
        
    service = ClientDetailService(session, ca_profile.id)
    return await service.get_client_matches(client_id)

@router.get("/{client_id}/documents", response_model=list[ClientDocumentResponse])
async def get_client_documents(
    client_id: UUID,
    user_id: UUID | None = Query(None, description="UUID of the current user"),
    session: AsyncSession = Depends(get_db_session),
) -> list[ClientDocumentResponse]:
    from app.services.ca_profile_service import CAProfileService
    ca_service = CAProfileService(session)
    if not user_id:
        from sqlalchemy import select
        from app.models.user import User
        res = await session.execute(select(User).where(User.email == "demo_ca@subsidydesk.com"))
        demo_user = res.scalar_one_or_none()
        if demo_user: user_id = demo_user.id
    ca_profile = await ca_service.get_ca_profile_by_user(user_id) if user_id else None
    if not ca_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CA Profile not found")
        
    service = ClientDetailService(session, ca_profile.id)
    return await service.get_client_documents(client_id)

@router.get("/{client_id}/audit", response_model=list[ClientAuditResponse])
async def get_client_audit(
    client_id: UUID,
    user_id: UUID | None = Query(None, description="UUID of the current user"),
    session: AsyncSession = Depends(get_db_session),
) -> list[ClientAuditResponse]:
    from app.services.ca_profile_service import CAProfileService
    ca_service = CAProfileService(session)
    if not user_id:
        from sqlalchemy import select
        from app.models.user import User
        res = await session.execute(select(User).where(User.email == "demo_ca@subsidydesk.com"))
        demo_user = res.scalar_one_or_none()
        if demo_user: user_id = demo_user.id
    ca_profile = await ca_service.get_ca_profile_by_user(user_id) if user_id else None
    if not ca_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CA Profile not found")
        
    service = ClientDetailService(session, ca_profile.id)
    return await service.get_client_audit(client_id)


@router.patch("/{client_id}", response_model=ClientRead)
async def update_client(
    client_id: UUID,
    data: ClientUpdate,
    user_id: UUID | None = Query(None, description="UUID of the current user"),
    session: AsyncSession = Depends(get_db_session),
) -> ClientRead:
    from app.services.ca_profile_service import CAProfileService
    ca_service = CAProfileService(session)
    if not user_id:
        from sqlalchemy import select
        from app.models.user import User
        res = await session.execute(select(User).where(User.email == "demo_ca@subsidydesk.com"))
        demo_user = res.scalar_one_or_none()
        if demo_user: user_id = demo_user.id
        
    ca_profile = await ca_service.get_ca_profile_by_user(user_id) if user_id else None
    if not ca_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CA Profile not found")
        
    service = ClientService(session, ca_profile.id)
    client = await service.update_client(client_id, data)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: UUID,
    user_id: UUID | None = Query(None, description="UUID of the current user"),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    from app.services.ca_profile_service import CAProfileService
    ca_service = CAProfileService(session)
    if not user_id:
        from sqlalchemy import select
        from app.models.user import User
        res = await session.execute(select(User).where(User.email == "demo_ca@subsidydesk.com"))
        demo_user = res.scalar_one_or_none()
        if demo_user: user_id = demo_user.id
        
    ca_profile = await ca_service.get_ca_profile_by_user(user_id) if user_id else None
    if not ca_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CA Profile not found")
        
    service = ClientService(session, ca_profile.id)
    deleted = await service.delete_client(client_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
